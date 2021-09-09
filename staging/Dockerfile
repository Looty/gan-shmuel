FROM python:rc-alpine3.14
RUN pip3 install Flask
COPY . .
RUN apk add --update docker openrc
RUN apk add docker docker-compose
RUN rc-update add docker boot
EXPOSE 8080
ENTRYPOINT ["python3" , "./ci.py"]
