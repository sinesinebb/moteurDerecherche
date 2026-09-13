# docker/zookeeper/Dockerfile
FROM wurstmeister/zookeeper:3.4.14
USER root
RUN apt-get update && apt-get install -y netcat && rm -rf /var/lib/apt/lists/*
USER zookeeper

