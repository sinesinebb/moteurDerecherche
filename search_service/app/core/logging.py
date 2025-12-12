# app/core/logging.py
import logging
import sys
import json
import time
from pythonjsonlogger import jsonlogger
from typing import Dict, Any, Optional
from core.config import settings
import structlog
from opentelemetry import trace

class StructuredLogger:
    """Logger structuré avancé avec OpenTelemetry"""
    
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
        self._configure_structlog()
    
    def _configure_structlog(self):
        """Configure structlog pour le logging structuré"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                self._add_trace_info,
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    def _add_trace_info(self, logger, method_name, event_dict):
        """Ajoute les informations de tracing OpenTelemetry"""
        span = trace.get_current_span()
        if span.is_recording():
            span_context = span.get_span_context()
            event_dict['trace_id'] = format(span_context.trace_id, '032x')
            event_dict['span_id'] = format(span_context.span_id, '016x')
            event_dict['trace_flags'] = str(span_context.trace_flags)
        return event_dict

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Formateur JSON personnalisé avec métadonnées enrichies"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        super().add_fields(log_record, record, message_dict)
        
        # Métadonnées standardisées
        log_record['service'] = 'search-service'
        log_record['environment'] = settings.ENVIRONMENT
        log_record['timestamp'] = self._format_time(record.created)
        log_record['level'] = record.levelname
        
        # Informations de contexte
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line_number'] = record.lineno
        
        # Supprimer les champs redondants
        log_record.pop('name', None)
        log_record.pop('filename', None)
    
    def _format_time(self, timestamp: float) -> str:
        """Formate le timestamp en ISO 8601"""
        return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(timestamp))

class RequestContextFilter(logging.Filter):
    """Filtre pour ajouter le contexte de requête aux logs"""
    
    def __init__(self):
        super().__init__()
        self.context = {}
    
    def filter(self, record):
        for key, value in self.context.items():
            setattr(record, key, value)
        return True
    
    def set_context(self, **kwargs):
        """Définit le contexte de la requête"""
        self.context.clear()
        self.context.update(kwargs)

def setup_logging():
    """Configuration complète du logging"""
    
    # Niveau de log
    log_level = settings.get_log_level()
    
    # Configuration de base
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[],
        force=True
    )
    
    # Handler console avec format JSON
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(service)s %(module)s %(function)s %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Handler fichier pour production
    if settings.is_production():
        file_handler = logging.FileHandler('/var/log/search-service.json.log')
        file_handler.setFormatter(formatter)
    
    # Handler errors séparé
    error_handler = logging.FileHandler('/var/log/search-service.error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Configurer le logger racine
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(console_handler)
    
    if settings.is_production():
        root_logger.addHandler(file_handler)
    
    root_logger.addHandler(error_handler)
    
    # Ajouter le filtre de contexte
    context_filter = RequestContextFilter()
    root_logger.addFilter(context_filter)
    
    # Réduire le bruit des bibliothèques
    logging.getLogger("elasticsearch").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("kafka").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Configurer structlog
    structured_logger = StructuredLogger()
    
    root_logger.setLevel(log_level)
    
    return context_filter

def get_logger(name: str) -> structlog.BoundLogger:
    """Retourne un logger structlog configuré"""
    return structlog.get_logger(name)

# Configuration initiale
context_filter = setup_logging()
logger = get_logger(__name__)

class LogContext:
    """Context manager pour le logging avec contexte riche"""
    
    def __init__(self, **context):
        self.context = context
        self.logger = get_logger(__name__)
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        # Mettre à jour le contexte global
        context_filter.set_context(**self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.context['duration'] = duration
        
        if exc_type:
            self.logger.error(
                "Context execution failed",
                exc_info=True,
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                **self.context
            )
        else:
            self.logger.info(
                "Context execution completed",
                **self.context
            )
    
    def log(self, level: str, message: str, **extra):
        """Log un message avec le contexte enrichi"""
        log_context = {**self.context, **extra}
        getattr(self.logger, level.lower())(message, **log_context)

def log_execution_time(extra_context: dict = None):
    """
    Décorateur avancé pour logger le temps d'exécution avec contexte
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            func_name = func.__name__
            context = extra_context or {}
            context.update({
                'function': func_name,
                'type': 'performance'
            })
            
            with LogContext(**context) as log_ctx:
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    log_ctx.log('error', f"Function {func_name} failed")
                    raise
                finally:
                    duration = time.time() - start_time
                    log_ctx.log('info', 
                        f"Function {func_name} executed",
                        duration_seconds=duration,
                        performance_metric=True
                    )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            func_name = func.__name__
            context = extra_context or {}
            context.update({
                'function': func_name,
                'type': 'performance'
            })
            
            with LogContext(**context) as log_ctx:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    log_ctx.log('error', f"Function {func_name} failed")
                    raise
                finally:
                    duration = time.time() - start_time
                    log_ctx.log('info', 
                        f"Function {func_name} executed",
                        duration_seconds=duration,
                        performance_metric=True
                    )
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator