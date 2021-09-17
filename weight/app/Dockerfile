
FROM python:3.8
# CMD tail -f /dev/null

RUN apt-get update -y && apt-get install -y python3-pip python-dev
#RUN pip3 install flask

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt


COPY . .


ENTRYPOINT [ "python3" ]
CMD [ "rest.py" ]
