#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 17-11-18 上午10:36
"""
import json
from concurrent.futures import ThreadPoolExecutor

from tornado.web import RequestHandler

from simple_webssh.constant import MAX_THREAD_COUNT

__all__ = ["BaseHandler", "thread_pool"]

thread_pool = ThreadPoolExecutor(MAX_THREAD_COUNT)


class BaseHandler(RequestHandler):
    """
    所有handler的基类
    """

    def __init__(self, application, request, **kwargs):
        """
            所有handler的基类
        Args:

        """

        super().__init__(application, request, **kwargs)
        self.json_args = None
        self.rs_body = {
            "code": 0,
            "msg": "success",
            "data": {}
        }

    def data_received(self, chunk):
        pass

    def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            try:
                self.body_args = json.loads(self.request.body.decode(), encoding="utf8")
            except ValueError:
                self.body_args = None
        else:
            self.body_args = None

    def write_error(self, status_code, **kwargs):
        super().write_error(status_code, **kwargs)

    def get_json_port(self, port_name):
        value = self.body_args.get(port_name)
        try:
            port = int(value)
        except ValueError:
            port = 0

        if 0 < port < 65535:
            return port

        raise ValueError("Invalid port {}".format(value))

    def get_json_name(self, name):
        value = self.body_args.get(name)
        if not value:
            raise ValueError("Empty {}".format(name))
        return value

    def get_necessary_argument(self, name):
        value = self.get_argument(name)
        if not value:
            raise ValueError("Empty {}".format(name))
        return value

    def get_port(self, port_name):
        value = self.get_necessary_argument(port_name)
        try:
            port = int(value)
        except ValueError:
            port = 0

        if 0 < port < 65535:
            return port

        raise ValueError("Invalid port {}".format(value))
