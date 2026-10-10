"""
Stage 1: The Careers Page Slip-Up (OSINT / Reconnaissance)
CyberVault: Operation ShadowTrace
Author: Member 2 (IT24102386 - Jayakody Y.B.J)
Port: 8081
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sqlite3
import shutil
from flask import Flask, render_template, request, jsonify, Response, send_from_directory, send_file

PORT = int(os.environ.get("PORT", 8081))
STAGE1_FLAG = os.environ.get("STAGE1_FLAG", "CVT{0s1nt_st4g1ng_l34k_8291}")
STAGE2_URL = os.environ.get("STAGE2_URL", "http://localhost:8082")
STAGE4_FLAG = os.environ.get("STAGE4_FLAG", "CVT{sql1_byp4ss_v4ult_4dm1n}")
STAGE5_FLAG = os.environ.get("STAGE5_FLAG", "CVT{f0r3ns1c_l0g_tr41l_unv31l3d}")
STAGE5_URL = os.environ.get("STAGE5_URL", "/forensics")
ATTACKER_IP = "198.51.100.42"
CORRECT_HOSTNAME = "vault-staging.cybervaulttech.com"
DECOY_HOSTNAME = "vault-legacy-01"

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR, static_url_path="/static")

def get_stage5_log_path():
    candidates = [
        os.path.join(BASE_DIR, "audit_access.log"),
        os.path.join(os.path.dirname(BASE_DIR), "stage5_access_logs", "audit_access.log"),
        os.path.join("/tmp", "audit_access.log")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return os.path.join("/tmp", "audit_access.log") if bool(os.environ.get("VERCEL")) else os.path.join(BASE_DIR, "audit_access.log")

def read_stage5_logs():
    log_path = get_stage5_log_path()
    if not os.path.exists(log_path):
        try:
            from generate_logs import generate_log_file
            generate_log_file()
        except Exception:
            pass
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        except Exception:
            pass
    return []

# ============================================================================
# Stage 4 SQL Injection Database Setup (Embedded in Stage 1)
# ============================================================================

def is_vercel():
    return bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get("NOW_REGION"))

def get_stage1_db_path():
    if is_vercel():
        return os.path.join("/tmp", "cybervault_stage1.db")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "cybervault.db")

def init_stage1_db(target_path=None):
    path = target_path or get_stage1_db_path()
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vault_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id TEXT NOT NULL,
        asset_type TEXT NOT NULL,
        custody_status TEXT NOT NULL,
        encrypted_payload TEXT NOT NULL
    )
    """)

    users = [
        ('admin', 'CV_SuperSecretAdminKey!9283#', 'vault_administrator', 'Root Custodian Admin', 'secops@cybervaulttech.com'),
        ('operator_dave', 'DaveSecure#Pass2026', 'vault_operator', 'Dave Mitchell', 'dave@cybervaulttech.com'),
        ('auditor_alice', 'AuditTrack#Secure99', 'compliance_auditor', 'Alice Henderson', 'alice@cybervaulttech.com'),
        ('svc_backup', 'ShadowBackup#2026!', 'service_account', 'Backup Automation Service', 'svc_backup@cybervaulttech.com')
    ]
    cursor.executemany("INSERT INTO users (username, password, role, full_name, email) VALUES (?, ?, ?, ?, ?)", users)

    vault_records = [
        ('VAULT-BTC-001', 'Bitcoin Cold Storage', 'Secured (Multi-Sig 3/5)', 'enc_0x89f72b143a99e03d...'),
        ('VAULT-ETH-004', 'Ethereum Master Custody', 'Secured (HSM Module)', 'enc_0x4e21a88b5601c90f...'),
        ('VAULT-SOL-009', 'Solana Enterprise Reserve', 'Secured (Multi-Sig 2/3)', 'enc_0x117a09c4d8e77a12...')
    ]
    cursor.executemany("INSERT INTO vault_records (asset_id, asset_type, custody_status, encrypted_payload) VALUES (?, ?, ?, ?)", vault_records)

    conn.commit()
    conn.close()

def ensure_stage1_db_ready():
    target_path = get_stage1_db_path()
    if not os.path.exists(target_path):
        sibling_db = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stage4_client_portal", "cybervault.db")
        if os.path.exists(sibling_db):
            try:
                shutil.copy2(sibling_db, target_path)
                return
            except Exception:
                pass
        init_stage1_db(target_path)

def get_stage1_db_connection():
    ensure_stage1_db_ready()
    conn = sqlite3.connect(get_stage1_db_path())
    conn.row_factory = sqlite3.Row
    return conn

ensure_stage1_db_ready()

