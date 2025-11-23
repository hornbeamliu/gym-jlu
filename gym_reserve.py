#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import ssl
import gzip
import time
import argparse
import sys
from http.client import HTTPResponse
from typing import Optional
from datetime import datetime, timedelta, timezone

# token 6EAFFB4F718DFC67A647F6F0AD7C4E72 55190613
# token EBA2E4E8A6E527096C34A0730CF91B4A sunty

# 创建北京时区 (UTC+8)
beijing_tz = timezone(timedelta(hours=8))

# 健身票配置
TICKET_CONFIGS = {
    'morning': {
        'id': 1593,
        'time': '6:00-7:30',
        'name': '早晨健身票',
        'description': '健身票6:00-7:30'
    },
    'evening': {
        'id': 1576,
        'time': '19:30-21:30',
        'name': '晚间健身票',
        'description': '健身票19:30-21:30'
    }
}

# 获取明天的日期（使用北京时间）
tomorrow = (datetime.now(beijing_tz) + timedelta(days=1)).strftime('%Y-%m-%d')

# 生成带日期和星期信息的标题
def generate_title_with_date(base_title):
    """生成带日期和星期信息的标题，如：6月20日 本周三 健身房预约成功"""
    # 获取明天的日期（预约当天）
    tomorrow_beijing_time = datetime.now(beijing_tz) + timedelta(days=1)
    
    # 获取月份和日期
    month = tomorrow_beijing_time.month
    day = tomorrow_beijing_time.day
    
    # 获取星期几
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday = weekdays[tomorrow_beijing_time.weekday()]
    
    # 生成完整标题
    return f"{month}月{day}日 {weekday} {base_title}"

# 忽略SSL证书验证（如果需要）
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 请求URL
url = "https://ss.jlu.edu.cn/easyserpClient/ticket/freeBuyTicket"

# 请求头
headers = {
    "Host": "ss.jlu.edu.cn",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/6.8.0(0x16080000) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.10(0x13080a10) XWEB/1227",
    "auth": "REEVVFUg8IOJFnWytC4NNSMDAA8O4cn4Ggpci8oMYNwQ8FLShA0QH3bNgs9o6sO2VB40n9j8x+hMAJ5S/eW2jLwN/EbNHd78rYAgi4vsdL5uo3VVyt/1ZNnmD2CHdvZImF1TIlXxbe166viYCuA+zuhh8AMJ44182477rGZn1EN1G1l33RpGe+qIqBbqvBMsHHaNgbU6421jLdQuCYmKQSAqDCH2GEO9AlkcCpegCcTAoTP15fPx8YheVZ+3AVJ8Zx5q3+5ZF5Q+Q9miUzMmzcr2ZJnd7WY8WUih0MHqUT9fyAIyyKwVhaVWWrBcYlxvGHNAckg61TJIEJi/7QPvVw==:taqI6IzBZluPPzjMzmtT/yWZp5fUeBe7Xu1FtYbUzp4XVKQYFM/X92m0Y9OeujFwx8iFK0t1qWf8UpJRWjKocqhc6WQz69jZsUT8a9x97b7Je+/TCcfkXsi2gSoykn9mLlJCL5mTF/OSaahTBANsY4FDNqmvMCiivslH/4ZjIhKAkv35C2QPiCdNDxB9sK/D",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://ss.jlu.edu.cn",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://ss.jlu.edu.cn/easyserp/index.html",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9"
}

# 生成请求数据
def create_request_data(ticket_id):
    return {
        "ticketInfo": f'[{{"ticketId":{ticket_id},"price":0}}]',
        "token": "EBA2E4E8A6E527096C34A0730CF91B4A",
        "shopNum": "0001",
        "useDay": tomorrow
    }

# 解析gzip压缩内容
def decode_response(response: HTTPResponse) -> Optional[str]:
    if response.status != 200:
        return f"请求失败，状态码: {response.status}"
    
    content_encoding = response.getheader('Content-Encoding', '').lower()
    raw_data = response.read()
    
    if 'gzip' in content_encoding:
        try:
            return gzip.decompress(raw_data).decode('utf-8')
        except Exception as e:
            return f"解压缩数据失败: {e}"
    else:
        try:
            return raw_data.decode('utf-8')
        except UnicodeDecodeError:
            return f"解码数据失败，原始数据长度: {len(raw_data)} 字节"

