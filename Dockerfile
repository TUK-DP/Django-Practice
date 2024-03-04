# using local image
FROM ubuntu:latest

RUN apt-get update
# Install python
RUN apt-get install -y python3.9 python3-pip

# Install java-11
RUN apt-get install -y openjdk-11-jdk

# Install git
RUN apt-get install -y git
# git clone py-hanspell
RUN git clone https://github.com/ssut/py-hanspell.git /app/py-hanspell

RUN cd /app/py-hanspell && python3 setup.py install

# Install tzdata
RUN apt-get install -y tzdata

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT ["python3", "manage.py", "runserver", "0.0.0.0:8000"]