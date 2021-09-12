FROM python:rc-alpine3.14
RUN pip3 install Flask
COPY . .
RUN apk add --update docker openrc
RUN apk add docker docker-compose
RUN rc-update add docker boot
RUN apk update && \
    apk upgrade && \
    apk add git
RUN pip install Flask-APScheduler
RUN pip install Flask-Mail
RUN git clone https://github.com/Looty/gan-shmuel.git
EXPOSE 8080
ENTRYPOINT ["python3" , "./ci.py"]
