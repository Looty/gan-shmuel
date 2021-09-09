FROM python:rc-alpine3.14
RUN pip3 install Flask
COPY . .
EXPOSE 8080
ENTRYPOINT ["python3" , "./ci.py"]
