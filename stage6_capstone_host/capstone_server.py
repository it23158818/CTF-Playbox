import os
import subprocess
from flask import Flask, render_template, request, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR if os.path.isdir(STATIC_DIR) else None,
    static_url_path="/static"
)

STAGE6_FLAG = os.environ.get("STAGE6_FLAG", "CVT{r00t_pr1v_3sc_c4pst0n3_mast3r}")

def simulate_terminal(cmd):
    """
    Simulates the exact bash terminal environment of the svc_backup user on the staging host.
    Matches Section 5.6 of IE3132 Assignment 01/02.
    """
    cmd = cmd.strip()
    cmd_lower = cmd.lower()
    
    if cmd == "whoami":
        return {"output": "svc_backup", "is_error": False, "is_flag": False}
        
    elif cmd == "id":
        return {
            "output": "uid=1001(svc_backup) gid=1001(svc_backup) groups=1001(svc_backup)",
            "is_error": False, 
            "is_flag": False
        }
        
    elif cmd in ["pwd", "echo $HOME"]:
        return {"output": "/home/svc_backup", "is_error": False, "is_flag": False}
        
    elif cmd in ["uname -a", "uname -r"]:
        return {"output": "Linux cybervault-staging 5.15.0-89-generic #99-Ubuntu SMP x86_64 x86_64 x86_64 GNU/Linux", "is_error": False, "is_flag": False}
        
    elif cmd in ["ls", "ls -la", "ls -l"]:
        return {
            "output": "total 20\ndrwxr-xr-x 2 svc_backup svc_backup 4096 Oct  8 02:00 .\ndrwxr-xr-x 3 root       root       4096 Oct  8 01:50 ..\n-rw-r--r-- 1 svc_backup svc_backup  220 Oct  8 01:50 .bash_logout\n-rw-r--r-- 1 svc_backup svc_backup 3771 Oct  8 01:50 .bashrc\n-rw-r--r-- 1 svc_backup svc_backup  807 Oct  8 01:50 .profile",
            "is_error": False,
            "is_flag": False
        }
        
    elif "cat /root/flag.txt" in cmd or "/root/flag" in cmd and not cmd.startswith("sudo"):
        return {
            "output": "cat: /root/flag.txt: Permission denied",
            "is_error": True,
            "is_flag": False
        }

    elif cmd == "sudo -l":
        return {
            "output": (
                "Matching Defaults entries for svc_backup on cybervault-staging:\n"
                "    env_reset, mail_badpass, secure_path=/usr/local/sbin\\:/usr/local/bin\\:/usr/sbin\\:/usr/bin\\:/sbin\\:/bin\n\n"
                "User svc_backup may run the following commands on cybervault-staging:\n"
                "    (root) NOPASSWD: /usr/local/bin/backup-vault.sh"
            ),
            "is_error": False,
            "is_flag": False
        }
        
    elif cmd.startswith("sudo /usr/local/bin/backup-vault.sh") or cmd.startswith("/usr/local/bin/backup-vault.sh"):
        if not cmd.startswith("sudo"):
            return {
                "output": "[-] FATAL ERROR: This maintenance backup script must be executed with root privileges.\n[-] Hint: Check your elevated execution permissions using 'sudo -l'.",
                "is_error": True,
                "is_flag": False
            }
            
        output = (
            "======================================================================\n"
            " [!] CYBERVAULT ENTERPRISE BACKUP ENGINE v3.4.1 [RESTRICTED]\n"
            "======================================================================\n"
            "[+] Privileged Session Verified: User = root (UID: 0, GID: 0)\n"
            "[+] Target System: CyberVault Primary Staging Custody Host\n"
            "[+] Initiating root-level encrypted asset snapshot...\n"
            "[+] Unlocking Secure Custody Root Keystore...\n\n"
            "======================================================================\n"
            f" [★] CAPSTONE ROOT FLAG ACQUIRED: {STAGE6_FLAG}\n"
            "======================================================================\n\n"
            "[+] Syncing database snapshots to /var/backups/cybervault_latest.tar.gz\n"
            "[+] Sudo privilege escalation verification: SUCCESS\n"
            "[+] Operation ShadowTrace: All 6 Stages Solved!"
        )
        return {"output": output, "is_error": False, "is_flag": True}
        
    elif cmd.startswith("sudo") and not "/usr/local/bin/backup-vault.sh" in cmd:
        return {
            "output": f"Sorry, user svc_backup is not allowed to execute '{cmd.replace('sudo ', '')}' as root on cybervault-staging.",
            "is_error": True,
            "is_flag": False
        }
        
    elif cmd == "help":
        return {
            "output": "Available commands: whoami, id, uname -a, pwd, ls -la, sudo -l, sudo /usr/local/bin/backup-vault.sh, cat /root/flag.txt, clear, exit",
            "is_error": False,
            "is_flag": False
        }
        
    else:
        return {
            "output": f"bash: {cmd}: command not found. Try 'whoami', 'id', 'sudo -l', or 'help'.",
            "is_error": True,
            "is_flag": False
        }

@app.route("/", methods=["GET", "POST"])
@app.route("/api/index", methods=["GET", "POST"])
@app.route("/api/index.py", methods=["GET", "POST"])
def index():
    # Dispatch when Vercel rewrites requests to /api/index?path=...
    target_path = request.args.get("path", "").strip()
    if target_path:
        clean_path = target_path.rstrip("/") if target_path != "/" else "/"
        if not clean_path.startswith("/"):
            clean_path = "/" + clean_path

        if clean_path in ("/api/exec", "/api/exec/"):
            return exec_cmd()
        elif clean_path in ("/health", "/health/"):
            return health()
        elif clean_path in ("/reset", "/reset/"):
            return reset()
        elif clean_path in ("/", ""):
            return render_template("terminal.html")

    return render_template("terminal.html")

@app.route("/api/exec", methods=["GET", "POST"])
def exec_cmd():
    if request.method == "GET":
        return jsonify({"error": "POST method required with JSON {'command': '...'}"}), 405
    data = request.get_json(silent=True) or request.form
    command = data.get("command", "").strip() if data else ""
    result = simulate_terminal(command)
    return jsonify(result), 200

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "stage": "Stage 6 - System Security Capstone"}), 200

@app.route("/reset", methods=["GET", "POST"])
def reset():
    return jsonify({"status": "reset_complete", "message": "Stage 6 restored to pristine state."}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5006))
    print(f"[*] Starting CyberVault Stage 6 Capstone Service on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
