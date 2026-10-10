FROM ubuntu:22.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install OpenSSH server, sudo, and basic system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    sudo \
    curl \
    net-tools \
    procps \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Configure SSH daemon
RUN mkdir -p /var/run/sshd \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

# Create low-privilege service account: svc_backup
RUN useradd -m -s /bin/bash -u 1001 svc_backup \
    && echo "svc_backup:ShadowBackup#2026!" | chpasswd

# Install Root Flag in /root/flag.txt (accessible only by root)
COPY flag.txt /root/flag.txt
RUN chmod 600 /root/flag.txt && chown root:root /root/flag.txt

# Install vulnerable backup script
COPY backup-vault.sh /usr/local/bin/backup-vault.sh
RUN chmod 755 /usr/local/bin/backup-vault.sh && chown root:root /usr/local/bin/backup-vault.sh

# Install sudoers rule for svc_backup
COPY sudoers_svc_backup /etc/sudoers.d/svc_backup
RUN chmod 440 /etc/sudoers.d/svc_backup && chown root:root /etc/sudoers.d/svc_backup

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 22

CMD ["/usr/local/bin/entrypoint.sh"]
