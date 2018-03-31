#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 17-11-18 下午1:36
"""

from .handlers import *

__all__ = ["handlers"]

handlers = [
    (r'/webssh/connection', WebsshHandler),
    (r'/webssh/session', WebsshSocketHandler),
    (r'/measure/telnet', TelnetHandler),
    (r'/measure/ping', PingHandler),
]
