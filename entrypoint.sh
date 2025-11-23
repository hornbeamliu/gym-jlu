#!/bin/bash
. bin/activate
# 启动cron服务
sudo service cron start

# 加载定时任务
crontab crontab.txt
crontab -l

python3 hello.py

