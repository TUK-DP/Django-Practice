FROM twoone14/dp-base-image:latest

RUN apt-get install dos2unix -y

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt