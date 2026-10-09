"""
================================================================================
CyberVault : Operation ShadowTrace - Central CTF Scoring & Submission Portal
Author: Member 3 - IT24103027 (Hettige D.R.B)
================================================================================
"""

import os
import sys
import functools
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, flash, abort
)
from dotenv import load_dotenv

# Ensure local modules can be imported
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

from db import db_manager
from crypto_vault import encrypt_flag, decrypt_flag, get_crypto_status

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = os.getenv("SECRET_KEY", "cybervault_super_secret_session_key_2026!")

# Make built-ins available in Jinja2 templates
app.jinja_env.globals.update(enumerate=enumerate, session=session, zip=zip)


# Configuration constants
PORT = int(os.getenv("PORT", 5000))
ADMIN_ROUTE_SECRET = os.getenv("ADMIN_ROUTE_SECRET", "sh4d0w_9f7a2c").strip()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "CyberVaultAdmin#2026!").strip()
TOTAL_MAX_POINTS = int(os.getenv("TOTAL_MAX_POINTS", 100))
MIN_STAGE_POINTS = int(os.getenv("MIN_STAGE_POINTS", 5))


# ------------------------------------------------------------------------------
# Context Processors & Helpers
# ------------------------------------------------------------------------------
@app.context_processor
def inject_global_vars():
    """Injects common CTF stats and current user information to all templates."""
    current_user = None
    user_score = 0.0
    user_solved_count = 0
    
    if "username" in session:
        uname = session["username"]
        current_user = db_manager.db.users.find_one({"username": uname.lower()}, {"_id": 0})
        if not current_user:
            session.pop("username", None)
            session.pop("role", None)
        else:
            prog = db_manager.get_user_progress(uname)
            user_score = sum(p.get("points_earned", 0.0) for p in prog.values() if p.get("solved"))
            user_solved_count = sum(1 for p in prog.values() if p.get("solved"))

    return {
        "current_user": current_user,
        "user_score": round(user_score, 2),
        "user_solved_count": user_solved_count,
        "total_stages_count": 6,
        "total_max_points": TOTAL_MAX_POINTS,
        "admin_secret_token": ADMIN_ROUTE_SECRET,
        "db_backend": db_manager.backend_type,
        "is_admin": session.get("is_admin", False)
    }


def login_required(view_func):
    """Decorator to protect participant routes."""
    @functools.wraps(view_func)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            flash("Please sign in or register to access operational challenges.", "warning")
            return redirect(url_for("login", next=request.path))
        user = db_manager.db.users.find_one({"username": session["username"].lower()})
        if not user:
            session.pop("username", None)
            session.pop("role", None)
            flash("Session expired. Please sign in again.", "warning")
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped


# ------------------------------------------------------------------------------
# PARTICIPANT ROUTES
# ------------------------------------------------------------------------------
@app.route("/")
@app.route("/home")
def home():
    """Event Home Page showing about the event, mission storyline, rules, and CTAs."""
    return render_template("home.html")


