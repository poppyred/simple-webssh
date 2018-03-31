## simple-webssh接口文档

### webssh模块
#### webssh连接主机接口
- 协议 ```POST```
- URL ```/webssh/connection```
##### 参数列表

- ```hostname```，str，必传，需要连接的主机地址
- ```port```, int，必传，连接主机的端口号
- ```username```，str，必传，连接的用户名
- ```password```，str，非必传，连接需要的密码
- ```private_key```，str，非必传，连接需要的公钥，password和private_key二选一

##### 返回结果
```
{
    "code": 0,
    "msg": "success",
    "data": {
        "token": "4343354354354"
    }
}

```
注：pub_key是否以文件的形式传送更合适？

#### webssh websocket会话接口
- 协议 ```ws```
- URL ```/webssh/session```
##### 参数列表

- ```token```，str,必传，连接主机接口返回的token值

注：```xterm```，终端类型，这里默认用的xterm

### ping模块
#### ping主机接口
- 协议 ```POST,GET```
- URL ```/measure/ping```
##### 参数列表

- ```hostname```，str，必传，需要ping的主机地址
- ```count```, int, 非必传，ping的次数默认3次
- ```timeout```, int, 非必传，ping的超时时间，单位秒，默认1秒

##### 返回结果
```
{
    "code": 0,
    "msg": "success",
    "data": {
        "max_rtt":"6.736", 
        "min_rtt":"6.736, 
        "avg_rtt":"6.736,
        "packet_lost":0,
        "dst_ip":"127.0.0.1"
        "output":[...]
    }
}
```

### telnet模块
#### telnet主机端口接口
- 协议 ```POST,GET```
- URL ```/measure/telnet```
##### 参数列表

- ```hostname```，str，必传，需要telnet的主机地址
- ```port```, int, 必传，需要telnet的端口号
- ```timeout```, int, 非必传，telnet的超时时间，单位秒，默认1秒

##### 返回结果
```
{
    "code": 0,
    "msg": "success",
    "data": {
    }
}
```
