#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 17-11-17 下午3:44
"""
import socket
import aelog

from tornado import gen

from .base_handler import BaseHandler, thread_pool

__all__ = ["TelnetHandler"]


class TelnetHandler(BaseHandler):
    """
    判断某个机器的端口是否打开的功能
    """

    @gen.coroutine
    def post(self, ):
        try:
            hostname = self.get_json_name("hostname")
            port = self.get_json_port("port")
            timeout = int(self.body_args.get("timeout", 1))
            yield thread_pool.submit(self.measure_telent, hostname, port, timeout)
        except (ValueError, OSError) as e:
            aelog.exception(e)
            self.rs_body["code"] = -1
            self.rs_body["msg"] = str(e)
        self.write(self.rs_body)

    @gen.coroutine
    def get(self, ):
        try:
            hostname = self.get_necessary_argument("hostname")
            port = self.get_port("port")
            timeout = int(self.get_argument("timeout", 1))
            yield thread_pool.submit(self.measure_telent, hostname, port, timeout)
        except (ValueError, OSError) as e:
            aelog.exception(e)
            self.rs_body["code"] = -1
            self.rs_body["msg"] = str(e)
        self.write(self.rs_body)

    @staticmethod
    def measure_telent(hostname, port, timeout):
        """
        测试某个域名的端口是否联通
        Args:
            hostname, port, timeout
        Returns:

        """
        s = socket.socket()
        s.settimeout(timeout)
        try:
            aelog.info("telnet {0}:{1} timeout={2}".format(hostname, port, timeout))
            s.connect((hostname, port))
        except TimeoutError as e:
            raise TimeoutError("connecting to ({0},{1}) timeout, {2}".format(hostname, port, e))
        except ConnectionError as e:
            raise ConnectionError("connect error: {0}".format(e))
        except OSError as e:
            raise OSError(e)
        finally:
            s.close()
