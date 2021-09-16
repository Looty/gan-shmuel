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
# >
RUN apk add --update openssh
RUN mkdir /.ssh
#COPY /home/ec2-user/.ssh/aws_github.pub /.ssh/
#RUN ssh-add /.ssh/aws_github.pub
# <
#RUN git clone https://github.com/Looty/gan-shmuel.git
#RUN git clone git@github.com:Looty/gan-shmuel.git
#COPY . .
#EXPOSE 8080
#ENTRYPOINT ["python3" , "./ci.py"]
