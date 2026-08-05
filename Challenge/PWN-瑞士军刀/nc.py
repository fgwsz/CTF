#!/usr/bin/python3
#-*- coding:utf-8 -*-

from pwn import *
# 连接远程服务的 10198 端口
io = remote('160.202.254.160', 10198)
# 进入interactive交互界面
io.interactive()
