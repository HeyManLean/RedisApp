FROM ubuntu

COPY sources.list /etc/apt/sources.list

RUN apt-get update &&\
    apt-get install vim -y  &&\
    apt-get install mysql-server -y &&\
    apt-get install mysql-client -y &&\
    apt-get install libmysqlclient-dev -y

RUN chmod -R 755 /var/lib/mysql && \
    chmod -R 777 /var/run/mysqld && \
    service mysql restart

EXPOSE 3306

CMD ["/bin/bash"]

# pkill -9 mysqld
# chmod -R 777 /var/run/mysqld
# chmod -R 755 /var/lib/mysql
# service mysql restart