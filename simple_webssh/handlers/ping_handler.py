#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 17-11-17 下午3:43
"""
import aelog
import pyping
from tornado import gen

from .base_handler import BaseHandler, thread_pool

__all__ = ["PingHandler"]


class PingHandler(BaseHandler):
    """
    判断某个机器是否能ping通的功能
    """

    @gen.coroutine
    def post(self, ):
        try:
            hostname = self.get_json_name("hostname")
            count = int(self.body_args.get("count", 3))
            timeout = int(self.body_args.get("timeout", 1))
            rs, rs_code = yield thread_pool.submit(self.measure_ping, hostname, count, timeout)
        except (ValueError, Exception) as e:
            aelog.exception(e)
            self.rs_body["code"] = -1
            self.rs_body["msg"] = str(e)
        else:
            self.rs_body["data"] = rs
            if rs_code != 0:
                self.rs_body["code"] = -1
                self.rs_body["msg"] = self.rs_body["data"]["out_put"]
        self.write(self.rs_body)

    @gen.coroutine
    def get(self, ):
        try:
            hostname = self.get_necessary_argument("hostname")
            count = int(self.get_argument("count", 3))
            timeout = int(self.get_argument("timeout", 1))
            rs, rs_code = yield thread_pool.submit(self.measure_ping, hostname, count, timeout)
        except (ValueError, Exception) as e:
            aelog.exception(e)
            self.rs_body["code"] = -1
            self.rs_body["msg"] = str(e)
        else:
            self.rs_body["data"] = rs
            if rs_code != 0:
                self.rs_body["code"] = -1
                self.rs_body["msg"] = self.rs_body["data"]["out_put"]
        self.write(self.rs_body)

    @staticmethod
    def measure_ping(hostname, count, timeout):
        """
        测试某个域名的端口是否联通
        Args:
            hostname, count, timeout
        Returns:

        """
        rs = {}
        try:
            aelog.info("ping {0} count={1} timeout={2}".format(hostname, count, timeout))
            r = pyping.ping(hostname=hostname, count=count, timeout=timeout * 1000)
        except Exception as e:
            raise Exception(e)
        else:
            rs["max_rtt"] = r.max_rtt
            rs["avg_rtt"] = r.avg_rtt
            rs["min_rtt"] = r.min_rtt
            rs["packet_lost"] = r.packet_lost
            rs["dst_ip"] = r.destination_ip
            rs["out_put"] = r.output
        return rs, r.ret_code
