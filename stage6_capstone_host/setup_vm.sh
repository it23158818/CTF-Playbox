#!/bin/bash
# ==============================================================================
# CyberVault Capstone VM Setup Script (Ubuntu Server 22.04 LTS)
# Deploys Stage 6 System Security / Privilege Escalation Environment
# ==============================================================================

if [ "$EUID" -ne 0 ]; then
  echo "[-] Please run as root (sudo ./setup_vm.sh)"
  exit 1
fi

echo "[*] Configuring CyberVault Stage 6 Capstone Environment..."

# 1. Create svc_backup user if not exists
if id "svc_backup" &>/dev/null; then
    echo "[i] User svc_backup already exists."
else
    useradd -m -s /bin/bash -u 1001 svc_backup
    echo "svc_backup:ShadowBackup#2026!" | chpasswd
    echo "[+] Created service user: svc_backup"
fi

# 2. Deploy Root Flag
echo "CVT{r00t_pr1v_3sc_c4pst0n3_mast3r}" > /root/flag.txt
chmod 600 /root/flag.txt
chown root:root /root/flag.txt
echo "[+] Root flag installed in /root/flag.txt (chmod 600)"

# 3. Deploy backup script
cp backup-vault.sh /usr/local/bin/backup-vault.sh
chmod 755 /usr/local/bin/backup-vault.sh
chown root:root /usr/local/bin/backup-vault.sh
echo "[+] Backup script installed to /usr/local/bin/backup-vault.sh"

# 4. Configure sudoers rule
echo "svc_backup ALL=(ALL) NOPASSWD: /usr/local/bin/backup-vault.sh" > /etc/sudoers.d/svc_backup
chmod 440 /etc/sudoers.d/svc_backup
chown root:root /etc/sudoers.d/svc_backup
echo "[+] Sudoers NOPASSWD rule configured for svc_backup"

# 5. Verify SSH configuration
systemctl enable ssh
systemctl restart ssh
echo "[+] SSH service verified and running."
echo "[+] Stage 6 Capstone VM deployment complete!"
