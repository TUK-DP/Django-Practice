FROM twoone14/dp-base-image:latest

RUN apt-get install dos2unix -y

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY ./docker-entrypoint.sh /app/docker-entrypoint.sh

RUN chmod +x docker-entrypoint.sh
RUN dos2unix docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]