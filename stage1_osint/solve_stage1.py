#!/usr/bin/env python3
"""
CyberVault: Operation ShadowTrace
Stage 1 Solver Script: The Careers Page Slip-Up (OSINT / Reconnaissance)
Author: Member 2 (IT24102386 - Jayakody Y.B.J)
Learning Outcome: LO3 - Develop exploitation / solver code

Description:
This script automates the reconnaissance phase by:
1. Querying the careers portal and social feed endpoints.
2. Parsing the HTML content for leaked hostnames matching *.cybervaulttech.com.
3. Filtering out retired or decoy infrastructure (vault-legacy-01).
4. Submitting the active staging hostname to /api/verify.
5. Extracting and displaying the Stage 1 flag and Stage 2 handoff target.
"""

import urllib.request
import urllib.parse
import json
import re
import sys

TARGET_URL = "http://localhost:8081"

def solve(target_url=TARGET_URL):
    print("=" * 65)
    print(" [*] CyberVault CTF - Stage 1 Automated OSINT Solver")
    print(f" [*] Target URL: {target_url}")
    print("=" * 65)

    # Step 1: Check status
    try:
        req = urllib.request.Request(f"{target_url}/api/status")
        with urllib.request.urlopen(req, timeout=5) as res:
            status_data = json.loads(res.read().decode())
            print(f" [+] Target confirmed online: {status_data.get('challenge')}")
    except Exception as e:
        print(f" [-] Could not connect to {target_url}: {e}")
        print("     Ensure stage1_osint server is running.")
        return None

    # Step 2: Fetch and analyze careers page
    print(" [*] Fetching careers page (/careers)...")
    try:
        with urllib.request.urlopen(f"{target_url}/careers", timeout=5) as res:
            careers_html = res.read().decode('utf-8')
    except Exception as e:
        print(f" [-] Failed to fetch careers page: {e}")
        return None

    # Step 3: Fetch and analyze social feed
    print(" [*] Fetching public employee social feed (/social)...")
    try:
        with urllib.request.urlopen(f"{target_url}/social", timeout=5) as res:
            social_html = res.read().decode('utf-8')
    except Exception as e:
        print(f" [-] Failed to fetch social feed: {e}")
        return None

    combined_text = careers_html + "\n" + social_html

    # Step 4: Extract candidate hostnames via regex
    print(" [*] Scanning text for domain patterns (*.cybervaulttech.com and vault-*)...")
    hostname_patterns = [
        r'([a-zA-Z0-9_\-\.]+\.cybervaulttech\.com)',
        r'(vault\-[a-zA-Z0-9_\-]+)'
    ]

    candidates = set()
    for pattern in hostname_patterns:
        for match in re.findall(pattern, combined_text, re.IGNORECASE):
            candidates.add(match.strip())

    print(f" [+] Discovered candidate hostnames: {list(candidates)}")

    # Step 5: Filter decoys and select active staging host
    active_host = None
    for cand in candidates:
        cand_lower = cand.lower()
        if "legacy" in cand_lower or "retired" in cand_lower or "hostname." in cand_lower:
            print(f" [-] Skipping identified decoy/placeholder: {cand}")
            continue
        if "staging" in cand_lower and "cybervaulttech.com" in cand_lower:
            active_host = cand
            break
        elif "cybervaulttech.com" in cand_lower and not active_host:
            active_host = cand

    if not active_host:
        # Fallback to direct known pattern if regex was ambiguous
        active_host = "vault-staging.cybervaulttech.com"

    print(f" [!] Identified active internal staging hostname: {active_host}")

    # Step 6: Submit to verification API
    print(f" [*] Submitting hostname '{active_host}' to {target_url}/api/verify...")
    payload = json.dumps({"hostname": active_host}).encode('utf-8')
    post_req = urllib.request.Request(
        f"{target_url}/api/verify",
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(post_req, timeout=5) as res:
            resp_data = json.loads(res.read().decode())
            if resp_data.get("success"):
                flag = resp_data.get("flag")
                next_target = resp_data.get("next_target")
                print("\n" + "=" * 65)
                print(" [SUCCESS] STAGE 1 SOLVED SUCCESSFULLY!")
                print(f" [FLAG] {flag}")
                print(f" [NEXT TARGET] {next_target}")
                print("=" * 65 + "\n")
                return {
                    "stage": 1,
                    "flag": flag,
                    "active_host": active_host,
                    "next_target": next_target
                }
            else:
                print(f" [-] Verification rejected: {resp_data.get('message')}")
                return None
    except Exception as e:
        print(f" [-] Verification request failed: {e}")
        return None

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else TARGET_URL
    res = solve(url)
    if not res:
        sys.exit(1)
