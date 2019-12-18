# docker 集群 demo

### 1. build mysql

```shell
cd machine_dockerfiles

# 主库 (写库)
docker build -t mysql:v1 --file mysql.Dockerfile .

# 从库 (读库)
docker build -t mysql_slave:v1 --file mysql_slave.Dockerfile .
```

- 主库设置

```
vim /etc/mysql/mysql.conf.d/mysql.conf

[mysqld]
server-id=101
bin-log=mysql-bin

# 设置从库用户 repl, host: %, pwd: 123456
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%' identified by '123456';

# 使用maxscale
grant replication client on *.* to 'maxscale'@'%' identified by '123456';

show master status;
```

- 从库设置

```
vim /etc/mysql/mysql.conf.d/mysql.conf

[mysqld]
server-id=101


# 设置主库数据, 使用用户 repl 连接，密码：123456
CHANGE MASTER TO
MASTER_HOST='172.17.0.3',
MASTER_USER='repl',
MASTER_PASSWORD='123456',
MASTER_LOG_FILE='mysql-bin.000001',
MASTER_LOG_POS=154;


grant replication client on *.* to 'maxscale'@'%' identified by '123456';


start slave;
show slave status\G
```


### 2. build maxscale

```shell
cd machine_dockerfiles

docker build -t maxscale:v1 --file maxscale.Dockerfile . 
```

```sql
grant replication client on *.* to 'maxscale'@'%' identified by '123456';
```