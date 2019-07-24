# 处理列表

### 1. db 处理

- [x] model 操作
- [x] 多数据库映射处理
- [x] redis，mongo，mysql
- [ ] flask_sqlalchemy, 多库切换

### 2. request 处理

- [x] 解析参数
- [x] 获取必要参数，ip 等

### 3. response 处理

- [x] 响应码定义
- [x] 响应内容及 cookie 处理

### 4. config 配置

- [x] logging 配置
- [x] 数据库配置
- [ ] celery 配置
- [ ] 不同开发环境下的配置继承

### 5. 额外辅助 web 工具

- cors: 跨域访问
- csrf: 跨站攻击
- limiter: 限制访问频率
- sqlalchemy: mysql orm，读写分离等
- flask_script: Manager 调用
- celery: 异步队列，多项目调用
- sentry: 服务器异常
- gunicorn: 服务器
- supervisor: 进程管理
- nginx: 开启 web 服务
- makefile: 部署脚本
- itsdangerous: 多服务器访问加密

### 6. 结构代码优化

- 使用 blinker 解耦，跨模块操作的，避免循环引用等
- 使用 redis 实现 cache 缓存

