"""
================================================================================
CyberVault : Operation ShadowTrace - Database Manager (MongoDB Dual-Engine)
Supports live MongoDB daemon and persistent JSON-backed driver fallback.
All flags stored in MongoDB are strictly encrypted via AES-256.
================================================================================
"""

import os
import json
import time
import bcrypt
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import mongomock
from dotenv import load_dotenv

from crypto_vault import encrypt_flag, hash_flag, decrypt_flag

import tempfile

# Load env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/cybervault_ctf")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "cybervault_ctf")

# On Vercel serverless environment, local filesystem is read-only except /tmp
if os.environ.get("VERCEL"):
    DATA_DIR = os.path.join(tempfile.gettempdir(), "cybervault_data")
else:
    DATA_DIR = os.path.join(BASE_DIR, "data")

STORAGE_FILE = os.path.join(DATA_DIR, "mongo_storage.json")

try:
    os.makedirs(DATA_DIR, exist_ok=True)
except Exception:
    pass

DEFAULT_CRYPTIC_BRIEFS = {
    1: "The adversary and employees leave subtle digital footprints across corporate public gateways. Shadows believe casual updates go unnoticed in the digital commons, yet public corporate feeds and job listings reveal operational infrastructure. Scour the organization's public channels to discover the hidden domain.",
    2: "A picture is worth a thousand words, but its hidden attributes can whisper confidential secrets. An asset depicting an ancient Roman emperor was published on the social stream. Peer behind the visible pixels and into the digital canvas properties to unmask what lies buried beneath.",
    3: "A secured vault portal guards confidential assets, demanding legitimate credentials. Yet when applications trust user input unconditionally, an adversary can craft punctuation that alters database logic and nullifies the password barrier completely. Force the gateway to accept your presence as the master administrator.",
    4: "Upon piercing the portal perimeter, an urgent dispatch materialized in a confidential transmission popup. The letters appear shifted out of alignment, guarded by the ancient wheel of rotation. Rotate the alphabet back into alignment to reveal the intercepted intelligence.",
    5: "Every intruder leaves echoes in the machine's historical audit records. A relentless adversary battered the vault's endpoints in repeated failure before sneaking through an opening. Trace the forensic timeline of anomalous requests to uncover the flag left in the trail.",
    6: "You have gained access to the remote staging bastion console as a restricted service account. However, sovereign authority remains locked in root custody. Investigate your authorized sudo delegations, invoke the privileged maintenance routine, and claim the final capstone flag."
}


