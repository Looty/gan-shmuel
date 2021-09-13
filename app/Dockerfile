FROM python:3.5-alpine3.10 

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
VOLUME /provider.json:/provider.json

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