@app.route("/challenges")
@login_required
def challenges():
    """
    Main CTF Challenge Dashboard.
    Enforces sequential progression: Each stage unlocks only after the previous stage is solved.
    """
    all_stages = db_manager.get_all_stages()
    user_progress = db_manager.get_user_progress(session["username"])

    visible_stages = []
    for idx, s in enumerate(all_stages):
        sid = s["stage_id"]
        prog = user_progress.get(sid, {})
        s["is_solved"] = prog.get("solved", False)
        s["points_earned"] = prog.get("points_earned", 0.0)
        s["penalty_deducted"] = prog.get("penalty_deducted", 0.0)
        s["hints_unlocked"] = prog.get("hints_unlocked", [])
        
        # Hint 1 is free and shown normally
        s["user_hint1"] = s.get("hint1_text")
        # Hint 2 is only revealed when unlocked
        s["user_hint2"] = s.get("hint2_text") if 2 in s["hints_unlocked"] else None

        # Sequential unlock: Stage 1 is unlocked. Stage N is unlocked only if Stage N-1 is solved.
        if idx == 0:
            s["is_unlocked"] = True
        else:
            prev_stage = all_stages[idx - 1]
            prev_prog = user_progress.get(prev_stage["stage_id"], {})
            s["is_unlocked"] = prev_prog.get("solved", False)

        # Only display unlocked stages (completed stages + current active stage)
        if s["is_unlocked"]:
            visible_stages.append(s)

    total_stages_count = len(all_stages)
    solved_count = sum(1 for s in all_stages if user_progress.get(s["stage_id"], {}).get("solved"))
    progress_pct = round((solved_count / total_stages_count) * 100, 1) if total_stages_count else 0

    return render_template(
        "index.html",
        stages=visible_stages,
        total_stages_count=total_stages_count,
        solved_count=solved_count,
        progress_pct=progress_pct
    )


@app.route("/submit_all", methods=["GET", "POST"])
@login_required
def submit_all():
    """Redirects to main sequential challenges dashboard."""
    return redirect(url_for("challenges"))


@app.route("/submit_flag", methods=["POST"])
@login_required
def submit_flag():
    """AJAX flag validator for single stage challenge cards."""
    stage_id = request.form.get("stage_id") or request.json.get("stage_id")
    flag_val = request.form.get("flag") or request.json.get("flag", "")
    
    if not stage_id or not flag_val:
        return jsonify({"success": False, "message": "Missing Stage ID or flag input."}), 400

    try:
        sid = int(stage_id)
    except ValueError:
        return jsonify({"success": False, "message": "Invalid Stage ID."}), 400

    success, msg, pts = db_manager.submit_stage_flag(session["username"], sid, flag_val)
    
    # Recalculate user's current total score
    prog = db_manager.get_user_progress(session["username"])
    total_score = sum(p.get("points_earned", 0.0) for p in prog.values() if p.get("solved"))

    return jsonify({
        "success": success,
        "message": msg,
        "points_awarded": pts,
        "stage_id": sid,
        "new_total_score": round(total_score, 2)
    })


@app.route("/unlock_hint", methods=["POST"])
@login_required
def unlock_hint():
    """Unlocks Hint 1 (minor penalty -10%) or Hint 2 (major penalty -50%) for the logged in user."""
    stage_id = request.form.get("stage_id") or (request.json and request.json.get("stage_id"))
    hint_num = request.form.get("hint_number") or (request.json and request.json.get("hint_number"))

    if not stage_id or not hint_num:
        return jsonify({"success": False, "message": "Invalid stage or hint number."}), 400

    try:
        sid = int(stage_id)
        hnum = int(hint_num)
        if hnum not in (1, 2):
            return jsonify({"success": False, "message": "Hint number must be 1 or 2."}), 400
    except ValueError:
        return jsonify({"success": False, "message": "Parameters must be integers."}), 400

    success, msg, hint_text = db_manager.unlock_hint(session["username"], sid, hnum)
    if success:
        return jsonify({
            "success": True,
            "message": msg,
            "hint_number": hnum,
            "stage_id": sid,
            "hint_text": hint_text
        })
    else:
        return jsonify({"success": False, "message": msg}), 400


@app.route("/leaderboard")
def leaderboard():
    """Live CTF Scoreboard & Ranking Table."""
    board = db_manager.get_leaderboard()
    stages = db_manager.get_all_stages()
    recent = db_manager.get_recent_submissions(limit=10)
    return render_template("leaderboard.html", leaderboard=board, stages=stages, recent_submissions=recent)


