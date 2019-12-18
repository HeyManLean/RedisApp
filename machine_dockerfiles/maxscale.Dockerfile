FROM ubuntu:18.04

COPY sources.list /etc/apt/sources.list
COPY vendors/maxscale-2.4.4-1.ubuntu.bionic.x86_64.deb /data/maxscale.deb

WORKDIR /data

RUN apt-get update &&\
    apt-get install sudo -y  &&\
    apt-get install vim net-tools inetutils-ping -y &&\
    apt-get install libcurl4 libedit2 -y

RUN dpkg -i maxscale.deb

CMD [ "/bin/bash" ]


# docker build -t maxscale:v1 --file machine_dockerfiles/maxscale.Dockerfile . 