# 项目背景
本人常用的机场为了订阅安全，限制每天订阅次数，一旦超过则会重置订阅链接。本项目是为了解决无意识地超过次数限制，避免陷入订阅失效焦虑。

*PS: 我用的客户端是 OpenClash，虽然设置每天更新，但是上面会显示套餐余额，每次点击查看套餐余额相当于就订阅了一次*

[机场推荐](https://invite.wgetcloud.ltd/auth/register?code=t7jm)

# 实现功能

统一管理订阅，定时下载并存储订阅信息，自动进行订阅转换，并提供代理服务。

*PS: 目前自动订阅转换只支持 clash -> surge, clash -> sufboard，因为我只用到这些，其他没条件测试 (●'◡'●)*

# 快速开始
使用 `pip` 安装：
```shell
$ pip install subscribe-manager
```

添加配置文件 `config.yaml`，格式如下：

```yaml
services:
  <your_service_name>:
    sensitive_policy:
      - check_type: "<check_type>"
        keyword: "<keyword>"
    target_type: "<target_type>"
    auto_transform: "true"
    urls:
      - uuid: "<your_unique_identifier1>"
        url: "<your_original_subscribe_link1>"
      - uuid: "<your_unique_identifier2>"
        url: "<your_original_subscribe_link2>"
      - uuid: "..."
        url: "..."
```

配置文件定义说明：

- `services` : 订阅设置的顶层
- `<your_servie_name>` : 服务名称，为方便区分，可以按照机场名来填写
- `sensitive_policy` : 敏感策略，考虑到原始订阅内容会包含一些敏感信息，可以设置一些检查策略，进行删除
- `check_type` : 目前只开放 `start`，删除指定关键字开头的行
- `keyword` : 关键字，配合 `check_type` 使用
- `target_type`：订阅类型，目前只支持 clash, sufboard, surge
- auto_transform: 自动订阅转换，目前只支持 clash -> surfboard, clash -> surge
- `urls` : 设置订阅信息
  - `uuid`：唯一标识，在下载订阅文件保存时，文件名依此生成
  - `url` ：订阅的原始环境



例子：

添加 `example.py` : 

```python
from subscribe_manager import SubscribeManager

sm = SubscribeManager()
sm.start()
```
与 `example.py` 同一目录下， 添加配置文件 `config.yaml`
```yaml
services:
  myService:
    target_type: "clash"
    auto_transform: "true"
    urls:
      - uuid: "aaa"
        url: "https://example.com/link/abcdefg"
      - uuid: "bbb"
        url: "https://example.com/link/hijklmn"
```

执行后，看到以下目录结构

```cmd
|   config.yaml
|   example.py
|   subscribe_manager.db
|
\---subscribe
    \---myService
            aaa_clash.yaml
            aaa_surfboard.conf
            aaa_surge.conf
            bbb_clash.yaml
            bbb_surfboard.conf
            bbb_surge.conf
```

数据库 `subscribe_manager.db` 默认生成在同一目录，存放文件路径，订阅url，订阅信息，订阅文件存放在对应服务名称的文件夹下。

接口服务默认发布在 `http://127.0.0.1:8000`，以 `get` 方法调用 `http://127.0.0.1:8000/link/<service_name>/<uuid>?target=<target_type>`，`?target=<target_type>`未指定时，默认为 `clash`。

以本例来说:

| 请求地址                                              | 结果                                       |
| ----------------------------------------------------- | ------------------------------------------ |
| http://127.0.0.1:8000/link/myService/aaa              | 未指定target，默认返回 aaa_clash.yaml 内容 |
| http://127.0.0.1:8000/link/myService/aaa?target=surge | 返回 aaa_surge.conf 内容                   |

SubscribeManager 参数说明：

| 参数名称            | 参数说明                           | 默认值               |
| ------------------- | ---------------------------------- | -------------------- |
| max_subscribe_count | 最大订阅次数                       | 5                    |
| config_file         | 配置文件路径                       | config.yaml          |
| subscribe_save_path | 订阅内容本地保存路径               | subscribe            |
| refresh_flag        | 是否刷新，服务启动时，是否下载订阅 | True                 |
| interval_type       | 间隔类型                           | days                 |
| interval            | 间隔时长                           | 1                    |
| start_date          | 定时开始时间                       | 2000-01-01 00:00:00  |
| host                | host                               | 127.0.0.1            |
| port                | port                               | 8000                 |
| db_name             | 数据库名称                         | subscribe_manager.db |

你也可以直接通过命令行的形式直接运行，与上面不同的是，在 `config.yaml` 中需要额外增加 `settings`，如果缺失 `settings`，程序会根据默认值执行

```yaml
settings:
  max_subscribe_count: <your_max_subscribe_count>
  subscribe_save_path: "<your_subscribe_save_path>"
  refresh_flag: "<your_refresh_flag>"
  interval_type: "<your_interval_type>"
  interval: <your_interval>
  start_date: "<your_start_date>"
  host: "<your_host>"
  port: <your_port>
  db_name: "<your_db_name>"

services:
  <your_service_name>:
    sensitive_policy:
      - check_type: "<check_type>"
        keyword: "<keyword>"
    target_type: "<target_type>"
    auto_transform: "true"
    urls:
      - uuid: "<your_unique_identifier1>"
        url: "<your_original_subscribe_link1>"
      - uuid: "<your_unique_identifier2>"
        url: "<your_original_subscribe_link2>"
      - uuid: "..."
        url: "..."
```

运行命令：

```shell
$  sbscmgr --config_file <your_config_file>
```

如果未指定 `--config_file`，直接运行，则默认为当前目录的  `config.yaml`