# ------------------------------------------------------------------------------
# AUTHENTICATION ROUTES (REGISTRATION & SIGNIN)
# ------------------------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    """Participant registration form."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        full_name = request.form.get("full_name", "").strip()
        team_name = request.form.get("team_name", "").strip()

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        success, msg = db_manager.register_user(username, password, full_name, team_name)
        if success:
            session["username"] = username.lower()
            session["role"] = "participant"
            flash(f"Welcome, Cadet {username}! Registration successful.", "success")
            return redirect(url_for("challenges"))
        else:
            flash(msg, "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Participant Sign In form."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template("login.html")

        success, user_doc = db_manager.authenticate_user(username, password)
        if success:
            session["username"] = user_doc["username"]
            session["role"] = user_doc.get("role", "participant")
            flash(f"Authenticated as {user_doc['username']}! Good hunting.", "success")
            
            # Avoid redirect loop to auth pages
            next_url = request.args.get("next")
            if not next_url or "/login" in next_url or "/register" in next_url:
                next_url = url_for("challenges")
            return redirect(next_url)
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Clears participant session."""
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("home"))


# ------------------------------------------------------------------------------
# ADMIN PANEL (SECRET ROUTE & ENCRYPTED FLAG GENERATOR)
# ------------------------------------------------------------------------------
@app.route("/admin")
def deception_admin():
    """Deception endpoint: Obscured / blocked. Direct access returns 404."""
    abort(404, description="Resource not found. Administrative interface is relocated to an obscured environment token.")


@app.route(f"/{ADMIN_ROUTE_SECRET}/admin", methods=["GET", "POST"])
def admin_portal():
    """
    Secret Admin Route defined by {base}/<ADMIN_ROUTE_SECRET>/admin
    Shows Admin Login Form if unauthenticated, or Admin Management Panel if logged in.
    """
    if not session.get("is_admin"):
        # Show Admin Login Form
        if request.method == "POST":
            user = request.form.get("admin_user", "").strip()
            pwd = request.form.get("admin_pass", "").strip()
            if user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
                session["is_admin"] = True
                flash("Admin Authorization Verified. Welcome to CyberVault Command.", "success")
                return redirect(url_for("admin_portal"))
            else:
                flash("Unauthorized: Invalid administrative credentials.", "error")
        return render_template("admin_login.html", secret_token=ADMIN_ROUTE_SECRET)

    # Render authenticated Admin Management Panel
    stages = db_manager.get_all_stages(include_decrypted_for_admin=True)
    crypto_status = get_crypto_status()
    all_users = list(db_manager.db.users.find({}, {"_id": 0}))
    submissions = db_manager.get_recent_submissions(limit=30)
    total_configured_points = sum(s.get("base_points", 0) for s in stages)

    return render_template(
        "admin_panel.html",
        stages=stages,
        crypto_status=crypto_status,
        users=all_users,
        submissions=submissions,
        total_points=total_configured_points,
        secret_token=ADMIN_ROUTE_SECRET
    )


@app.route(f"/{ADMIN_ROUTE_SECRET}/admin/logout")
def admin_logout():
    """Logs out admin user."""
    session.pop("is_admin", None)
    flash("Administrative session terminated.", "info")
    return redirect(url_for("challenges"))


@app.route(f"/{ADMIN_ROUTE_SECRET}/admin/update_stages", methods=["POST"])
def admin_update_stages():
    """
    Handles updating flags, allocated points, and hints.
    Enforces CTF Rules:
      1. Maximum total points across all 6 stages must equal 100.
      2. Minimum points for any single challenge is 5.
      3. Points must strictly increase by level (P1 < P2 < P3 < P4 < P5 < P6).
      4. Flags are encrypted via AES-256 before saving to MongoDB!
    """
    if not session.get("is_admin"):
        abort(403)

    stages = db_manager.get_all_stages()
    new_points = []

    # First pass: collect and validate points
    for s in stages:
        sid = s["stage_id"]
        try:
            pts = int(request.form.get(f"points_{sid}", s["base_points"]))
        except ValueError:
            flash(f"Invalid points format for Stage {sid}.", "error")
            return redirect(url_for("admin_portal"))

        if pts < MIN_STAGE_POINTS:
            flash(f"Rule Violation: Stage {sid} has {pts} points. Minimum allowed per challenge is {MIN_STAGE_POINTS} points!", "error")
            return redirect(url_for("admin_portal"))

        new_points.append((sid, pts))

    # Verify strictly increasing points: P1 < P2 < P3 < P4 < P5 < P6
    new_points.sort(key=lambda x: x[0])
    for i in range(len(new_points) - 1):
        if new_points[i][1] >= new_points[i + 1][1]:
            flash(
                f"Rule Violation: Points must strictly increase with each stage level! "
                f"Stage {new_points[i][0]} has {new_points[i][1]} pts which is >= Stage {new_points[i+1][0]} ({new_points[i+1][1]} pts).",
                "error"
            )
            return redirect(url_for("admin_portal"))

    total_sum = sum(p[1] for p in new_points)
    if total_sum != TOTAL_MAX_POINTS:
        flash(f"Rule Violation: Total sum of allocated stage points is {total_sum} pts. It must exactly equal {TOTAL_MAX_POINTS} points!", "error")
        return redirect(url_for("admin_portal"))

    # Second pass: commit updates with AES-256 encryption
    for s in stages:
        sid = s["stage_id"]
        name = request.form.get(f"name_{sid}", s["stage_name"])
        domain = request.form.get(f"domain_{sid}", s["domain"])
        target_url = request.form.get(f"url_{sid}", s["target_url"])
        pts = int(request.form.get(f"points_{sid}", s["base_points"]))
        raw_flag = request.form.get(f"flag_{sid}", "")
        hint1 = request.form.get(f"hint1_{sid}", s["hint1_text"])
        h1_pen = int(request.form.get(f"h1_pen_{sid}", s["hint1_penalty_pct"]))
        hint2 = request.form.get(f"hint2_{sid}", s["hint2_text"])
        h2_pen = int(request.form.get(f"h2_pen_{sid}", s["hint2_penalty_pct"]))

        db_manager.update_stage_config(
            stage_id=sid,
            stage_name=name,
            domain=domain,
            target_url=target_url,
            base_points=pts,
            plaintext_flag=raw_flag,
            hint1_text=hint1,
            hint1_penalty_pct=h1_pen,
            hint2_text=hint2,
            hint2_penalty_pct=h2_pen
        )

    flash("Configuration Updated Successfully! All flags have been re-encrypted with AES-256 in MongoDB.", "success")
    return redirect(url_for("admin_portal"))


@app.route(f"/{ADMIN_ROUTE_SECRET}/admin/reset_user/<username>", methods=["POST"])
def admin_reset_user(username):
    """Admin function to reset user score and progress."""
    if not session.get("is_admin"):
        abort(403)
    db_manager.db.user_progress.delete_many({"username": username.lower()})
    db_manager.db.submissions.delete_many({"username": username.lower()})
    db_manager.sync_storage()
    flash(f"Progress and submissions for user '{username}' have been cleared.", "info")
    return redirect(url_for("admin_portal"))


# ------------------------------------------------------------------------------
# APPLICATION ENTRYPOINT
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 80)
    print(" [*] CYBERVAULT CENTRAL CTF SCORING & CHALLENGE PORTAL")
    print(f" [*] Local Interface:      http://localhost:{PORT}")
    print(f" [*] Admin Secret Route:   http://localhost:{PORT}/{ADMIN_ROUTE_SECRET}/admin")
    print(f" [*] Admin Credentials:    {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    print(f" [*] Total Max Points:     {TOTAL_MAX_POINTS} pts (Min {MIN_STAGE_POINTS} pts/stage)")
    print(f" [*] Database Storage:     {db_manager.backend_type}")
    print("=" * 80)
    app.run(host="0.0.0.0", port=PORT, debug=True)
