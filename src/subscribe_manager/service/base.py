import os
from typing import List, Optional

import yaml
from pydantic import BaseModel
from subscribe_manager.constant import BASE_DIR
from subscribe_manager.common.log_util import get_logger

logger = get_logger(__name__)


class Proxy(BaseModel):
    """
    代理服务器设置
    """

    name: str
    type: str
    server: Optional[str] = None
    port: Optional[int] = None
    password: Optional[str] = None
    sni: Optional[str] = None
    skip_cert_verify: Optional[bool] = None

    def display(self, target_type: str) -> str:
        if target_type in ["surge", "surfboard"]:
            return (
                f"{self.name} = {self.type}, {self.server}, {self.port}, "
                f"{'encrypt-method=aes-128-gcm, ' if target_type == 'surfboard' else ''}"
                f"password={self.password}, sni={self.sni}, "
                f"skip-cert-verify={'true' if self.skip_cert_verify else 'false'}"
            )
        else:
            raise ValueError(f"{target_type} is not supported")


class ProxyGroup(BaseModel):
    """
    代理组设置
    """

    name: str
    type: str
    proxys: List[Proxy]

    def display(self, target_type: str) -> str:
        if target_type in ["surge", "surfboard"]:
            return f"{self.name} = {self.type}, {', '.join(proxy.name for proxy in self.proxys)}"
        else:
            raise ValueError(f"{target_type} is not supported")


class Rule(BaseModel):
    type: str
    value: Optional[str] = None
    proxy_group: ProxyGroup
    tag: Optional[str] = None

    def display(self, target_type: str) -> str:
        if target_type in ["surge", "surfboard"]:
            return ",".join(
                item if item != "MATCH" else "FINAL"
                for item in [self.type, self.value, self.proxy_group.name, self.tag]
                if item
            )
        else:
            raise ValueError(f"{target_type} is not supported")


class SubscribeConfig(BaseModel):
    """
    订阅设置
    """

    sub_type: str
    begin_comment: str
    proxys: List[Proxy]
    proxy_groups: List[ProxyGroup]
    rules: List[Rule]

    def subscribe_transform(self, target_type: str) -> str:
        subscribe_content = ""
        template_path = os.path.join(BASE_DIR, "static", "template", target_type + ".template")
        if target_type in ["surge", "surfboard"]:
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()

            subscribe_content += "\n" + "[Proxy]"
            for proxy in self.proxys:
                if proxy.type not in ["INTERNAL", "PROXY_GROUP"]:
                    subscribe_content += "\n" + proxy.display(target_type)

            subscribe_content += "\n" + "\n" + "[Proxy Group]"
            for proxy_group in self.proxy_groups:
                if proxy_group.type not in ["INTERNAL"]:
                    subscribe_content += "\n" + proxy_group.display(target_type)
            subscribe_content += "\n" + "\n" + "[Rule]"
            for rule in self.rules:
                subscribe_content += "\n" + rule.display(target_type)
            return template.replace("{BEGIN_COMMENT}", self.begin_comment).replace("{CONTENT}", subscribe_content)
        else:
            raise ValueError(f"target_type {target_type} is not supported")


def load_subscribe_config(subscribe_name: str, target: str) -> SubscribeConfig:
    with open(subscribe_name, "r", encoding="utf-8") as file:
        subscribe_config_str = file.read()
    # 提取备注内容
    begin_comment = "\n".join(line for line in subscribe_config_str.splitlines() if line.startswith("#"))
    subscribe_content = yaml.safe_load(subscribe_config_str)

    proxys = []
    for proxy_dict in subscribe_content["proxies"]:
        name = proxy_dict["name"]
        proxy_type = proxy_dict["type"]
        server = proxy_dict["server"]
        port = proxy_dict["port"]
        password = proxy_dict["password"]
        sni = proxy_dict["sni"]
        skip_cert_verify = proxy_dict["skip-cert-verify"]
        proxy = Proxy(
            name=name,
            type=proxy_type,
            server=server,
            port=port,
            password=password,
            sni=sni,
            skip_cert_verify=skip_cert_verify,
        )
        proxys.append(proxy)
    # 添加固定
    proxys.append(Proxy(name="DIRECT", type="INTERNAL"))
    proxys_map = {proxy.name: proxy for proxy in proxys}

    proxy_groups: List[ProxyGroup] = []
    proxy_group: ProxyGroup
    for proxy_group_dict in subscribe_content["proxy-groups"]:
        proxy_names = proxy_group_dict["proxies"]
        group_proxys = [item for name in proxy_names if (item := proxys_map.get(name)) is not None]

        proxy_group_name = proxy_group_dict["name"]
        proxy_group_type = proxy_group_dict["type"]
        proxy_group = ProxyGroup(name=proxy_group_name, type=proxy_group_type, proxys=group_proxys)
        # 代理组也默认为一个代理，因为代理组可能包含代理组
        proxy = Proxy(name=proxy_group_name, type="PROXY_GROUP")
        proxys.append(proxy)
        proxys_map[proxy_group_name] = proxy

        proxy_groups.append(proxy_group)

    # REJECT
    proxy_group = ProxyGroup(name="REJECT", type="INTERNAL", proxys=[])
    proxy_groups.append(proxy_group)

    proxy_groups_map = {proxy_group.name: proxy_group for proxy_group in proxy_groups}

    rules: List[Rule] = []
    rule: Rule
    for rule_str in subscribe_content["rules"]:
        items: List[str] = rule_str.split(",")
        if len(items) <= 2:
            rule_type = items[0].strip()
            proxy_group_name = items[1].strip()
            try:
                proxy_group = proxy_groups_map[proxy_group_name]
            except KeyError:
                logger.error(f"Proxy group '{proxy_group_name}' not found")
                continue
            rule = Rule(type=rule_type, proxy_group=proxy_group)
        elif len(items) == 3:
            rule_type = items[0].strip()
            value = items[1].strip()
            proxy_group_name = items[2].strip()
            try:
                proxy_group = proxy_groups_map[proxy_group_name]
            except KeyError:
                logger.error(f"Proxy group '{proxy_group_name}' in rule '{rule_str}' not found")
                continue
            rule = Rule(type=rule_type, value=value, proxy_group=proxy_group)
        elif len(items) == 4:
            rule_type = items[0].strip()
            value = items[1].strip()
            proxy_group_name = items[2].strip()
            tag = items[3].strip()
            try:
                proxy_group = proxy_groups_map[proxy_group_name]
            except KeyError:
                logger.error(f"Proxy group '{proxy_group_name}' not found")
                continue
            rule = Rule(type=rule_type, value=value, proxy_group=proxy_group, tag=tag)
        else:
            logger.error(f"rule {rule_str} not support")
            continue
        if rule is not None:
            rules.append(rule)

    subscribe_config = SubscribeConfig(
        sub_type=target, begin_comment=begin_comment, proxys=proxys, proxy_groups=proxy_groups, rules=rules
    )
    return subscribe_config