# 发送PushPlus通知
def send_pushplus_notification(title, content):
    pushplus_url = "https://www.pushplus.plus/api/send"
    pushplus_data = {
        "token": "1a4e4b3c5b0148a0bfb4d1697da270ed",
        "title": title,
        "content": content,
        "template": "json",
        "channel": "wechat",
        "pre": ""
    }
    encoded_data = json.dumps(pushplus_data).encode('utf-8')
    
    headers = {
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(pushplus_url, data=encoded_data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req, context=ssl_context) as response:
            result = response.read().decode('utf-8')
            print(f"\n推送通知结果:")
            print(result)
    except Exception as e:
        print(f"\n推送通知失败: {e}")

# 发送预约请求
def send_reservation_request(ticket_config):
    try:
        # 生成请求数据
        data = create_request_data(ticket_config['id'])
        # 对请求数据进行URL编码
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        
        # 创建请求对象
        req = urllib.request.Request(url, data=encoded_data, headers=headers, method='POST')
        
        # 发送请求
        with urllib.request.urlopen(req, context=ssl_context) as response:
            # 解析响应
            response_text = decode_response(response)
            
            # 打印状态码（使用北京时间）
            current_time = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{current_time}] 状态码: {response.status}")
            
            # 打印响应头
            print("\n响应头:")
            for header, value in response.getheaders():
                print(f"{header}: {value}")
            
            # 打印响应内容
            print("\n响应内容:")
            if response_text:
                # 尝试解析为JSON
                json_response = json.loads(response_text)
                print(json.dumps(json_response, ensure_ascii=False, indent=2))
                
                return json_response
            else:
                print("无响应内容或解析失败")
                return None
                
    except Exception as e:
        print(f"请求发送失败: {e}")
        return None

# 主函数
def main(ticket_type='morning'):
    # 获取健身票配置
    if ticket_type not in TICKET_CONFIGS:
        print(f"错误：未知的健身票类型 '{ticket_type}'")
        print(f"可用类型：{', '.join(TICKET_CONFIGS.keys())}")
        return
    
    ticket_config = TICKET_CONFIGS[ticket_type]
    print(f"开始预约 {ticket_config['name']} ({ticket_config['time']})")
    
    retry_count = 0
    max_retries = 3  # 最多重试3次
    
    while retry_count < max_retries:
        current_time = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[{current_time}] 尝试第 {retry_count + 1} 次预约...")
        
        # 发送预约请求
        json_response = send_reservation_request(ticket_config)
        
        if json_response is None:
            print("请求失败，1分钟后重试...")
            time.sleep(60)
            retry_count += 1
            continue
            
        # 检查预约结果
        if json_response.get("msg") == "success":
            # 发送成功通知
            print("预约成功！")
            send_pushplus_notification(
                generate_title_with_date("健身房预约成功"), 
                f"{ticket_config['description']} 预约成功！尝试次数: {retry_count + 1}"
            )
            break  # 预约成功，退出循环
        elif json_response.get("msg") == "fail":
            failure_reason = json_response.get("data", "未知原因")
            
            # 检查是否是"已达到购买上限"的情况（视为预约成功）
            if "同一场次限制购票1张,您已达到购买上限，请选择其他场次" in failure_reason:
                print("检测到已预约过该场次，视为预约成功！")
                send_pushplus_notification(
                    generate_title_with_date("健身房预约成功"), 
                    f"{ticket_config['description']} 已预约成功（检测到重复预约）！尝试次数: {retry_count + 1}"
                )
                break  # 视为预约成功，退出循环
            
            # 其他失败情况，继续重试
            print(f"预约失败，原因：{failure_reason}")
            
            if retry_count == 0:
                send_pushplus_notification(
                    generate_title_with_date("健身房开始预约"), 
                    f"{ticket_config['description']} 首次预约失败，原因：{failure_reason}。将每分钟自动重试直至成功。"
                )
            
            # 等待1分钟后重试
            time.sleep(60)
            retry_count += 1
        else:
            # 未知响应
            print(f"收到未知响应: {json_response}")
            time.sleep(60)
            retry_count += 1
    
    if retry_count >= max_retries:
        send_pushplus_notification(
            generate_title_with_date("健身房预约失败"), 
            f"{ticket_config['description']} 预约失败，已达到最大重试次数 {max_retries}。"
        )
        print(f"已达到最大重试次数 {max_retries}，停止尝试。")

# 解析命令行参数
def parse_arguments():
    parser = argparse.ArgumentParser(description='吉林大学健身票预约程序')
    parser.add_argument('ticket_type', 
                       choices=['morning', 'evening'], 
                       nargs='?',
                       default='morning',
                       help='健身票类型: morning (6:00-7:30) 或 evening (19:30-21:30)')
    return parser.parse_args()

# 执行主函数
if __name__ == "__main__":
    args = parse_arguments()
    main(args.ticket_type) 