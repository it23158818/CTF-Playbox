import os
import random
from datetime import datetime, timedelta

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_access.log")

STAGE5_FLAG = "CVT{f0r3ns1c_l0g_tr41l_unv31l3d}"
ATTACKER_IP = "198.51.100.42"
TARGET_SSH_HOST = "10.0.6.10 (port 2222)"
SVC_CREDS = "svc_backup:ShadowBackup#2026!"

BENIGN_IPS = [
    "10.0.4.12", "10.0.4.15", "10.0.4.88", "192.168.1.104", 
    "192.168.1.115", "172.16.20.5", "10.0.1.200", "192.168.2.14"
]

BENIGN_ENDPOINTS = [
    ("/index.html", 200, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"),
    ("/assets/css/vault.css", 200, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"),
    ("/assets/img/logo.png", 200, "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"),
    ("/api/status", 200, "CyberVault-HealthProbe/1.4"),
    ("/dashboard", 302, "Mozilla/5.0 (X11; Linux x86_64)"),
    ("/assets/js/app.js", 304, "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"),
    ("/robots.txt", 404, "Mozilla/5.0 (compatible; Googlebot/2.1)"),
    ("/favicon.ico", 200, "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
]

def generate_log_file():
    start_time = datetime(2026, 10, 8, 1, 30, 0)
    lines = []
    
    # 1. Normal morning traffic before attack
    curr_time = start_time
    for _ in range(80):
        curr_time += timedelta(seconds=random.randint(5, 45))
        ip = random.choice(BENIGN_IPS)
        endpoint, status, ua = random.choice(BENIGN_ENDPOINTS)
        size = random.randint(300, 4800)
        timestamp_str = curr_time.strftime("%d/%b/%Y:%H:%M:%S +0000")
        lines.append(f'{ip} - - [{timestamp_str}] "GET {endpoint} HTTP/1.1" {status} {size} "-" "{ua}"')

    # 2. Reconnaissance scan from attacker IP
    curr_time += timedelta(minutes=5)
    recon_targets = [
        "/", "/wp-login.php", "/phpmyadmin", "/config.json", "/.env", "/api/v1/auth"
    ]
    for target in recon_targets:
        curr_time += timedelta(seconds=random.randint(1, 4))
        timestamp_str = curr_time.strftime("%d/%b/%Y:%H:%M:%S +0000")
        lines.append(f'{ATTACKER_IP} - - [{timestamp_str}] "GET {target} HTTP/1.1" 404 198 "-" "python-requests/2.28.1"')

    # 3. Sustained brute-force pattern against /admin returning 401 Unauthorized
    curr_time += timedelta(minutes=2)
    passwords_tried = [
        "admin123", "password", "vault2026", "root", "12345678", "secret", "masterkey",
        "cybervault", "letmein", "toor", "pass123", "administrator", "shadow"
    ]
    for pwd in passwords_tried:
        curr_time += timedelta(seconds=random.randint(3, 8))
        timestamp_str = curr_time.strftime("%d/%b/%Y:%H:%M:%S +0000")
        lines.append(f'{ATTACKER_IP} - - [{timestamp_str}] "POST /admin HTTP/1.1" 401 512 "-" "python-requests/2.28.1 [AUTH_FAIL: user=admin]"')

    # Interleave some harmless traffic
    for _ in range(15):
        curr_time += timedelta(seconds=random.randint(10, 30))
        ip = random.choice(BENIGN_IPS)
        endpoint, status, ua = random.choice(BENIGN_ENDPOINTS)
        size = random.randint(300, 2400)
        timestamp_str = curr_time.strftime("%d/%b/%Y:%H:%M:%S +0000")
        lines.append(f'{ip} - - [{timestamp_str}] "GET {endpoint} HTTP/1.1" {status} {size} "-" "{ua}"')

    # 4. Attacker's breakthrough request returning 200 OK with x-debug-flag and SSH credentials
    curr_time += timedelta(seconds=12)
    timestamp_str = curr_time.strftime("%d/%b/%Y:%H:%M:%S +0000")
    breakthrough_line = (
        f'{ATTACKER_IP} - - [{timestamp_str}] "POST /admin HTTP/1.1" 200 14820 "-" '
        f'"python-requests/2.28.1" [x-debug-flag: {STAGE5_FLAG}] '
        f'[AUDIT_NOTE: Bypass detected. Staging target: {TARGET_SSH_HOST} / SSH credentials discovered: {SVC_CREDS}]'
    )
    lines.append(breakthrough_line)

    # 5. Subsequent routine traffic
    for _ in range(40):
        curr_time += timedelta(seconds=random.randint(5, 60))
        ip = random.choice(BENIGN_IPS)
        endpoint, status, ua = random.choice(BENIGN_ENDPOINTS)
        size = random.randint(300, 4800)
        timestamp_str = curr_time.strftime("%d/%b/%Y:%H:%M:%S +0000")
        lines.append(f'{ip} - - [{timestamp_str}] "GET {endpoint} HTTP/1.1" {status} {size} "-" "{ua}"')

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
        
    print(f"[+] Stage 5 Access Log generated with {len(lines)} entries at: {LOG_FILE}")
    print(f"[+] Malicious IP: {ATTACKER_IP} | Flag: {STAGE5_FLAG}")
    print(f"[+] Next Stage Pivoting Credentials: {SVC_CREDS} -> {TARGET_SSH_HOST}")

if __name__ == "__main__":
    generate_log_file()
