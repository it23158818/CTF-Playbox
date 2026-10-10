import os
from flask import Flask, render_template, request, jsonify, send_file
from generate_logs import generate_log_file, LOG_FILE, STAGE5_FLAG, ATTACKER_IP

app = Flask(__name__)

# Mock users extracted from CyberVault system accounts
SYSTEM_USERS = [
    {"id": 1, "username": "admin",          "full_name": "Root Custodian Admin",       "email": "secops@cybervaulttech.com",     "role": "vault_administrator",  "status": "Active",   "last_login": "2026-10-08 01:30:12"},
    {"id": 2, "username": "operator_dave",  "full_name": "Dave Mitchell",             "email": "dave@cybervaulttech.com",      "role": "vault_operator",       "status": "Active",   "last_login": "2026-10-07 18:22:05"},
    {"id": 3, "username": "auditor_alice",  "full_name": "Alice Henderson",           "email": "alice@cybervaulttech.com",     "role": "compliance_auditor",   "status": "Active",   "last_login": "2026-10-06 09:44:33"},
    {"id": 4, "username": "svc_backup",     "full_name": "Backup Automation Service", "email": "svc_backup@cybervaulttech.com","role": "service_account",      "status": "Compromised","last_login": "2026-10-08 02:12:55"},
    {"id": 5, "username": "j.fernandez",    "full_name": "Juan Fernandez",            "email": "juan@cybervaulttech.com",      "role": "vault_operator",       "status": "Inactive", "last_login": "2026-09-30 14:10:00"},
    {"id": 6, "username": "m.chen",         "full_name": "Michelle Chen",             "email": "mchen@cybervaulttech.com",     "role": "compliance_auditor",   "status": "Active",   "last_login": "2026-10-09 08:55:19"},
    {"id": 7, "username": "r.patel",        "full_name": "Raj Patel",                 "email": "raj@cybervaulttech.com",       "role": "vault_operator",       "status": "Active",   "last_login": "2026-10-08 11:30:41"},
]

STAGE6_SSH_INFO = {
    "host": os.environ.get("STAGE6_HOST", "localhost"),
    "port": int(os.environ.get("STAGE6_PORT", 2222)),
    "user": "svc_backup",
    "pass": "ShadowBackup#2026!",
    "url": os.environ.get("STAGE6_WEB_URL", "http://localhost:5006")
}

# Ensure log exists
if not os.path.exists(LOG_FILE):
    generate_log_file()

def read_logs():
    if not os.path.exists(LOG_FILE):
        generate_log_file()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

@app.route("/")
def index():
    lines = read_logs()
    failed_401_count = sum(1 for line in lines if " 401 " in line and ATTACKER_IP in line)
    return render_template(
        "forensics.html",
        log_lines=lines,
        total_lines=len(lines),
        failed_count=failed_401_count,
        attacker_ip=ATTACKER_IP,
        stage6_info=STAGE6_SSH_INFO
    )

@app.route("/api/logs/raw")
def download_raw():
    return send_file(LOG_FILE, mimetype="text/plain", as_attachment=True, download_name="audit_access.log")

@app.route("/api/logs")
def get_logs_json():
    lines = read_logs()
    return jsonify({
        "total": len(lines),
        "logs": lines
    })

@app.route("/api/validate-flag", methods=["POST"])
def validate_flag():
    data = request.get_json(silent=True) or request.form
    user_flag = data.get("flag", "").strip()
    
    if user_flag == STAGE5_FLAG:
        return jsonify({
            "valid": True,
            "message": "Flag accepted! Access trail confirmed.",
            "stage": 5,
            "stage6_info": STAGE6_SSH_INFO
        }), 200
    else:
        return jsonify({"valid": False, "message": "Invalid flag"}), 400

@app.route("/api/users")
def get_users():
    return jsonify({"total": len(SYSTEM_USERS), "users": SYSTEM_USERS})

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "stage": "Stage 5 - Digital Forensics"}), 200

@app.route("/reset", methods=["POST"])
def reset():
    generate_log_file()
    return jsonify({"status": "reset_complete", "message": "Stage 5 log file regenerated to initial state."}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5005))
    print(f"[*] Starting CyberVault Stage 5 Forensic Service on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
