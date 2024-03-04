FROM twoone14/dp-base-image:0.2

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT ["python3", "manage.py", "runserver", "0.0.0.0:8000"]