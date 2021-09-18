FROM python:rc-alpine3.14
RUN pip3 install Flask
RUN apk add --update docker openrc
RUN apk add docker docker-compose
RUN rc-update add docker boot
RUN apk update && \
    apk upgrade && \
    apk add git
RUN pip3 install Flask-APScheduler
RUN pip3 install Flask-Mail
RUN pip3 install secure-smtplib
ARG KEY
ENV KEY ${KEY}
RUN git clone https://${KEY}@github.com/Looty/gan-shmuel
COPY . .
EXPOSE 8080
ENTRYPOINT ["python3" , "./ci.py"]