class DatabaseManager:
    def __init__(self):
        self.is_mock = False
        self.backend_type = "Unknown"
        self.client = None
        self.db = None
        self._init_connection()
        self._ensure_initial_schema()

    def _init_connection(self):
        """Attempts connection to real MongoDB; falls back to persistent mongomock."""
        try:
            real_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2500)
            # Force server check
            real_client.server_info()
            self.client = real_client
            self.db = self.client[MONGO_DB_NAME]
            self.is_mock = False
            self.backend_type = "MongoDB Live Engine (Daemon / ReplicaSet)"
            print(f"[+] [MongoDB] Connected to live MongoDB server: {MONGO_URI}")
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as err:
            self.is_mock = True
            self.backend_type = "MongoDB Embedded Driver (Local Persistent Storage)"
            print(f"[*] [MongoDB] Live daemon not detected ({err}). Initializing local MongoDB storage engine.")
            self.client = mongomock.MongoClient()
            self.db = self.client[MONGO_DB_NAME]
            self._load_mock_storage()

    def _load_mock_storage(self):
        """Loads persistent JSON data into mongomock if existing."""
        if not os.path.exists(STORAGE_FILE):
            return
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for col_name, docs in data.items():
                if docs:
                    self.db[col_name].drop()
                    self.db[col_name].insert_many(docs)
            print(f"[+] [MongoDB] Restored persistent documents from {STORAGE_FILE}")
        except Exception as e:
            print(f"[-] [MongoDB] Error restoring mock storage: {e}")

    def sync_storage(self):
        """Persists mock storage to disk so data is never lost across server restarts."""
        if not self.is_mock:
            return
        try:
            dump = {}
            for col_name in ["users", "flags", "submissions", "user_progress", "system_config", "audit_logs"]:
                dump[col_name] = list(self.db[col_name].find({}, {"_id": 0}))
            with open(STORAGE_FILE, "w", encoding="utf-8") as f:
                json.dump(dump, f, indent=2, default=str)
        except Exception as e:
            print(f"[-] [MongoDB] Error saving mock storage: {e}")

    def _ensure_initial_schema(self):
        """Seeds default stages, encrypted flags, marks, and sample users if not present."""
        print("[+] [MongoDB] Synchronizing 6 CTF stages with AES-256 encrypted flags...")
        initial_stages = [
            {
                "stage_id": 1,
                "stage_name": "Stage 1: Open-Source Intelligence & Perimeter Reconnaissance",
                "domain": "OSINT & Digital Footprinting",
                "target_url": "https://ctf-playbox-fvpk.vercel.app/",
                "placeholder": "_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _",
                "base_points": 5,
                "raw_flag": "vault-staging.cybervaulttech.com",
                "hint1_text": "Hiring announcements often whisper what infrastructure teams are secretly building. Cross-reference corporate job requirements with the engineering social broadcasts.",
                "hint1_penalty_pct": 0,
                "hint2_text": "Look for an employee posting about recent cluster migrations on the public feed. An internal staging domain name was accidentally left in plain sight.",
                "hint2_penalty_pct": 50,
                "difficulty": "Foundational (OSINT)"
            },
            {
                "stage_id": 2,
                "stage_name": "Stage 2: Digital Steganography & Metadata Analysis",
                "domain": "Digital Steganography & Asset Analysis",
                "target_url": "https://ctf-playbox-fvpk.vercel.app/",
                "placeholder": "CVT{...}",
                "base_points": 10,
                "raw_flag": "CVT{m3t4d4t4_3x1f_us3r_c0mm3nt_l34k}",
                "hint1_text": "Images speak in pixels to human eyes, but machines read the invisible headers inscribed within their creation records.",
                "hint1_penalty_pct": 0,
                "hint2_text": "Inspect the EXIF metadata properties of the shared Roman emperor image. The embedded user comment holds an encoded ciphertext waiting to be translated.",
                "hint2_penalty_pct": 50,
                "difficulty": "Easy (Steganography)"
            },
            {
                "stage_id": 3,
                "stage_name": "Stage 3: Authentication Portal SQL Injection Bypass",
                "domain": "Web Application Security (OWASP SQLi)",
                "target_url": "https://ctf-playbox-fvpk.vercel.app/",
                "placeholder": "CVT{...}",
                "base_points": 15,
                "raw_flag": "CVT{sql1_byp4ss_v4ult_4dm1n}",
                "hint1_text": "When a gatekeeper blindly concatenates your words into queries, a well-placed punctuation mark can silence the rest of the question.",
                "hint1_penalty_pct": 0,
                "hint2_text": "The login form is vulnerable to classic SQL injection. Inject an SQL termination and comment syntax into the username field to bypass password authentication as the administrator.",
                "hint2_penalty_pct": 50,
                "difficulty": "Intermediate (SQLi Bypass)"
            },
            {
                "stage_id": 4,
                "stage_name": "Stage 4: Classical Cryptanalysis & Caesar Cipher",
                "domain": "Classical Cryptanalysis & Rotational Ciphers",
                "target_url": "https://ctf-playbox-fvpk.vercel.app/",
                "placeholder": "CVT{...}",
                "base_points": 20,
                "raw_flag": "CVT{c43s4r_sh1ft_k3y_r0t4t10n_9173}",
                "hint1_text": "The Roman general's ancient wheel of letters has turned. Rotate the characters of the intercepted alert to restore order to chaos.",
                "hint1_penalty_pct": 0,
                "hint2_text": "Analyze the encrypted memo displayed in the transmission popup. Apply a Caesar cipher rotation key to unshift the disguised ciphertext letters back to their true positions.",
                "hint2_penalty_pct": 50,
                "difficulty": "Intermediate (Caesar Cryptanalysis)"
            },
            {
                "stage_id": 5,
                "stage_name": "Stage 5: Forensic Access Log Analysis & Threat Hunting",
                "domain": "Digital Forensics & Incident Response",
                "target_url": "https://ctf-playbox-fvpk.vercel.app/",
                "placeholder": "CVT{...}",
                "base_points": 24,
                "raw_flag": "CVT{f0r3ns1c_l0g_tr41l_unv31l3d}",
                "hint1_text": "Where many doors were knocked upon in vain, one finally opened. Follow the footprints of the persistent visitor through the historical ledger.",
                "hint1_penalty_pct": 0,
                "hint2_text": "Filter the server access logs for anomalous IP addresses exhibiting bursts of authentication failures followed by a successful request. The trail reveals leaked forensic artifacts.",
                "hint2_penalty_pct": 50,
                "difficulty": "Intermediate - Advanced (Log Forensics)"
            },
            {
                "stage_id": 6,
                "stage_name": "Stage 6: Capstone Host Linux Privilege Escalation",
                "domain": "Linux System Security & Privilege Escalation",
                "target_url": "https://ctf-playbox-r7ou.vercel.app/",
                "placeholder": "CVT{...}",
                "base_points": 26,
                "raw_flag": "CVT{r00t_pr1v_3sc_c4pst0n3_mast3r}",
                "hint1_text": "A humble servant often possesses special delegated privileges granted by the sovereign realm. Query the system to see what powers you are permitted to invoke.",
                "hint1_penalty_pct": 0,
                "hint2_text": "In the web terminal, inspect your user's allowed sudo privileges to identify scripts that can be executed with elevated root permissions, then run the authorized maintenance script.",
                "hint2_penalty_pct": 50,
                "difficulty": "Advanced (Privilege Escalation Capstone)"
            }
        ]

        for st in initial_stages:
            # Encrypt flag before inserting into MongoDB
            enc = encrypt_flag(st["raw_flag"])
            hsh = hash_flag(st["raw_flag"])
            stage_doc = {
                "stage_id": st["stage_id"],
                "stage_name": st["stage_name"],
                "domain": st["domain"],
                "target_url": st["target_url"],
                "placeholder": st.get("placeholder", "CVT{...}"),
                "base_points": st["base_points"],
                "encrypted_flag": enc,
                "flag_hash": hsh,
                "hint1_text": st["hint1_text"],
                "hint1_penalty_pct": st["hint1_penalty_pct"],
                "hint2_text": st["hint2_text"],
                "hint2_penalty_pct": st["hint2_penalty_pct"],
                "difficulty": st["difficulty"],
                "updated_at": datetime.utcnow().isoformat()
            }
            self.db.flags.update_one({"stage_id": st["stage_id"]}, {"$set": stage_doc}, upsert=True)

        # Ensure administrative user exists in users collection
        if not self.db.users.find_one({"role": "admin"}):
            print("[+] [MongoDB] Seeding administrative account into users collection...")
            admin_doc = {
                "username": "admin",
                "password_hash": bcrypt.hashpw(b"CyberVaultAdmin#2026!", bcrypt.gensalt()).decode("utf-8"),
                "full_name": "Chief System Administrator",
                "team_name": "CyberVault Command Enclave",
                "role": "admin",
                "created_at": datetime.utcnow().isoformat()
            }
            self.db.users.replace_one({"username": "admin"}, admin_doc, upsert=True)

        # Seed sample benchmark participants for the scoreboard if empty
        if self.db.users.count_documents({"role": "participant"}) == 0:
            print("[+] [MongoDB] Seeding initial leaderboard benchmark users...")
            demo_users = [
                {
                    "username": "phantom_zero",
                    "password_hash": bcrypt.hashpw(b"ShadowHacker#1", bcrypt.gensalt()).decode("utf-8"),
                    "full_name": "Kavinda Perera",
                    "team_name": "RedTeam Alpha",
                    "role": "participant",
                    "created_at": "2026-10-08T08:30:00"
                },
                {
                    "username": "cyber_valkyrie",
                    "password_hash": bcrypt.hashpw(b"ShadowHacker#2", bcrypt.gensalt()).decode("utf-8"),
                    "full_name": "Sanuthi Jayawardena",
                    "team_name": "ByteGuardians",
                    "role": "participant",
                    "created_at": "2026-10-08T09:15:00"
                }
            ]
            self.db.users.insert_many(demo_users)

            # Seed benchmark solves
            # phantom_zero: solved stages 1, 2, 4 (with hint 1 on stage 4)
            # Stage 1: 5 pts
            # Stage 2: 10 pts
            # Stage 4: 20 pts - 10% = 18 pts -> Total: 33 pts
            self.db.user_progress.insert_many([
                {
                    "username": "phantom_zero",
                    "stage_id": 1,
                    "solved": True,
                    "hints_unlocked": [],
                    "penalty_deducted": 0,
                    "points_earned": 5.0,
                    "solved_at": "2026-10-08T09:00:00"
                },
                {
                    "username": "phantom_zero",
                    "stage_id": 2,
                    "solved": True,
                    "hints_unlocked": [],
                    "penalty_deducted": 0,
                    "points_earned": 10.0,
                    "solved_at": "2026-10-08T09:40:00"
                },
                {
                    "username": "phantom_zero",
                    "stage_id": 4,
                    "solved": True,
                    "hints_unlocked": [1],
                    "penalty_deducted": 2.0,
                    "points_earned": 18.0,
                    "solved_at": "2026-10-08T10:15:00"
                },
                # cyber_valkyrie: solved Stage 1, 2
                {
                    "username": "cyber_valkyrie",
                    "stage_id": 1,
                    "solved": True,
                    "hints_unlocked": [],
                    "penalty_deducted": 0,
                    "points_earned": 5.0,
                    "solved_at": "2026-10-08T09:25:00"
                },
                {
                    "username": "cyber_valkyrie",
                    "stage_id": 2,
                    "solved": True,
                    "hints_unlocked": [],
                    "penalty_deducted": 0,
                    "points_earned": 10.0,
                    "solved_at": "2026-10-08T10:00:00"
                }
            ])

        self.sync_storage()

    # ==========================================================================
    # USER OPERATIONS
    # ==========================================================================
    def register_user(self, username, password, full_name="", team_name=""):
        clean_user = username.strip().lower()
        if not clean_user or not password:
            return False, "Username and password are required."
        if len(clean_user) < 3:
            return False, "Username must be at least 3 characters."
        if self.db.users.find_one({"username": clean_user}):
            return False, f"User '{clean_user}' is already registered."

        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        doc = {
            "username": clean_user,
            "password_hash": pw_hash,
            "full_name": full_name.strip() or clean_user,
            "team_name": team_name.strip() or "Independent Cadet",
            "role": "participant",
            "created_at": datetime.utcnow().isoformat()
        }
        self.db.users.insert_one(doc)
        self.sync_storage()
        return True, "Registration successful."

    def authenticate_user(self, username, password):
        clean_user = username.strip().lower()
        user_doc = self.db.users.find_one({"username": clean_user})
        if not user_doc:
            return False, None
        stored_hash = user_doc.get("password_hash", "")
        if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            return True, user_doc
        return False, None

    def authenticate_admin(self, username, password):
        """Authenticates admin credentials dynamically against the MongoDB users collection."""
        clean_user = username.strip().lower()
        admin_doc = self.db.users.find_one({"username": clean_user, "role": "admin"})
        if not admin_doc:
            return False, None
        stored_hash = admin_doc.get("password_hash", "")
        if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            return True, admin_doc
        return False, None

    # ==========================================================================
    # STAGES & FLAGS
    # ==========================================================================
    def get_all_stages(self, include_decrypted_for_admin=False):
        stages = list(self.db.flags.find({}, {"_id": 0}).sort("stage_id", 1))
        for s in stages:
            sid = s.get("stage_id", 1)
            s["cryptic_brief"] = DEFAULT_CRYPTIC_BRIEFS.get(sid, s.get("cryptic_brief", ""))
            s["hint1_penalty_pct"] = 0
            s["hint2_penalty_pct"] = 50
            if "placeholder" not in s or not s["placeholder"]:
                s["placeholder"] = "_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _" if sid == 1 else "CVT{...}"
            if include_decrypted_for_admin:
                s["decrypted_flag"] = decrypt_flag(s.get("encrypted_flag", ""))
        return stages

    def get_stage_by_id(self, stage_id: int):
        stage = self.db.flags.find_one({"stage_id": int(stage_id)}, {"_id": 0})
        if stage:
            sid = stage.get("stage_id", 1)
            stage["cryptic_brief"] = DEFAULT_CRYPTIC_BRIEFS.get(sid, stage.get("cryptic_brief", ""))
            stage["hint1_penalty_pct"] = 0
            stage["hint2_penalty_pct"] = 50
            if "placeholder" not in stage or not stage["placeholder"]:
                stage["placeholder"] = "_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _" if sid == 1 else "CVT{...}"
        return stage

    def update_stage_config(self, stage_id: int, stage_name: str, domain: str, target_url: str,
                            base_points: int, plaintext_flag: str,
                            hint1_text: str, hint1_penalty_pct: int,
                            hint2_text: str, hint2_penalty_pct: int,
                            placeholder: str = None):
        """Updates stage configuration and encrypts the flag in MongoDB."""
        update_data = {
            "stage_name": stage_name.strip(),
            "domain": domain.strip(),
            "target_url": target_url.strip(),
            "base_points": int(base_points),
            "hint1_text": hint1_text.strip(),
            "hint1_penalty_pct": int(hint1_penalty_pct),
            "hint2_text": hint2_text.strip(),
            "hint2_penalty_pct": int(hint2_penalty_pct),
            "updated_at": datetime.utcnow().isoformat()
        }
        if placeholder is not None:
            update_data["placeholder"] = placeholder.strip()
        if plaintext_flag and plaintext_flag.strip():
            clean_flag = plaintext_flag.strip()
            update_data["encrypted_flag"] = encrypt_flag(clean_flag)
            update_data["flag_hash"] = hash_flag(clean_flag)

        self.db.flags.update_one({"stage_id": int(stage_id)}, {"$set": update_data})
        self.sync_storage()

    # ==========================================================================
    # USER PROGRESS & HINTS
    # ==========================================================================
    def get_user_progress(self, username: str):
        """Returns dict of stage_id -> progress record for the user."""
        docs = list(self.db.user_progress.find({"username": username.lower()}, {"_id": 0}))
        prog = {}
        for d in docs:
            prog[d["stage_id"]] = d
        return prog

    def unlock_hint(self, username: str, stage_id: int, hint_number: int):
        """Unlocks Hint 1 (free / no deduction) or Hint 2 (-50% marks deduction) for a specific stage and user."""
        stage_id = int(stage_id)
        hint_number = int(hint_number)
        username = username.lower()

        stage = self.get_stage_by_id(stage_id)
        if not stage:
            return False, "Stage not found.", None

        record = self.db.user_progress.find_one({"username": username, "stage_id": stage_id})
        if not record:
            record = {
                "username": username,
                "stage_id": stage_id,
                "solved": False,
                "hints_unlocked": [],
                "penalty_deducted": 0.0,
                "points_earned": 0.0,
                "solved_at": None
            }
            self.db.user_progress.insert_one(record)

        hints = record.get("hints_unlocked", [])
        if hint_number not in hints:
            hints.append(hint_number)
            self.db.user_progress.update_one(
                {"username": username, "stage_id": stage_id},
                {"$set": {"hints_unlocked": sorted(hints)}}
            )
            self.sync_storage()

        hint_text = stage.get("hint1_text") if hint_number == 1 else stage.get("hint2_text")
        if hint_number == 1:
            return True, "Hint 1 revealed (No marks deduction).", hint_text
        else:
            return True, "Hint 2 unlocked (-50% stage marks deduction applied).", hint_text

    def submit_stage_flag(self, username: str, stage_id: int, submitted_flag: str):
        """
        Validates submitted flag against encrypted flag in MongoDB, calculates penalties,
        and saves submission and progress.
        """
        stage_id = int(stage_id)
        username = username.lower()
        clean_sub = submitted_flag.strip()

        stage = self.get_stage_by_id(stage_id)
        if not stage:
            return False, "Invalid Stage ID.", 0.0

        # Check if already solved
        progress = self.db.user_progress.find_one({"username": username, "stage_id": stage_id})
        if progress and progress.get("solved"):
            return False, f"Stage {stage_id} already solved! Earned: {progress.get('points_earned')} pts", progress.get('points_earned')

        from crypto_vault import verify_flag, decrypt_flag
        is_valid = verify_flag(clean_sub, stage.get("encrypted_flag"), stage.get("flag_hash"))

        # Additional validation resilience for Stage 1 domain or accidental CVT{...} wrapper
        if not is_valid:
            expected_flag = decrypt_flag(stage.get("encrypted_flag", ""))
            if clean_sub.lower() == expected_flag.lower():
                is_valid = True
            elif clean_sub.startswith("CVT{") and clean_sub.endswith("}"):
                inner = clean_sub[4:-1].strip()
                if inner.lower() == expected_flag.lower() or inner == expected_flag:
                    is_valid = True

        # Calculate score and penalties
        base_points = float(stage.get("base_points", 0))
        hints_unlocked = progress.get("hints_unlocked", []) if progress else []
        
        penalty_deducted = 0.0
        # If hint 2 viewed: 50% deduction of marks
        if 2 in hints_unlocked:
            penalty_deducted = base_points * 0.50
        elif 1 in hints_unlocked:
            # Hint 1 is free: 0% penalty
            penalty_deducted = 0.0

        points_awarded = max(0.0, round(base_points - penalty_deducted, 2)) if is_valid else 0.0

        # Record submission
        submission_doc = {
            "username": username,
            "stage_id": stage_id,
            "submitted_flag": clean_sub,
            "is_correct": is_valid,
            "points_awarded": points_awarded,
            "penalty_deducted": penalty_deducted if is_valid else 0.0,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.db.submissions.insert_one(submission_doc)

        if is_valid:
            self.db.user_progress.update_one(
                {"username": username, "stage_id": stage_id},
                {"$set": {
                    "solved": True,
                    "points_earned": points_awarded,
                    "penalty_deducted": penalty_deducted,
                    "solved_at": datetime.utcnow().isoformat()
                }},
                upsert=True
            )
            self.sync_storage()
            penalty_msg = f" (Penalties: -{penalty_deducted} pts)" if penalty_deducted > 0 else ""
            return True, f"🎉 Flag Accepted! Stage {stage_id} complete. Earned {points_awarded} / {base_points} pts{penalty_msg}", points_awarded
        else:
            self.sync_storage()
            err_msg = "❌ Incorrect hostname. Ensure exact full domain name (e.g. vault-staging.cybervaulttech.com)." if stage_id == 1 else "❌ Incorrect flag. Ensure exact casing and 'CVT{...}' format."
            return False, err_msg, 0.0

    # ==========================================================================
    # RANKINGS & LEADERBOARD
    # ==========================================================================
    def get_leaderboard(self):
        """
        Calculates rankings:
        Total Score (out of 100), solved count, hints penalty, last solve time.
        Ordered by: score DESC, last_solved_at ASC.
        """
        users = list(self.db.users.find({"role": "participant"}, {"_id": 0}))
        stages = self.get_all_stages()
        total_possible = sum(s.get("base_points", 0) for s in stages)

        board = []
        for u in users:
            uname = u["username"]
            progress_records = list(self.db.user_progress.find({"username": uname}))
            
            solved_stages = [p["stage_id"] for p in progress_records if p.get("solved")]
            total_score = sum(p.get("points_earned", 0.0) for p in progress_records if p.get("solved"))
            total_penalty = sum(p.get("penalty_deducted", 0.0) for p in progress_records if p.get("solved"))
            hints_used_count = sum(len(p.get("hints_unlocked", [])) for p in progress_records)

            solve_timestamps = [p.get("solved_at") for p in progress_records if p.get("solved") and p.get("solved_at")]
            last_solve = max(solve_timestamps) if solve_timestamps else u.get("created_at")

            board.append({
                "username": uname,
                "full_name": u.get("full_name", uname),
                "team_name": u.get("team_name", "Cadet"),
                "total_score": round(total_score, 2),
                "total_possible": total_possible,
                "solved_count": len(solved_stages),
                "solved_stages": solved_stages,
                "hints_used_count": hints_used_count,
                "total_penalty": round(total_penalty, 2),
                "last_solve": last_solve
            })

        # Sort: Highest score first, then earliest last solve
        board.sort(key=lambda x: (-x["total_score"], x["last_solve"] or "9999"))

        # Add rank position
        for idx, entry in enumerate(board, 1):
            entry["rank"] = idx

        return board

    def get_recent_submissions(self, limit=20):
        return list(self.db.submissions.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))


db_manager = DatabaseManager()
