import os
import re
import sys
import json
import time
import ping3
import ntplib
import base64
import random
import string
import asyncio
import aiohttp
import argparse
import requests
from datetime import datetime

# Colors & Styling
w = "\033[1;00m"
g = "\033[1;32m"
y = "\033[1;33m"
r = "\033[1;31m"
b = "\033[1;34m"
cyan = "\033[1;36m"

def clear():
    os.system("clear")

def Line():
    print(f"{cyan}="*os.get_terminal_size().columns)

def Logo():
    clear()
    # DEX စာသားအလှ (ASCII Art)
    logo = f"""
{r} ██████  ███████ ██   ██ 
{r} ██   ██ ██       ██ ██  
{r} ██   ██ █████     ███   
{r} ██   ██ ██       ██ ██  
{r} ██████  ███████ ██   ██ 
{w} ───────────────────────
{w}  BY: {y}TUNAUNGKYAW {w}| {g}v1.0{w}
    """
    print(logo)
    Line()
    print(f"{w}[*] Target: Ruijie Network Bypass")
    print(f"{w}[*] Status: Ready to work")
    Line()

class Setup:
    def set(self):
        Logo()
        print(f"{g}[+] Starting Setup Process...")
        os.system("pkg update && pkg upgrade -y")
        os.system("pip install requests aiohttp ntplib pycryptodome ping3")
        # Default IP အနေနဲ့ သိမ်းထားမယ်
        with open(".ip", "w") as f:
            f.write("192.168.99.1")
        print(f"{g}[+] Setup Completed Successfully!")
        print(f"{y}[!] Now run: python skb.py -o internet")

class InternetAccess:
    def __init__(self):
        try:
            with open(".ip", "r") as f:
                self.ip = f.read().strip()
        except FileNotFoundError:
            self.ip = "192.168.99.1"

    async def is_internet_access(self, session):
        try:
            async with session.get("https://httpbin.org", timeout=3) as req:
                return f"{g}True{w}"
        except:
            return f"{r}False{w}"

    async def execute(self):
        Logo()
        print(f"{g}[+] Attempting to bypass internet...")
        print(f"{w}[*] Using Gateway IP: {self.ip}")
        Line()
        async with aiohttp.ClientSession() as session:
            while True:
                now = datetime.now().strftime("%H:%M:%S")
                is_open = await self.is_internet_access(session)
                ping_val = ping3.ping('8.8.8.8')
                ping_str = f"{g}{int(ping_val*1000)}ms" if ping_val else f"{r}Timeout"
                
                # Dashboard logic
                sys.stdout.write(f"\r{w}[{now}] {w}Ping: {ping_str} {w}| Internet: {is_open}  ")
                sys.stdout.flush()
                await asyncio.sleep(2)

def feature():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", help="features option", choices=["internet", "setup"], required=True)
    args = parser.parse_args() 
    
    if args.option == "setup":
        Setup().set()
    elif args.option == "internet":
        iobj = InternetAccess()
        asyncio.run(iobj.execute())

if __name__ == "__main__":
    try:
        feature()
    except KeyboardInterrupt:
        print(f"\n\n{r}[!] Stopped by user.")
        sys.exit()
