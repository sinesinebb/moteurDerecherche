from builtins import object
from collections import OrderedDict
import logging
import sys
import datetime
import os
import errno
import copy



# Remplacement de pythonjsonlogger et cloghandler par du stdlib
from logging.handlers import RotatingFileHandler

class LogFactory(object):
    _instance = None

    @classmethod
    def get_instance(cls, **kwargs):
        if cls._instance is None:
            cls._instance = LogObject(**kwargs)
        return cls._instance

class LogCallbackHandler:
    def __init__(self, logger):
        self.logger = logger
        self.callbacks = OrderedDict([
            ("DEBUG", []),
            ("INFO", []),
            ("WARNING", []),
            ("ERROR", []),
            ("CRITICAL", []),
        ])

    def parse_log_level(self, log_level):
        MIN_LOG_LEVEL = self.logger.level_dict['DEBUG']
        MAX_LOG_LEVEL = self.logger.level_dict['CRITICAL']
        chrs = log_level[:2]
        if chrs == '<=':
            lvl = log_level[2:]
            hi = self.logger.level_dict[lvl]
            r = range(MIN_LOG_LEVEL, hi+1)
        elif chrs.startswith('<'):
            lvl = log_level[1:]
            hi = self.logger.level_dict[lvl]
            r = range(MIN_LOG_LEVEL, hi)
        elif chrs == '>=':
            lvl = log_level[2:]
            lo = self.logger.level_dict[lvl]
            r = range(lo, MAX_LOG_LEVEL+1)
        elif chrs.startswith('>'):
            lvl = log_level[1:]
            lo = self.logger.level_dict[lvl]
            r = range(lo+1, MAX_LOG_LEVEL+1)
        elif chrs.startswith('='):
            lvl = log_level[1:]
            num = self.logger.level_dict[lvl]
            r = range(num, num+1)
        elif chrs == '*':
            r = range(MIN_LOG_LEVEL, MAX_LOG_LEVEL+1)
        else:
            num = self.logger.level_dict[log_level]
            r = range(num, num+1)
        return list(r)

    def is_subdict(self, a, b):
        return all((k in b and b[k]==v) for k,v in a.items())

    def register_callback(self, log_level, fn, criteria=None):
        criteria = criteria or {}
        num_to_level = {v: k for k, v in self.logger.level_dict.items()}
        num_to_level[2] = "WARNING"
        for n in self.parse_log_level(log_level):
            lvl = num_to_level[n]
            self.callbacks[lvl].append((fn, criteria))

    def fire_callbacks(self, log_level, log_message=None, log_extra=None):
        log_extra = log_extra or {}
        for cb, crit in self.callbacks[log_level]:
            if crit and not self.is_subdict(crit, log_extra):
                continue
            cb(log_message, log_extra)

class LogObject(object):
    level_dict = {
        "DEBUG": 0, "INFO": 1, "WARN": 2, "WARNING": 2,
        "ERROR": 3, "CRITICAL": 4,
    }

    def __init__(self, json=False, stdout=True, name='scrapy-cluster',
                 dir='logs', file='main.log', bytes=25_000_000, backups=5,
                 level='INFO',
                 format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
                 propagate=False, include_extra=False):

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = propagate
        self.json = json
        self.log_level = level
        self.format_string = format
        self.include_extra = include_extra
        self.cb_handler = LogCallbackHandler(self)

        formatter = logging.Formatter(self.format_string)

        if stdout:
            sh = logging.StreamHandler(sys.stdout)
            sh.setLevel(logging.DEBUG)
            sh.setFormatter(formatter)
            self.logger.addHandler(sh)
            self._check_log_level(level)
            self.debug("Logging to stdout")
        else:
            os.makedirs(dir, exist_ok=True)
            fh = RotatingFileHandler(
                os.path.join(dir, file),
                maxBytes=bytes,
                backupCount=backups
            )
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
            self._check_log_level(level)
            self.debug(f"Logging to file: {dir}/{file}")

    def _check_log_level(self, level):
        if level not in self.level_dict:
            self.log_level = 'DEBUG'
            self.logger.warning(
                f"Unknown log level '{level}', defaulting to DEBUG"
            )

    def debug(self, message, extra={}):
        if self.level_dict['DEBUG'] >= self.level_dict[self.log_level]:
            e = self.add_extras(extra, "DEBUG")
            self.logger.debug(message)  # no JSON mode here
            self.cb_handler.fire_callbacks('DEBUG', message, e)

    def info(self, message, extra={}):
        if self.level_dict['INFO'] >= self.level_dict[self.log_level]:
            e = self.add_extras(extra, "INFO")
            self.logger.info(message)
            self.cb_handler.fire_callbacks('INFO', message, e)

    def warning(self, message, extra={}):
        if self.level_dict['WARNING'] >= self.level_dict[self.log_level]:
            e = self.add_extras(extra, "WARNING")
            self.logger.warning(message)
            self.cb_handler.fire_callbacks('WARNING', message, e)

    def error(self, message, extra={}):
        if self.level_dict['ERROR'] >= self.level_dict[self.log_level]:
            e = self.add_extras(extra, "ERROR")
            self.logger.error(message)
            self.cb_handler.fire_callbacks('ERROR', message, e)

    def critical(self, message, extra={}):
        if self.level_dict['CRITICAL'] >= self.level_dict[self.log_level]:
            e = self.add_extras(extra, "CRITICAL")
            self.logger.critical(message)
            self.cb_handler.fire_callbacks('CRITICAL', message, e)

    @property
    def name(self):
        return self.logger.name

    def add_extras(self, d, level):
        copy_d = copy.deepcopy(d)
        copy_d.setdefault('level', level)
        copy_d.setdefault('timestamp', self._get_time())
        copy_d.setdefault('logger', self.name)
        return copy_d

    def _get_time(self):
        return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    def register_callback(self, log_level, fn, criteria=None):
        return self.cb_handler.register_callback(log_level, fn, criteria)
