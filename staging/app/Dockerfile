FROM ubuntu:20.04


CMD tail -f /dev/null

COPY . /app
WORKDIR /app
RUN apt-get update -y && apt-get install -y python3-pip python-dev
#RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev
#RUN pip3 install flask

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt


#COPY . .
COPY app.py /app

ENTRYPOINT [ "python3" ]
CMD [ "rest.py" ]
##