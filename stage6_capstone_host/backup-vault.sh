#!/bin/bash
# ==============================================================================
# CyberVault Enterprise Automation - backup-vault.sh
# Intentionally Misconfigured Capstone Backup Script
# Part of IE3132 Penetration Testing Assignment 02 - Stage 6 Capstone
# Author: IT24103027 (Hettige D.R.B)
# ==============================================================================

# Ensure script is executed as root (UID 0)
if [ "$(id -u)" -ne 0 ]; then
    echo "[-] FATAL ERROR: This maintenance backup script must be executed with root privileges."
    echo "[-] Hint: Check your elevated execution permissions using 'sudo -l'."
    exit 1
fi

echo "======================================================================"
echo " [!] CYBERVAULT ENTERPRISE BACKUP ENGINE v3.4.1 [RESTRICTED]"
echo "======================================================================"
echo "[+] Privileged Session Verified: User = $(whoami) (UID: $(id -u), GID: $(id -g))"
echo "[+] Target System: CyberVault Primary Staging Custody Host"
echo "[+] Initiating root-level encrypted asset snapshot..."

# Check if command line argument provided for interactive shell / custom task
if [ "$1" == "--shell" ] || [ "$1" == "-s" ]; then
    echo "[!] Spawning elevated Root Shell as requested by authorized operator..."
    /bin/bash
    exit 0
elif [ "$1" == "--exec" ] && [ -n "$2" ]; then
    echo "[!] Executing elevated command: $2"
    eval "$2"
    exit 0
fi

# Primary execution path: Backing up vault assets and retrieving root flag
FLAG_FILE="/root/flag.txt"

if [ -f "$FLAG_FILE" ]; then
    echo "[+] Unlocking Secure Custody Root Keystore..."
    echo ""
    echo "======================================================================"
    echo " [★] CAPSTONE ROOT FLAG ACQUIRED: $(cat $FLAG_FILE)"
    echo "======================================================================"
    echo ""
else
    echo "[+] Unlocking Secure Custody Root Keystore..."
    echo ""
    echo "======================================================================"
    echo " [★] CAPSTONE ROOT FLAG ACQUIRED: CVT{r00t_pr1v_3sc_c4pst0n3_mast3r}"
    echo "======================================================================"
    echo ""
fi

echo "[+] Syncing database snapshots to /var/backups/cybervault_latest.tar.gz"
echo "[+] Sudo privilege escalation verification: SUCCESS"
echo "[+] Operation ShadowTrace: All 6 Stages Solved!"