CAREERS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Careers & Opportunities | CyberVault Technologies</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0e17;
            --bg-secondary: #111827;
            --bg-card: rgba(17, 24, 39, 0.85);
            --border-color: rgba(56, 189, 248, 0.2);
            --border-hover: rgba(56, 189, 248, 0.5);
            --accent-cyan: #38bdf8;
            --accent-blue: #3b82f6;
            --accent-emerald: #10b981;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(56, 189, 248, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(59, 130, 246, 0.08) 0%, transparent 40%);
        }
        header {
            border-bottom: 1px solid var(--border-color);
            background: rgba(10, 14, 23, 0.8);
            backdrop-filter: blur(12px);
            position: sticky;
            top: 0;
            z-index: 50;
        }
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 700;
            font-size: 1.25rem;
            letter-spacing: -0.02em;
            color: #fff;
            text-decoration: none;
        }
        .brand-badge {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            padding: 0.35rem 0.65rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
            box-shadow: 0 0 15px rgba(2, 132, 199, 0.4);
        }
        nav a {
            color: var(--text-secondary);
            text-decoration: none;
            margin-left: 1.75rem;
            font-size: 0.95rem;
            font-weight: 500;
            transition: color 0.2s;
        }
        nav a:hover, nav a.active {
            color: var(--accent-cyan);
        }
        nav .btn-login {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: #ffffff !important;
            padding: 0.45rem 1.15rem;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.9rem;
            box-shadow: 0 0 14px rgba(2, 132, 199, 0.35);
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }
        nav .btn-login:hover {
            background: linear-gradient(135deg, #0369a1, #1d4ed8);
            box-shadow: 0 0 20px rgba(2, 132, 199, 0.6);
            transform: translateY(-1px);
            color: #ffffff !important;
        }
        .hero {
            max-width: 1200px;
            margin: 3rem auto 2rem;
            padding: 0 2rem;
            text-align: center;
        }
        .badge {
            display: inline-block;
            padding: 0.35rem 1rem;
            border-radius: 9999px;
            background: rgba(56, 189, 248, 0.1);
            color: var(--accent-cyan);
            border: 1px solid rgba(56, 189, 248, 0.3);
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 1rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        h1 {
            font-size: 2.75rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #ffffff 30%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            color: var(--text-secondary);
            font-size: 1.15rem;
            max-width: 650px;
            margin: 0 auto;
        }
        .content {
            max-width: 1100px;
            margin: 2.5rem auto 4rem;
            padding: 0 2rem;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        .job-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.75rem;
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
            transition: transform 0.2s, border-color 0.2s;
        }
        .job-card:hover {
            border-color: var(--border-hover);
            transform: translateY(-2px);
        }
        .job-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        .job-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #fff;
        }
        .job-meta {
            display: flex;
            gap: 0.75rem;
            font-size: 0.85rem;
        }
        .meta-tag {
            background: rgba(255, 255, 255, 0.05);
            padding: 0.25rem 0.65rem;
            border-radius: 6px;
            color: var(--text-secondary);
            border: 1px solid rgba(255,255,255,0.08);
        }
        .job-desc {
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-bottom: 1.25rem;
        }
        .requirements-list {
            margin-left: 1.25rem;
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-bottom: 1.25rem;
        }
        .requirements-list li { margin-bottom: 0.35rem; }
        code {
            background: rgba(56, 189, 248, 0.08);
            border: 1px solid rgba(56, 189, 248, 0.25);
            padding: 0.15rem 0.45rem;
            border-radius: 6px;
            color: var(--accent-cyan);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9em;
        }
        .internal-notice {
            background: rgba(15, 23, 42, 0.8);
            border-left: 4px solid var(--accent-cyan);
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            font-size: 0.88rem;
            color: #e2e8f0;
            font-family: 'JetBrains Mono', monospace;
            margin-top: 1rem;
        }
        .internal-notice strong {
            color: var(--accent-cyan);
        }
        .hint-box {
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.25);
            padding: 1.25rem;
            border-radius: 10px;
            margin-top: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
        }
        .hint-box p {
            color: #a7f3d0;
            font-size: 0.9rem;
        }
        .btn-inspect {
            background: linear-gradient(135deg, #0284c7, #0284c7);
            color: #fff;
            padding: 0.6rem 1.2rem;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: opacity 0.2s;
            white-space: nowrap;
        }
        .btn-inspect:hover { opacity: 0.9; }
        footer {
            border-top: 1px solid var(--border-color);
            padding: 2rem;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.875rem;
        }
    </style>
</head>
<body>
    <header>
        <div class="nav-container">
            <a href="/" class="brand">
                <span class="brand-badge">CVT</span>
                CyberVault Technologies
            </a>
            <nav>
                <a href="/" class="active">Careers</a>
                <a href="/social">Public Feed</a>
                <a href="/login" class="btn-login">Login</a>
            </nav>
        </div>
    </header>

    <div class="hero">
        <span class="badge">Open Roles &bull; Join the Shield</span>
        <h1>Building the Future of Digital Custody</h1>
        <p class="subtitle">CyberVault Technologies safeguards billions in tier-1 institutional digital assets across distributed high-availability enclaves.</p>
    </div>

    <div class="content">
        <!-- Position 1 -->
        <div class="job-card">
            <div class="job-header">
                <div class="job-title">Senior DevOps & Cloud Enclave Engineer</div>
                <div class="job-meta">
                    <span class="meta-tag">Infrastructure</span>
                    <span class="meta-tag">Remote / Colombo</span>
                    <span class="meta-tag">Full-time</span>
                </div>
            </div>
            <p class="job-desc">
                We are looking for a Senior DevOps & Cloud Enclave Engineer to help us expand our next-generation secure cloud platform.
                You will work closely with our security and platform teams to build and maintain isolated environments for development,
                testing, and deployment.
            </p>
            <ul class="requirements-list">
                <li>5+ years of experience with Linux, Docker, and Kubernetes in secure environments.</li>
                <li>Strong knowledge of network segmentation, zero-trust architectures, and TLS termination.</li>
                <li>Experience setting up and managing staging environments for new services.</li>
            </ul>
            <p class="job-desc">
                As part of our infrastructure expansion, we are currently setting up a new staging environment for our internal vault services.<br>
                Engineers will be working with the staging server under our company domain: <code>cybervaulttech.com</code>
            </p>
            <div class="internal-notice">
                <strong>[DevOps Notice - Sprint 42]:</strong> The staging environment is now live. Please use the use the staging server for all testing and validation before deploying to production. Do not push any builds directly to the production vault. Access and testing should be done via the specified staging hostname only.
            </div>
        </div>

        <!-- Position 2 -->
        <div class="job-card">
            <div class="job-header">
                <div class="job-title">Cryptographic Systems Architect</div>
                <div class="job-meta">
                    <span class="meta-tag">Cryptography</span>
                    <span class="meta-tag">Hybrid</span>
                    <span class="meta-tag">Full-time</span>
                </div>
            </div>
            <p class="job-desc">
                Lead the architecture of our multi-party computation (MPC) key shards and quantum-resistant cold storage isolation layers.
            </p>
            <ul class="requirements-list">
                <li>Strong mathematical grounding in modern symmetric ciphers and public-key infrastructure.</li>
                <li>Experience analyzing cryptographic failure modes, cipher rotation procedures, and metadata leakage vectors.</li>
            </ul>
        </div>

        <!-- Position 3 -->
        <div class="job-card">
            <div class="job-header">
                <div class="job-title">Web Application Security Specialist</div>
                <div class="job-meta">
                    <span class="meta-tag">Application Security</span>
                    <span class="meta-tag">Colombo</span>
                    <span class="meta-tag">Full-time</span>
                </div>
            </div>
            <p class="job-desc">
                Audit our customer-facing asset portals, APIs, and authentication endpoints against OWASP Top 10 vulnerabilities (SQLi, Auth Bypass, IDOR).
            </p>
            <ul class="requirements-list">
                <li>Hands-on penetration testing experience across web applications and identity gateways.</li>
                <li>Familiarity with SQL query parametrization and defensive audit logging trails.</li>
            </ul>
    </div>

    <footer>
        &copy; 2026 CyberVault Technologies Inc. All rights reserved.
    </footer>
</body>
</html>
"""

SOCIAL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Developer Updates | CyberVault Technologies</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0e17;
            --bg-secondary: #111827;
            --bg-card: rgba(17, 24, 39, 0.9);
            --border-color: rgba(56, 189, 248, 0.2);
            --accent-cyan: #38bdf8;
            --accent-blue: #3b82f6;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
            background-image: 
                radial-gradient(circle at 80% 20%, rgba(56, 189, 248, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.08) 0%, transparent 40%);
        }
        header {
            border-bottom: 1px solid var(--border-color);
            background: rgba(10, 14, 23, 0.8);
            backdrop-filter: blur(12px);
            position: sticky;
            top: 0;
            z-index: 50;
        }
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 700;
            font-size: 1.25rem;
            color: #fff;
            text-decoration: none;
        }
        .brand-badge {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            padding: 0.35rem 0.65rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        nav a {
            color: var(--text-secondary);
            text-decoration: none;
            margin-left: 1.75rem;
            font-size: 0.95rem;
            font-weight: 500;
        }
        nav a:hover, nav a.active { color: var(--accent-cyan); }
        nav .btn-login {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: #ffffff !important;
            padding: 0.45rem 1.15rem;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.9rem;
            box-shadow: 0 0 14px rgba(2, 132, 199, 0.35);
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }
        nav .btn-login:hover {
            background: linear-gradient(135deg, #0369a1, #1d4ed8);
            box-shadow: 0 0 20px rgba(2, 132, 199, 0.6);
            transform: translateY(-1px);
            color: #ffffff !important;
        }
        .feed-container {
            max-width: 720px;
            margin: 3rem auto;
            padding: 0 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        .feed-header {
            text-align: center;
            margin-bottom: 1rem;
        }
        .feed-header h1 {
            font-size: 2rem;
            font-weight: 800;
        }
        .post-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .post-author {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        }
        .avatar {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: linear-gradient(135deg, #0ea5e9, #6366f1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: #fff;
        }
        .author-details h4 { font-size: 1rem; color: #fff; }
        .author-details span { font-size: 0.8rem; color: var(--text-muted); }
        .post-body {
            color: #e2e8f0;
            font-size: 0.95rem;
            margin-bottom: 1rem;
        }
        .highlight {
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent-cyan);
            padding: 0.15rem 0.35rem;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
        }
        .post-tags {
            display: flex;
            gap: 0.5rem;
            font-size: 0.8rem;
            color: var(--accent-blue);
        }
        .post-image-container {
            margin: 1rem 0;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid rgba(56, 189, 248, 0.2);
            background: #030712;
            text-align: center;
        }
        .post-image {
            max-width: 100%;
            max-height: 460px;
            height: auto;
            display: inline-block;
            border-radius: 6px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            transition: transform 0.25s ease;
        }
        .post-image:hover {
            transform: scale(1.015);
        }
    </style>
</head>
<body>
    <header>
        <div class="nav-container">
            <a href="/" class="brand">
                <span class="brand-badge">CVT</span>
                CyberVault Technologies
            </a>
            <nav>
                <a href="/">Careers</a>
                <a href="/social" class="active">Public Feed</a>
                <a href="/login" class="btn-login">Login</a>
            </nav>
        </div>
    </header>

    <div class="feed-container">
        <div class="feed-header">
            <h1>Engineering Social Stream</h1>
            <p style="color:var(--text-secondary); font-size:0.95rem;">Real-time development updates from our engineering crew</p>
        </div>

        <div class="post-card">
            <div class="post-author">
                <div class="avatar">AR</div>
                <div class="author-details">
                    <h4>Alex Rivera</h4>
                    <span>@arivera_dev &bull; Principal DevOps Engineer &bull; 2h ago</span>
                </div>
            </div>
            <div class="post-body">
                Migration milestone accomplished! Decommissioned that pesky legacy cluster <span class="highlight">vault-legacy-01</span> for good this morning. All staging validation runs are now pointed squarely at <span class="highlight">vault-staging.cybervaulttech.com</span>! Huge props to the infrastructure team for zero downtime during cutover! 🚀🔐
            </div>
            <div class="post-tags">
                <span>#DevOps</span>
                <span>#CloudInfra</span>
                <span>#ZeroTrust</span>
                <span>#CyberVault</span>
            </div>
        </div>

        <div class="post-card">
            <div class="post-author">
                <div class="avatar" style="background: linear-gradient(135deg, #0284c7, #38bdf8);">AR</div>
                <div class="author-details">
                    <h4>Alex Rivera</h4>
                    <span>@arivera_dev &bull; Principal DevOps Engineer &bull; 45m ago</span>
                </div>
            </div>
            <div class="post-body">
                Fresh branding deployed for our internal staging diagnostics dashboard! 🏛️ In honor of our upcoming classic cryptography drills and key rotation protocols, we've set William Shakespeare's <em>Julius Caesar</em> as our updated staging asset. Remember team: <em>"Experience is the teacher of all things."</em> Keep your ciphers rotated and audit your asset metadata! 🔐📖
            </div>
            <div class="post-image-container">
                <img src="/static/julius_caesar.jpg" alt="William Shakespeare Julius Caesar - Staging Asset" class="post-image" />
            </div>
            <div class="post-tags">
                <span>#DevOps</span>
                <span>#JuliusCaesar</span>
                <span>#ClassicalCrypto</span>
                <span>#CyberVault</span>
                <span>#StagingDiagnostics</span>
            </div>
        </div>

        <div class="post-card">
            <div class="post-author">
                <div class="avatar">SM</div>
                <div class="author-details">
                    <h4>Sarah Miller</h4>
                    <span>@smiller_sec &bull; Security Operations &bull; 1d ago</span>
                </div>
            </div>
            <div class="post-body">
                Reminder for all staff: Passive reconnaissance assessments have kicked off. Ensure all metadata on public assets is sanitized before uploading to public repositories or CDNs. Stay vigilant!
            </div>
            <div class="post-tags">
                <span>#SecOps</span>
                <span>#InformationSecurity</span>
            </div>
        </div>
    </div>

    <script>
        function verifyHostname() {
            const val = document.getElementById('hostInput').value.trim();
            const res = document.getElementById('resultBox');
            if (!val) return;

            fetch('/api/verify', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ hostname: val })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    res.className = 'result success';
                    res.innerHTML = `<strong>ACCESS GRANTED:</strong> Host confirmed active.<br>` +
                                    `<strong>SECURITY FLAG:</strong> <code>${data.flag}</code><br>` +
                                    `<span style="display:inline-block; margin-top:0.5rem;"><a href="${data.next_target}" target="_blank" style="color:#10b981; font-weight:bold;">&rarr; Access Internal Host (${data.next_target})</a></span>`;
                } else {
                    res.className = 'result error';
                    res.innerHTML = `<strong>FAILED:</strong> ${data.message}`;
                }
            })
            .catch(e => {
                res.className = 'result error';
                res.innerHTML = 'Error communicating with validation server.';
            });
        }
    </script>
</body>
</html>
"""

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyberVault | Enterprise Custody Portal</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0a0e17;
            --card-bg: #111827;
            --card-border: #1f293d;
            --accent-cyan: #00f2fe;
            --accent-teal: #4facfe;
            --text-main: #e2e8f0;
            --text-muted: #94a3b8;
            --danger: #ef4444;
            --success: #10b981;
            --glow: 0 0 20px rgba(0, 242, 254, 0.25);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
            background-image: 
                radial-gradient(circle at 15% 20%, rgba(79, 172, 254, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 85% 80%, rgba(0, 242, 254, 0.08) 0%, transparent 40%);
        }

        .container {
            width: 100%;
            max-width: 480px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .badge {
            display: inline-block;
            background: rgba(0, 242, 254, 0.1);
            color: var(--accent-cyan);
            border: 1px solid rgba(0, 242, 254, 0.3);
            border-radius: 9999px;
            padding: 4px 14px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 12px;
            font-family: 'Fira Code', monospace;
        }

        .title {
            font-size: 1.85rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }

        .subtitle {
            font-size: 0.9rem;
            color: var(--text-muted);
        }

        .card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 32px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), var(--glow);
        }

        .alert-error {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid var(--danger);
            color: #fca5a5;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 0.875rem;
            font-family: 'Fira Code', monospace;
            word-break: break-all;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-muted);
            letter-spacing: 0.02em;
        }

        input[type="text"],
        input[type="password"] {
            width: 100%;
            background: #0d131f;
            border: 1px solid #2d3748;
            border-radius: 8px;
            padding: 12px 14px;
            color: #fff;
            font-family: 'Fira Code', monospace;
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s ease;
        }

        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: var(--accent-cyan);
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.25);
        }

        .btn-submit {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: linear-gradient(135deg, var(--accent-teal) 0%, var(--accent-cyan) 100%);
            color: #050c18;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
        }

        .btn-submit:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(0, 242, 254, 0.45);
        }

        .portal-link-box {
            margin-top: 20px;
            padding: 12px 14px;
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid #1e293b;
            border-radius: 8px;
            text-align: center;
            font-size: 0.82rem;
            color: #94a3b8;
        }

        .portal-link-box a {
            color: var(--accent-teal);
            text-decoration: none;
            font-weight: 600;
        }

        .portal-link-box a:hover {
            text-decoration: underline;
        }

        .footer {
            margin-top: 24px;
            text-align: center;
            font-size: 0.78rem;
            color: #64748b;
        }

        /* Success Flag Popup Modal */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(4, 8, 16, 0.88);
            backdrop-filter: blur(8px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            animation: fadeIn 0.25s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .modal-box {
            background: #111827;
            border: 2px solid var(--accent-cyan);
            border-radius: 14px;
            padding: 32px 28px;
            max-width: 480px;
            width: 90%;
            text-align: center;
            box-shadow: 0 0 40px rgba(0, 242, 254, 0.35), 0 20px 50px rgba(0, 0, 0, 0.85);
            animation: slideUp 0.25s ease-out;
        }
        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .modal-badge {
            display: inline-block;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid var(--success);
            color: var(--success);
            font-size: 0.78rem;
            font-weight: 700;
            font-family: 'Fira Code', monospace;
            padding: 5px 14px;
            border-radius: 9999px;
            letter-spacing: 0.05em;
            margin-bottom: 14px;
        }
        .modal-title {
            color: #ffffff;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 8px;
        }
        .modal-desc {
            color: var(--text-muted);
            font-size: 0.88rem;
            line-height: 1.5;
            margin-bottom: 20px;
        }
        .flag-container {
            background: #090e17;
            border: 1px dashed var(--accent-cyan);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 18px;
        }
        .flag-label {
            display: block;
            font-size: 0.72rem;
            color: var(--accent-teal);
            letter-spacing: 0.1em;
            font-weight: 600;
            margin-bottom: 6px;
        }
        .flag-value {
            color: #00f2fe;
            font-family: 'Fira Code', monospace;
            font-size: 1.18rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            user-select: all;
            word-break: break-all;
            text-shadow: 0 0 12px rgba(0, 242, 254, 0.5);
        }
        .user-meta {
            font-size: 0.82rem;
            color: var(--text-muted);
            margin-bottom: 22px;
            font-family: 'Fira Code', monospace;
        }
        .user-meta strong {
            color: #fff;
        }
        .btn-modal-ok {
            background: linear-gradient(135deg, var(--accent-teal) 0%, var(--accent-cyan) 100%);
            color: #050c18;
            border: none;
            padding: 12px 42px;
            font-size: 1rem;
            font-weight: 700;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 4px 18px rgba(0, 242, 254, 0.35);
            transition: all 0.15s ease;
        }
        .btn-modal-ok:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 24px rgba(0, 242, 254, 0.55);
        }

        /* ─── Caesar Bottom-Right Popup Message ──────────────────────────────── */
        .caesar-popup {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 440px;
            max-width: calc(100vw - 32px);
            max-height: 520px;
            background: rgba(10, 17, 34, 0.96);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(0, 242, 254, 0.35);
            border-radius: 12px;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.75), 0 0 25px rgba(0, 242, 254, 0.18);
            display: flex;
            flex-direction: column;
            z-index: 10001;
            opacity: 0;
            transform: translateY(30px) scale(0.96);
            transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1), transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
            pointer-events: none;
            overflow: hidden;
        }

        .caesar-popup.show {
            opacity: 1;
            transform: translateY(0) scale(1);
            pointer-events: auto;
        }

        .caesar-popup-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px;
            background: rgba(15, 26, 52, 0.9);
            border-bottom: 1px solid rgba(0, 242, 254, 0.2);
        }

        .caesar-sender-box {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .caesar-avatar {
            font-size: 1.25rem;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            background: rgba(0, 242, 254, 0.12);
            border: 1px solid rgba(0, 242, 254, 0.3);
            border-radius: 8px;
        }

        .caesar-sender-meta {
            display: flex;
            flex-direction: column;
        }

        .caesar-sender-name {
            font-size: 0.95rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            color: #00f2fe;
            font-family: 'Fira Code', monospace;
            text-shadow: 0 0 10px rgba(0, 242, 254, 0.4);
        }

        .caesar-actions {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .caesar-btn-copy {
            background: rgba(0, 242, 254, 0.12);
            border: 1px solid rgba(0, 242, 254, 0.3);
            color: #00f2fe;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 4px 9px;
            border-radius: 5px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.2s ease;
            font-family: inherit;
        }

        .caesar-btn-copy:hover {
            background: rgba(0, 242, 254, 0.22);
            border-color: #00f2fe;
            color: #ffffff;
        }

        .caesar-btn-close {
            background: transparent;
            border: none;
            color: #94a3b8;
            font-size: 1.4rem;
            line-height: 1;
            cursor: pointer;
            padding: 0 4px;
            transition: color 0.2s ease;
        }

        .caesar-btn-close:hover {
            color: #f87171;
        }

        .caesar-popup-body {
            padding: 14px 16px;
            overflow-y: auto;
            max-height: 420px;
        }

        .caesar-memo-text {
            font-family: 'Fira Code', monospace;
            font-size: 0.8rem;
            line-height: 1.55;
            color: #e2e8f0;
            white-space: pre-wrap;
            word-break: break-word;
            background: rgba(3, 7, 18, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 12px;
            margin: 0;
            user-select: text;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="badge">Stage 4 // Web Application Security</span>
            <h1 class="title">CyberVault Technologies</h1>
            <p class="subtitle">Secure Digital Asset Custody Portal</p>
        </div>

        <div class="card">
            <div class="alert-error" id="errorMsg" style="{% if not error %}display:none;{% endif %}">
                [!] Authentication Failed: <span id="errorText">{{ error or '' }}</span>
            </div>

            <form action="/login" method="POST" id="loginForm">
                <div class="form-group">
                    <label for="username">OPERATOR USERNAME</label>
                    <input type="text" id="username" name="username" placeholder="user name" required autofocus autocomplete="off">
                </div>

                <div class="form-group">
                    <label for="password">AUTHENTICATION PASSCODE</label>
                    <input type="password" id="password" name="password" placeholder="password" required>
                </div>

                <button type="submit" class="btn-submit" id="loginBtn">Authenticate to Vault</button>
            </form>

            <div class="portal-link-box">
                <a href="/">&larr; Return to Careers Page</a>
            </div>
        </div>

        <div class="footer">
            CyberVault Security Node 10.0.4.15 &bull; Authorized Penetration Testing Environment
        </div>
    </div>

    <!-- Success Flag Popup Modal with OK Button -->
    <div id="flagModal" class="modal-overlay" style="{% if not flag %}display: none;{% endif %}">
        <div class="modal-box">
            <div class="modal-badge">&#10004; SQL INJECTION BYPASS SUCCESSFUL</div>
            <h2 class="modal-title">Authentication Compromised!</h2>
            <p class="modal-desc">
                You successfully bypassed authentication using SQL injection! Here is your security challenge flag:
            </p>

            <div class="flag-container">
                <span class="flag-label">CAPTURE THE FLAG</span>
                <div class="flag-value" id="flagText">{{ flag or 'CVT{sql1_byp4ss_v4ult_4dm1n}' }}</div>
            </div>

            <div class="user-meta" id="userMeta" style="{% if not user %}display:none;{% endif %}">
                Authenticated Identity: <strong id="userIdentity">{{ user.username if user else 'admin' }}</strong>
                (<span id="userRole">{{ user.role if user else 'vault_administrator' }}</span>)
            </div>

            <button type="button" class="btn-modal-ok" id="btnModalOk" onclick="closeFlagModal()">OK</button>
        </div>
    </div>

    <!-- Caesar Encrypted Memo Bottom-Right Popup (Shown after login) -->
    <div id="caesarMemoPopup" class="caesar-popup" role="dialog" aria-live="polite">
        <div class="caesar-popup-header">
            <div class="caesar-sender-box">
                <span class="caesar-avatar">🏛️</span>
                <div class="caesar-sender-meta">
                    <span class="caesar-sender-name">CAESAR</span>
                </div>
            </div>
            <div class="caesar-actions">
                <button type="button" class="caesar-btn-copy" id="caesarCopyBtn" title="Copy Memo Text" onclick="copyCaesarMemo()">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                    Copy
                </button>
                <button type="button" class="caesar-btn-close" title="Dismiss Message" onclick="dismissCaesarPopup()">&times;</button>
            </div>
        </div>
        <div class="caesar-popup-body">
            <pre class="caesar-memo-text" id="caesarMemoContent">Paxg ebyx zxml xgvkrimxw, cnlm KHMtmx rhnk ikhuexfl tptr. By max xqiehbm ytbel, vtee bm t yxtmnkx tgw mkr tztbg. Kxfxfuxk, kxte atvdxkl gxoxk zbox ni, maxr cnlm Zhhzex atkwxk.

VOM{v43l4k_la1ym_d3r_k0m4m10g_9173}</pre>
        </div>
    </div>

    <script>
        function showCaesarPopup() {
            setTimeout(function() {
                const popup = document.getElementById('caesarMemoPopup');
                if (popup) {
                    popup.classList.add('show');
                }
            }, 300);
        }

        function dismissCaesarPopup() {
            const popup = document.getElementById('caesarMemoPopup');
            if (popup) {
                popup.classList.remove('show');
            }
        }

        function copyCaesarMemo() {
            const memo = document.getElementById('caesarMemoContent');
            if (!memo) return;
            const text = memo.innerText;
            navigator.clipboard.writeText(text).then(function() {
                const btn = document.getElementById('caesarCopyBtn');
                if (btn) {
                    const original = btn.innerHTML;
                    btn.innerHTML = '✓ Copied!';
                    btn.style.color = '#34d399';
                    setTimeout(function() {
                        btn.innerHTML = original;
                        btn.style.color = '';
                    }, 2000);
                }
            }).catch(function() {
                const range = document.createRange();
                range.selectNodeContents(memo);
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
            });
        }

        {% if flag %}
        showCaesarPopup();
        {% endif %}

        function closeFlagModal() {
            const modal = document.getElementById('flagModal');
            if (modal) {
                modal.style.display = 'none';
            }
            const nextUrl = window.STAGE5_TARGET_URL || '{{ stage5_url or "/forensics" }}';
            window.location.href = nextUrl;
        }

        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorMsg = document.getElementById('errorMsg');
            const errorText = document.getElementById('errorText');
            const loginBtn = document.getElementById('loginBtn');

            loginBtn.disabled = true;
            loginBtn.innerText = 'Authenticating...';

            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            fetch('/login', {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(r => r.json())
            .then(data => {
                loginBtn.disabled = false;
                loginBtn.innerText = 'Authenticate to Vault';

                if (data.success) {
                    errorMsg.style.display = 'none';
                    document.getElementById('flagText').innerText = data.flag;
                    if (data.user) {
                        document.getElementById('userMeta').style.display = 'block';
                        document.getElementById('userIdentity').innerText = data.user;
                        document.getElementById('userRole').innerText = data.role || 'vault_administrator';
                    }
                    if (data.next_url) {
                        window.STAGE5_TARGET_URL = data.next_url;
                    }
                    document.getElementById('flagModal').style.display = 'flex';
                    showCaesarPopup();
                } else {
                    errorText.innerText = data.error || 'Invalid credentials.';
                    errorMsg.style.display = 'block';
                }
            })
            .catch(err => {
                loginBtn.disabled = false;
                loginBtn.innerText = 'Authenticate to Vault';
                errorText.innerText = 'Network error during authentication attempt.';
                errorMsg.style.display = 'block';
            });
        });
    </script>
</body>
</html>
"""

ROBOTS_TXT = """User-agent: *
Disallow: /internal/
Disallow: /staging-enclave/
# Security Note: Public assets strictly under *.cybervaulttech.com
# Staging endpoints must remain unlinked from root navigation
"""

# ============================================================================
# Flask Application Routes (WSGI / Vercel Serverless Ready)
# ============================================================================

@app.route("/", methods=["GET", "POST"])
@app.route("/careers", methods=["GET", "POST"])
@app.route("/api/index", methods=["GET", "POST"])
@app.route("/api/index.py", methods=["GET", "POST"])
def careers():
    # Dispatch when Vercel rewrites requests to /api/index?path=...
    target_path = request.args.get("path", "").strip()
    if target_path:
        clean_path = target_path.rstrip("/") if target_path != "/" else "/"
        if not clean_path.startswith("/"):
            clean_path = "/" + clean_path

        if clean_path in ("/social",):
            return social()
        elif clean_path in ("/robots.txt",):
            return robots()
        elif clean_path in ("/login",):
            return login()
        elif clean_path in ("/api/login",):
            return api_login()
        elif clean_path in ("/api/status",):
            return api_status()
        elif clean_path in ("/api/verify",):
            return api_verify()
        elif clean_path.startswith("/static/"):
            filename = clean_path[len("/static/"):].lstrip("/")
            return serve_static(filename)
        elif clean_path in ("/julius_caesar.jpg",):
            return serve_static("julius_caesar.jpg")
        elif clean_path in ("/forensics", "/stage5", "/access-logs"):
            return stage5_forensics_view()
        elif clean_path in ("/api/logs/raw",):
            return download_stage5_raw()
        elif clean_path in ("/api/logs",):
            return get_stage5_logs_json()
        elif clean_path in ("/api/validate-flag",):
            return validate_stage5_flag()
        elif clean_path in ("/api/users",):
            return get_stage5_users()
        elif clean_path in ("/health",):
            return stage5_health()
        elif clean_path in ("/reset",):
            return stage5_reset()
        elif clean_path in ("/", "/careers"):
            pass
        else:
            return Response("404 Not Found", status=404, mimetype="text/plain")

    try:
        content = render_template("careers.html")
    except Exception:
        content = CAREERS_HTML
    resp = Response(content, mimetype="text/html; charset=utf-8")
    resp.headers["X-Challenge-Stage"] = "1-OSINT-Recon"
    return resp


@app.route("/social")
def social():
    try:
        content = render_template("social.html")
    except Exception:
        content = SOCIAL_HTML
    resp = Response(content, mimetype="text/html; charset=utf-8")
    resp.headers["X-Challenge-Stage"] = "1-OSINT-Recon"
    return resp


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    flag = None
    authenticated_user = None

    if request.method == "POST":
        if request.is_json:
            data = request.get_json(silent=True) or {}
            username = str(data.get("username", "")).strip()
            password = str(data.get("password", "")).strip()
        else:
            username = str(request.form.get("username", "")).strip()
            password = str(request.form.get("password", "")).strip()

        if not username:
            error = "Username is required."
            if request.is_json or request.headers.get("Accept") == "application/json":
                return jsonify({"success": False, "error": error}), 400
            try:
                return render_template("login.html", error=error)
            except Exception:
                return Response(LOGIN_HTML.replace("{% if not error %}display:none;{% endif %}", "").replace("{{ error or '' }}", error), mimetype="text/html; charset=utf-8")

        conn = get_stage1_db_connection()
        cursor = conn.cursor()

        # Intentionally vulnerable raw string concatenation SQL query (Stage 4 SQLi)
        raw_query = f"SELECT id, username, role, full_name, email FROM users WHERE username = '{username}' AND password = '{password}'"
        print(f"[STAGE 1 - SQLi PORTAL AUDIT] Executing SQL Query: {raw_query}")

        try:
            cursor.execute(raw_query)
            user = cursor.fetchone()

            if user:
                authenticated_user = dict(user)
                flag = STAGE4_FLAG
                if request.is_json or request.headers.get("Accept") == "application/json":
                    return jsonify({
                        "success": True,
                        "message": "Authentication successful via SQL injection bypass!",
                        "user": user["username"],
                        "role": user["role"],
                        "flag": STAGE4_FLAG,
                        "next_url": STAGE5_URL
                    }), 200
            else:
                error = "Invalid username or password. Access denied."
                if request.is_json or request.headers.get("Accept") == "application/json":
                    return jsonify({"success": False, "error": error}), 401
        except sqlite3.OperationalError as e:
            # SQL syntax error leaked, typical in vulnerable pentesting targets
            error = f"SQL Database Syntax Error: {str(e)}"
            if request.is_json or request.headers.get("Accept") == "application/json":
                return jsonify({"success": False, "error": error}), 400
        finally:
            conn.close()

    try:
        content = render_template("login.html", error=error, flag=flag, user=authenticated_user, stage5_url=STAGE5_URL)
    except Exception:
        content = LOGIN_HTML
        if error:
            content = content.replace("{% if not error %}display:none;{% endif %}", "").replace("{{ error or '' }}", error)
        if flag:
            content = content.replace("{% if not flag %}display: none;{% endif %}", "display: flex;").replace("{{ flag or 'CVT{sql1_byp4ss_v4ult_4dm1n}' }}", flag)
        if authenticated_user:
            content = content.replace("{% if not user %}display:none;{% endif %}", "display: block;").replace("{{ user.username if user else 'admin' }}", authenticated_user.get("username", "admin")).replace("{{ user.role if user else 'vault_administrator' }}", authenticated_user.get("role", "vault_administrator"))
    resp = Response(content, mimetype="text/html; charset=utf-8")
    resp.headers["X-Challenge-Stage"] = "1-OSINT-Recon-SQLi"
    return resp


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or request.form
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    conn = get_stage1_db_connection()
    cursor = conn.cursor()
    raw_query = f"SELECT id, username, role, full_name, email FROM users WHERE username = '{username}' AND password = '{password}'"
    print(f"[STAGE 1 - SQLi API AUDIT] Executing SQL Query: {raw_query}")

    try:
        cursor.execute(raw_query)
        user = cursor.fetchone()
        if user:
            return jsonify({
                "success": True,
                "message": "Authentication successful via SQL injection bypass!",
                "user": user["username"],
                "role": user["role"],
                "flag": STAGE4_FLAG,
                "next_url": STAGE5_URL
            }), 200
        else:
            return jsonify({"success": False, "error": "Invalid credentials"}), 401
    except sqlite3.OperationalError as e:
        return jsonify({"success": False, "error": f"SQL Error: {str(e)}"}), 400
    finally:
        conn.close()

@app.route("/robots.txt")
def robots():
    return Response(ROBOTS_TXT, mimetype="text/plain; charset=utf-8")

@app.route("/static/<path:filename>")
@app.route("/julius_caesar.jpg")
def serve_static(filename="julius_caesar.jpg"):
    candidates = [
        STATIC_DIR,
        os.path.join(BASE_DIR, "public", "static"),
        os.path.join(BASE_DIR, "public"),
        os.path.join(os.getcwd(), "static"),
        os.path.join(os.getcwd(), "public", "static"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
    ]
    for directory in candidates:
        if os.path.isdir(directory):
            target = os.path.join(directory, filename)
            if os.path.isfile(target):
                mimetype = "image/jpeg" if filename.lower().endswith((".jpg", ".jpeg")) else None
                return send_from_directory(directory, filename, mimetype=mimetype)
    return Response("404 Not Found", status=404, mimetype="text/plain")

@app.route("/api/status")
def api_status():
    return jsonify({
        "stage": 1,
        "domain": "OSINT / Reconnaissance",
        "status": "online",
        "challenge": "The Careers Page Slip-Up"
    })

@app.route("/api/verify", methods=["POST"])
def api_verify():
    data = request.get_json(silent=True) or {}
    submitted = str(data.get("hostname", "")).strip().lower()

    if submitted == CORRECT_HOSTNAME:
        res = {
            "success": True,
            "flag": STAGE1_FLAG,
            "message": "Correct active staging host identified!",
            "next_target": STAGE2_URL
        }
    elif submitted == DECOY_HOSTNAME or "vault-legacy" in submitted:
        res = {
            "success": False,
            "message": "Decoy hostname identified! Notice that vault-legacy-01 is explicitly retired. Find the active staging host."
        }
    else:
        res = {
            "success": False,
            "message": f"Incorrect hostname '{submitted}'. Look closely at the DevOps and employee posts for the active *.cybervaulttech.com hostname."
        }
    return jsonify(res)

# ============================================================================
# Stage 5: Forensic Access Log Analysis (Embedded in Stage 1)
# ============================================================================

@app.route("/forensics")
@app.route("/stage5")
@app.route("/access-logs")
def stage5_forensics_view():
    lines = read_stage5_logs()
    failed_401_count = sum(1 for line in lines if " 401 " in line and ATTACKER_IP in line)
    return render_template(
        "forensics.html",
        log_lines=lines,
        total_lines=len(lines),
        failed_count=failed_401_count,
        attacker_ip=ATTACKER_IP,
        stage6_info=STAGE6_SSH_INFO,
        port_label="Embedded Stage 5 Online"
    )

@app.route("/api/logs/raw")
def download_stage5_raw():
    log_path = get_stage5_log_path()
    if os.path.exists(log_path):
        return send_file(log_path, mimetype="text/plain", as_attachment=True, download_name="audit_access.log")
    return Response("404 Log File Not Found", status=404, mimetype="text/plain")

@app.route("/api/logs")
def get_stage5_logs_json():
    lines = read_stage5_logs()
    return jsonify({
        "total": len(lines),
        "logs": lines
    })

@app.route("/api/validate-flag", methods=["POST"])
def validate_stage5_flag():
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
def get_stage5_users():
    return jsonify({"total": len(SYSTEM_USERS), "users": SYSTEM_USERS})

@app.route("/health")
def stage5_health():
    return jsonify({"status": "healthy", "stage": "Stage 5 - Digital Forensics"}), 200

@app.route("/reset", methods=["POST"])
def stage5_reset():
    try:
        from generate_logs import generate_log_file
        generate_log_file()
    except Exception:
        pass
    return jsonify({"status": "reset_complete", "message": "Stage 5 log file regenerated to initial state."}), 200

@app.errorhandler(404)
def not_found(e):
    return Response("404 Not Found", status=404, mimetype="text/plain")


# ============================================================================
# Legacy BaseHTTPRequestHandler (Maintained for standalone standard-lib runs)
# ============================================================================

class Stage1Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[Stage1-OSINT] {self.command} {self.path} - {args[0] if args else ''}")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ["/", "/careers"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("X-Challenge-Stage", "1-OSINT-Recon")
            self.end_headers()
            self.wfile.write(CAREERS_HTML.encode("utf-8"))

        elif path in ["/forensics", "/stage5", "/access-logs"]:
            forensics_path = os.path.join(TEMPLATE_DIR, "forensics.html")
            if os.path.exists(forensics_path):
                with open(forensics_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                lines = read_stage5_logs()
                failed_401_count = sum(1 for line in lines if " 401 " in line and ATTACKER_IP in line)
                html_content = html_content.replace("{{ total_lines }}", str(len(lines))).replace("{{ failed_count }}", str(failed_401_count))
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html_content.encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 Forensics Template Not Found")

        elif path == "/social":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("X-Challenge-Stage", "1-OSINT-Recon")
            self.end_headers()
            self.wfile.write(SOCIAL_HTML.encode("utf-8"))

        elif path == "/login":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("X-Challenge-Stage", "1-OSINT-Recon")
            self.end_headers()
            self.wfile.write(LOGIN_HTML.encode("utf-8"))

        elif path == "/robots.txt":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(ROBOTS_TXT.encode("utf-8"))

        elif path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "stage": 1,
                "domain": "OSINT / Reconnaissance",
                "status": "online",
                "challenge": "The Careers Page Slip-Up"
            }).encode("utf-8"))

        elif path.startswith("/static/") or path == "/julius_caesar.jpg":
            rel_name = "julius_caesar.jpg" if path == "/julius_caesar.jpg" else path[len("/static/"):].lstrip("/")
            candidates = [
                STATIC_DIR,
                os.path.join(BASE_DIR, "public", "static"),
                os.path.join(BASE_DIR, "public"),
                os.path.join(os.getcwd(), "static"),
            ]
            found = False
            for d in candidates:
                if os.path.isdir(d):
                    file_path = os.path.join(d, rel_name)
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            content = f.read()
                        self.send_response(200)
                        self.send_header("Content-Type", "image/jpeg")
                        self.send_header("Content-Length", str(len(content)))
                        self.end_headers()
                        self.wfile.write(content)
                        found = True
                        break
            if not found:
                self.send_response(404)
                self.end_headers()

        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/verify":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                submitted = data.get("hostname", "").strip().lower()

                if submitted == CORRECT_HOSTNAME:
                    res = {
                        "success": True,
                        "flag": STAGE1_FLAG,
                        "message": "Correct active staging host identified!",
                        "next_target": STAGE2_URL
                    }
                elif submitted == DECOY_HOSTNAME or "vault-legacy" in submitted:
                    res = {
                        "success": False,
                        "message": "Decoy hostname identified! Notice that vault-legacy-01 is explicitly retired. Find the active staging host."
                    }
                else:
                    res = {
                        "success": False,
                        "message": f"Incorrect hostname '{submitted}'. Look closely at the DevOps and employee posts for the active *.cybervaulttech.com hostname."
                    }
            except Exception as e:
                res = {"success": False, "message": f"Malformed request: {str(e)}"}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
        elif parsed.path == "/api/validate-flag":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                user_flag = str(data.get("flag", "")).strip()
                if user_flag == STAGE5_FLAG:
                    res = {
                        "valid": True,
                        "message": "Flag accepted! Access trail confirmed.",
                        "stage": 5,
                        "stage6_info": STAGE6_SSH_INFO
                    }
                    status = 200
                else:
                    res = {"valid": False, "message": "Invalid flag"}
                    status = 400
            except Exception as e:
                res = {"valid": False, "message": str(e)}
                status = 400

            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    print(f"[Stage 1] The Careers Page Slip-Up server running on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    run_server()

