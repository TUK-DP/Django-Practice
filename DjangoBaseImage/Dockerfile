# using local image
FROM ubuntu:latest

RUN apt-get update
# Install python
RUN apt-get install -y python3.9 python3-pip && \
    pip3 install --upgrade pip

# Install java-11
RUN apt-get install -y openjdk-11-jdk

# TimeZone setting to Asia/Seoul
ENV TZ=Asia/Seoul
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime &&  \
    echo $TZ > /etc/timezone