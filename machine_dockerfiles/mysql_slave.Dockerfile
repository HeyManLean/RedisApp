FROM ubuntu:18.04

COPY sources.list /etc/apt/sources.list

RUN apt-get update &&\
    apt-get install vim -y  &&\
    apt-get install net-tools -y &&\
    apt-get install inetutils-ping -y &&\
    apt-get install mysql-server -y &&\
    apt-get install mysql-client -y &&\
    apt-get install libmysqlclient-dev -y

RUN chmod -R 755 /var/lib/mysql && \
    chmod -R 777 /var/run/mysqld && \
    service mysql restart &&\
    mysql < mysql_slave.sql

EXPOSE 3306

CMD ["/bin/bash"]
