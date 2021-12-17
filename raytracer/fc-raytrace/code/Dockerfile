FROM python:3.9.0-slim
RUN apt-get update
RUN apt-get -y install g++ libc-dev
RUN pip install flask
RUN pip install gunicorn
WORKDIR code/
COPY . . 
RUN g++ smallpt.cpp -o smallpt
ENTRYPOINT gunicorn -c gunicorn_conf.py server:app
EXPOSE 9000