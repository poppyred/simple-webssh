#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 17-11-17 下午3:43
"""
import io
import weakref

import aelog
import paramiko
import tornado.web
import tornado.websocket
from tornado import gen
from tornado.ioloop import IOLoop
# noinspection PyProtectedMember
from tornado.iostream import _ERRNO_CONNRESET
from tornado.util import errno_from_exception
from tornado.websocket import WebSocketHandler

from .base_handler import BaseHandler, thread_pool
from ..constant import BUFFER_SIZE, DELAY_TIME

__all__ = ["WebsshHandler", "WebsshSocketHandler"]

workers = {}


def destroy_worker(worker):
    """
    超时处理
    Args:

    Returns:

    """
    if worker.handler:
        return
    aelog.info('destory worker {}'.format(worker.token))
    workers.pop(worker.token, None)
    worker.close()


class Worker(object):
    """
    通过ioloop和paramiko的channel实时处理任务
    Args:

    Returns:

    """

    def __init__(self, ssh, chan, dst_addr):
        """
        通过ioloop和paramiko的channel实时处理任务
        Args:

        Returns:

        """
        self.loop = IOLoop.current()
        self.ssh = ssh
        self.chan = chan
        self.dst_addr = dst_addr
        self.fd = chan.fileno()
        self.token = str(id(self))
        self.data_to_dst = []
        self.handler = None
        self.mode = IOLoop.READ

    def __call__(self, fd, event):
        if event & IOLoop.READ:
            self.read_event()
        if event & IOLoop.WRITE:
            self.write_event()
        if event & IOLoop.ERROR:
            self.close()

    def add_message(self, message):
        """

        Args:
            message
        Returns:

        """
        self.data_to_dst.append(message)

    def set_handler(self, handler):
        if not self.handler:
            self.handler = handler

    def update_handler(self, mode):
        if self.mode != mode:
            self.loop.update_handler(self.fd, mode)
            self.mode = mode

    def read_event(self):
        aelog.debug('worker {} on read'.format(self.token))
        try:
            data = self.chan.recv(BUFFER_SIZE)
        except (OSError, IOError) as e:
            aelog.exception(e)
            if errno_from_exception(e) in _ERRNO_CONNRESET:
                self.close()
        else:
            if not data:
                self.close()
                return
            try:
                aelog.debug('"{}" to {}'.format(data, self.handler.src_addr))
                self.handler.write_message(data)
            except tornado.websocket.WebSocketClosedError as e:
                aelog.exception(e)
                self.close()

    def write_event(self):
        aelog.debug('worker {} on write'.format(self.token))
        if not self.data_to_dst:
            return
        data = ''.join(self.data_to_dst)
        try:
            aelog.debug('"{}" to {}'.format(data, self.dst_addr))
            sent = self.chan.send(data)
        except (OSError, IOError) as e:
            aelog.error(e)
            if errno_from_exception(e) in _ERRNO_CONNRESET:
                self.close()
            else:
                self.update_handler(IOLoop.WRITE)
        else:
            self.data_to_dst = []
            data = data[sent:]
            if data:
                self.data_to_dst.append(data)
                self.update_handler(IOLoop.WRITE)
            else:
                self.update_handler(IOLoop.READ)

    def close(self):
        aelog.info('Closing worker {}'.format(self.token))
        if self.handler:
            self.loop.remove_handler(self.fd)
            self.handler.close()
        self.chan.close()
        self.ssh.close()
        aelog.info('Closed worker {0} success,Connection to {1} lost'.format(self.token, self.dst_addr))


class WebsshHandler(BaseHandler):
    def get(self):
        self.render('index.html')

    @gen.coroutine
    def post(self):
        try:
            args = self.get_post_args()
            worker = yield thread_pool.submit(self.create_worker, args)
        except Exception as e:
            aelog.exception(e)
            self.rs_body["code"] = -1
            self.rs_body["msg"] = str(e)
        else:
            workers[worker.token] = worker
            self.rs_body["data"]["token"] = worker.token
        self.write(self.rs_body)

    @staticmethod
    def get_ssh_pkey(privatekey, password):
        password = None if not password else password
        spkey = io.StringIO(privatekey.decode())
        try:
            pkey = paramiko.RSAKey.from_private_key(spkey, password=password)
        except paramiko.SSHException:
            pkey = paramiko.DSSKey.from_private_key(spkey, password=password)
        return pkey

    def get_private_key(self):
        try:
            return self.request.files.get('private_key')[0]['body']
        except TypeError as e:
            aelog.exception(e)

    def get_post_args(self):
        hostname = self.get_necessary_argument('hostname')
        port = self.get_port("port")
        username = self.get_necessary_argument('username')
        password = self.get_argument('password')
        private_key = self.get_private_key()
        pkey = self.get_ssh_pkey(private_key, password) if private_key else None
        args = (hostname, port, username, password, pkey)
        return args

    @staticmethod
    def create_worker(args):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        dst_addr = '{}:{}'.format(*args[:2])
        aelog.info('Connecting to {}'.format(dst_addr))
        ssh.connect(*args)
        chan = ssh.invoke_shell(term='xterm')
        chan.setblocking(0)
        # 创建处理任务
        worker = Worker(ssh, chan, dst_addr)
        # control timeout
        IOLoop.current().call_later(DELAY_TIME, destroy_worker, worker)
        return worker


class WebsshSocketHandler(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = IOLoop.current()
        self.weakref_worker = None
        self.src_addr = None

    def check_origin(self, origin):
        return True

    def open(self):
        self.src_addr = '{}:{}'.format(*self.stream.socket.getpeername())
        aelog.info('Connected from {}'.format(self.src_addr))
        worker = workers.pop(self.get_argument('token'), None)
        if not worker:
            self.close(reason='Invalid worker token')
            return
        self.set_nodelay(True)
        worker.set_handler(self)
        self.weakref_worker = weakref.ref(worker)
        self.loop.add_handler(worker.fd, worker, IOLoop.READ)

    def on_message(self, message):
        aelog.debug('"{}" from {}'.format(message, self.src_addr))
        worker = self.weakref_worker()
        worker.add_message(message)
        worker.write_event()

    def on_close(self):
        aelog.info('Disconnected from {}'.format(self.src_addr))
        worker = self.weakref_worker() if self.weakref_worker else None
        if worker:
            worker.close()

    def data_received(self, chunk):
        pass
