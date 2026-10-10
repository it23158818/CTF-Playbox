#!/bin/bash
set -e

# Generate host keys if missing
ssh-keygen -A

# Ensure correct permissions
chmod 600 /root/flag.txt
chmod 755 /usr/local/bin/backup-vault.sh
chmod 440 /etc/sudoers.d/svc_backup

echo "[*] CyberVault Stage 6 Capstone SSH Daemon starting..."
exec /usr/sbin/sshd -D -e
