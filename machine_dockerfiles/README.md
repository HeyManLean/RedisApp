# docker 集群 demo

### 1. build mysql

```shell
cd machine_dockerfiles

# 主库 (写库)
docker build -t mysql:v1 --file mysql.Dockerfile .

# 从库 (读库)
docker build -t mysql_slave:v1 --file mysql_slave.Dockerfile .
```


### 2. build maxscale

```shell
cd machine_dockerfiles

docker build -t maxscale:v1 --file maxscale.Dockerfile . 
```

```sql
grant replication client on *.* to 'maxscale'@'%' identified by '123456';
```