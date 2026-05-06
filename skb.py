import os, sys, time, ping3, asyncio, aiohttp, argparse
from datetime import datetime

w, g, y, r, b, cyan = "\033[1;00m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m", "\033[1;36m"

def Logo():
    os.system("clear")
    print(f"{r} ██████  ███████ ██   ██ \n ██   ██ ██       ██ ██  \n ██   ██ █████     ███   \n ██   ██ ██       ██ ██  \n ██████  ███████ ██   ██ \n{w} ───────────────────────\n  BY: {y}TUNAUNGKYAW {w}| {g}v1.1{w}")
    print(f"{cyan}{'='*os.get_terminal_size().columns}\n{w}[*] Target: Ruijie Bypass\n{cyan}{'='*os.get_terminal_size().columns}")

class InternetAccess:
    async def is_internet_access(self, session):
        try:
            async with session.get("https://httpbin.org", timeout=3) as req:
                return f"{g}True{w}"
        except: return f"{r}False{w}"

    async def execute(self):
        Logo()
        async with aiohttp.ClientSession() as session:
            while True:
                now = datetime.now().strftime("%H:%M:%S")
                is_open = await self.is_internet_access(session)
                try:
                    ping_val = ping3.ping('8.8.8.8', timeout=2)
                    ping_str = f"{g}{int(ping_val*1000)}ms" if ping_val else f"{r}Timeout"
                except: ping_str = f"{r}Unreachable"
                
                sys.stdout.write(f"\r{w}[{now}] {w}Ping: {ping_str} {w}| Internet: {is_open}  ")
                sys.stdout.flush()
                await asyncio.sleep(2)

def feature():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", choices=["internet", "setup"], required=True)
    args = parser.parse_args()
    if args.option == "setup": print("Setup Done")
    elif args.option == "internet": asyncio.run(InternetAccess().execute())

if __name__ == "__main__":
    try: feature()
    except KeyboardInterrupt: sys.exit()
