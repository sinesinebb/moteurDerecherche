FROM python:3.6

# os setup
RUN apt-get update
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# install requirements
COPY utils /usr/src/utils
COPY redis-monitor/requirements.txt /usr/src/app/
RUN pip --default-timeout=100 install --no-cache-dir -r requirements.txt
RUN rm -rf /usr/src/utils

# move codebase over
COPY redis-monitor /usr/src/app

# override settings via localsettings.py
COPY docker/redis-monitor/settings.py /usr/src/app/localsettings.py

# copy testing script into container
COPY docker/run_docker_tests.sh /usr/src/app/run_docker_tests.sh

# set up environment variables

# run command
CMD ["python", "redis_monitor.py"]