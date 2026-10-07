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
from flask import Flask, render_template, request, jsonify, Response

PORT = int(os.environ.get("PORT", 8081))
STAGE1_FLAG = os.environ.get("STAGE1_FLAG", "CVT{0s1nt_st4g1ng_l34k_8291}")
STAGE2_URL = os.environ.get("STAGE2_URL", "http://localhost:8082")
CORRECT_HOSTNAME = "vault-staging.cybervaulttech.com"
DECOY_HOSTNAME = "vault-legacy-01"

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
app = Flask(__name__, template_folder=template_dir)

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
            font-size: 0.85rem;
            max-width: 1200px;
            margin: 0 auto;
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
                <a href="/robots.txt" target="_blank">robots.txt</a>
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
                We are seeking a senior infrastructure engineer to oversee deployment automation, zero-trust network policy, and container orchestration across our hybrid cloud environment.
            </p>
            <ul class="requirements-list">
                <li>5+ years managing Linux infrastructure, Docker Compose, and Kubernetes enclaves.</li>
                <li>Deep understanding of SSH bastion architecture, network micro-segmentation, and TLS termination.</li>
                <li>Experience configuring automated key rotation services and hardened backup environments.</li>
            </ul>
            <div class="internal-notice">
                <strong>[DevOps Notice - Sprint 42]:</strong> All pipeline deployments are transitioning away from legacy nodes. Do <strong>NOT</strong> attempt to push builds to the decommissioned <code>vault-legacy-01</code> node. All active testing is strictly provisioned on the dedicated staging host: <code>vault-staging.cybervaulttech.com</code>.
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
        .verify-box {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 1rem;
        }
        .verify-box h3 {
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
            color: var(--accent-cyan);
        }
        .verify-box p {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 1rem;
        }
        .form-row {
            display: flex;
            gap: 0.5rem;
        }
        input[type="text"] {
            flex: 1;
            padding: 0.7rem 1rem;
            background: #030712;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 6px;
            color: #fff;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: var(--accent-cyan);
        }
        button {
            padding: 0.7rem 1.4rem;
            background: linear-gradient(135deg, #0284c7, #2563eb);
            border: none;
            border-radius: 6px;
            color: #fff;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        button:hover { opacity: 0.9; }
        .result {
            margin-top: 1rem;
            padding: 0.75rem;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            display: none;
        }
        .result.success {
            display: block;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #34d399;
        }
        .result.error {
            display: block;
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.4);
            color: #f87171;
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
                <a href="/robots.txt" target="_blank">robots.txt</a>
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
        elif clean_path in ("/api/status",):
            return api_status()
        elif clean_path in ("/api/verify",):
            return api_verify()
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

@app.route("/robots.txt")
def robots():
    return Response(ROBOTS_TXT, mimetype="text/plain; charset=utf-8")

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

        elif path == "/social":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("X-Challenge-Stage", "1-OSINT-Recon")
            self.end_headers()
            self.wfile.write(SOCIAL_HTML.encode("utf-8"))

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
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    print(f"[Stage 1] The Careers Page Slip-Up server running on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    run_server()

