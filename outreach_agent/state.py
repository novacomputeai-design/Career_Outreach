"""Encrypted local relationship memory. Database must be outside the public checkout.

OUTREACH_STATE_KEY is a Fernet key kept in the host secret store, NEVER Git.
OUTREACH_IDENTITY_KEY is a separate high-entropy HMAC key (hex encoded).
"""
from __future__ import annotations
import hashlib
import hmac
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from cryptography.fernet import Fernet

REPO = Path(__file__).resolve().parents[1]
EVENTS = {"RECOMMENDED", "DISMISSED", "CONTACTED", "REPLIED", "MEETING",
          "INTRODUCTION", "OPPORTUNITY", "HIRED", "OPTED_OUT", "FOLLOW_UP"}
SEGMENTS = {"tucson", "remote", "other"}

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def normalized(text):
    return " ".join(str(text or "").casefold().strip().split())

class PrivateStore:
    def __init__(self, path, key=None, identity_key=None):
        self.path = Path(path).expanduser().resolve()
        if self.path == REPO or REPO in self.path.parents:
            raise ValueError("Private database cannot be inside the public repository")
        secret = key or os.getenv("OUTREACH_STATE_KEY")
        identity = identity_key or os.getenv("OUTREACH_IDENTITY_KEY")
        if not secret or not identity or len(identity) < 32:
            raise RuntimeError("Missing encryption and independent >=32-character identity keys")
        self.crypt = Fernet(secret.encode() if isinstance(secret, str) else secret)
        self.identity_key = identity.encode() if isinstance(identity, str) else identity
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.db = sqlite3.connect(str(self.path))
        self.db.row_factory = sqlite3.Row
        if os.name == "posix":
            os.chmod(self.path, 0o600)
        self.db.executescript("""
            PRAGMA journal_mode=WAL;
            PRAGMA foreign_keys=ON;
            CREATE TABLE IF NOT EXISTS people (
                person_id TEXT PRIMARY KEY,
                name_digest TEXT NOT NULL UNIQUE,
                profile_digest TEXT,
                encrypted_record BLOB NOT NULL,
                segment TEXT NOT NULL,
                state TEXT NOT NULL,
                opted_out INTEGER NOT NULL DEFAULT 0,
                first_seen TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS people_profile ON people(profile_digest);
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id TEXT NOT NULL REFERENCES people(person_id),
                kind TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                encrypted_note BLOB NOT NULL
            );
            CREATE TABLE IF NOT EXISTS approvals (
                person_id TEXT NOT NULL REFERENCES people(person_id),
                draft_sha TEXT NOT NULL,
                content_approved TEXT,
                sending_authorized TEXT,
                PRIMARY KEY (person_id, draft_sha)
            );
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                encrypted_value BLOB NOT NULL,
                approved_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS recommendations (
                run_id TEXT NOT NULL,
                person_id TEXT NOT NULL REFERENCES people(person_id),
                PRIMARY KEY(run_id, person_id)
            );
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                started TEXT NOT NULL,
                finished TEXT,
                state TEXT NOT NULL,
                encrypted_summary BLOB
            );
        """)
        self.db.commit()

    def digest(self, value):
        return hmac.new(self.identity_key, normalized(value).encode(), hashlib.sha256).hexdigest()

    def encrypt(self, data):
        return self.crypt.encrypt(json.dumps(data, ensure_ascii=False).encode())

    def decrypt(self, value):
        return json.loads(self.crypt.decrypt(value).decode())

    def match(self, person):
        """Name collisions are deliberately held, including possible namesakes."""
        name = self.digest(person["person_name"])
        profile = person.get("profile_url")
        pd = self.digest(profile.rstrip("/")) if profile else None
        rows = self.db.execute("SELECT * FROM people WHERE name_digest=? OR (? IS NOT NULL AND profile_digest=?)",
                               (name, pd, pd)).fetchall()
        return [dict(r) for r in rows]

    def register(self, person, segment="other", run_id=None):
        if segment not in SEGMENTS:
            raise ValueError("Invalid geographic segment")
        if self.match(person):
            raise ValueError("Identity previously seen or ambiguous; review manually")
        name = self.digest(person["person_name"])
        prof = person.get("profile_url")
        pd = self.digest(prof.rstrip("/")) if prof else None
        person_id = hashlib.sha256((name + (pd or "")).encode()).hexdigest()[:24]
        now = utcnow()
        with self.db:
            self.db.execute(
                "INSERT INTO people VALUES (?,?,?,?,?,?,?,?,?)",
                (person_id, name, pd, self.encrypt(person), segment, "RECOMMENDED", 0, now, now))
            self._event(person_id, "RECOMMENDED", {"source": "daily-audited-recommendation"})
            if run_id is not None:
                self.db.execute("INSERT INTO recommendations(run_id,person_id) VALUES(?,?)",
                                (run_id,person_id))
        return person_id

    def _event(self, person_id, kind, note):
        self.db.execute("INSERT INTO events(person_id,kind,occurred_at,encrypted_note) VALUES(?,?,?,?)",
                        (person_id, kind, utcnow(), self.encrypt(note)))

    def record_event(self, person_id, kind, note=None):
        if kind not in EVENTS:
            raise ValueError("Invalid event")
        row = self.db.execute("SELECT state,opted_out FROM people WHERE person_id=?", (person_id,)).fetchone()
        if row is None:
            raise LookupError("Unknown person")
        if row["opted_out"] and kind not in ("OPTED_OUT",):
            raise ValueError("Opted-out person; no further engagement event permitted")
        if kind in {"REPLIED", "MEETING", "INTRODUCTION", "OPPORTUNITY", "HIRED"}:
            prior = self.db.execute(
                "SELECT 1 FROM events WHERE person_id=? AND kind='CONTACTED'", (person_id,)).fetchone()
            if prior is None:
                raise ValueError("Must record actual contact before a conversation outcome")
        with self.db:
            self._event(person_id,kind,note or {})
            self.db.execute("UPDATE people SET state=?,opted_out=?,updated_at=? WHERE person_id=?",
                            (kind, int(kind=="OPTED_OUT"), utcnow(), person_id))

    def review_contact(self, person_id, *, confirmed_role, confirmed_route, confirmed_fit):
        """User-initiated independent review of actual role, route and meaningful fit."""
        if not all(x is True for x in (confirmed_role,confirmed_route,confirmed_fit)):
            raise ValueError("Role, route and professional fit require separate human confirmation")
        row=self.db.execute("SELECT state,opted_out FROM people WHERE person_id=?",(person_id,)).fetchone()
        if row is None or row["opted_out"]:
            raise ValueError("No eligible person to review")
        with self.db:
            self._event(person_id,"CONTACT_REVIEW_APPROVED",
                        {"human_confirmed_role":True,"human_confirmed_route":True,"human_confirmed_fit":True})
            self.db.execute("UPDATE people SET state=?,updated_at=? WHERE person_id=?",
                            ("CONTACT_REVIEW_APPROVED",utcnow(),person_id))

    def approval(self, person_id, draft, stage):
        """Content approval does not grant sending authorization. No send mechanism exists."""
        if stage not in ("CONTENT_APPROVED", "SEND_AUTHORIZED"):
            raise ValueError("Invalid approval stage")
        if not self.db.execute("SELECT 1 FROM people WHERE person_id=? AND opted_out=0",(person_id,)).fetchone():
            raise ValueError("Unknown or suppressed person")
        sha = hashlib.sha256(draft.encode()).hexdigest()
        row = self.db.execute("SELECT * FROM approvals WHERE person_id=? AND draft_sha=?",
                              (person_id, sha)).fetchone()
        if stage == "SEND_AUTHORIZED" and (row is None or row["content_approved"] is None):
            raise ValueError("Specific draft must be approved before separate send authorization")
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO approvals(person_id,draft_sha) VALUES(?,?)",(person_id,sha))
            col = "content_approved" if stage == "CONTENT_APPROVED" else "sending_authorized"
            self.db.execute(f"UPDATE approvals SET {col}=? WHERE person_id=? AND draft_sha=?",
                            (utcnow(),person_id,sha))
        return sha

    def start_run(self, run_id):
        with self.db:
            self.db.execute("INSERT INTO runs(run_id,started,state) VALUES(?,?,?)",
                            (run_id,utcnow(),"STARTED"))

    def finish_run(self, run_id, status, summary):
        with self.db:
            self.db.execute("UPDATE runs SET finished=?,state=?,encrypted_summary=? WHERE run_id=?",
                            (utcnow(),status,self.encrypt(summary),run_id))

    def latest_report(self):
        row=self.db.execute("SELECT encrypted_summary FROM runs WHERE finished IS NOT NULL "
                            "ORDER BY finished DESC LIMIT 1").fetchone()
        if row is None or row["encrypted_summary"] is None:
            return None
        return self.decrypt(row["encrypted_summary"])

    def human_reviewed_count(self):
        return self.db.execute("SELECT COUNT(DISTINCT person_id) FROM events "
                               "WHERE kind='CONTACT_REVIEW_APPROVED'").fetchone()[0]

    def reviewed_for_run(self, run_id):
        """Readiness is counted only after independently recorded human review."""
        row=self.db.execute(
            "SELECT COUNT(DISTINCT r.person_id) FROM recommendations r "
            "JOIN people p ON p.person_id=r.person_id "
            "JOIN events e ON e.person_id=r.person_id AND e.kind='CONTACT_REVIEW_APPROVED' "
            "WHERE r.run_id=? AND p.opted_out=0", (run_id,)).fetchone()
        return int(row[0]) if row else 0

    def counts(self):
        return [dict(r) for r in self.db.execute(
            "SELECT p.segment,e.kind,COUNT(DISTINCT e.person_id) AS n FROM events e JOIN people p USING(person_id) "
            "GROUP BY p.segment,e.kind ORDER BY p.segment,e.kind")]

    def get_strategy(self):
        row=self.db.execute("SELECT encrypted_value FROM preferences WHERE key='search_priority'").fetchone()
        if not row:
            return "tucson"
        data=self.decrypt(row["encrypted_value"])
        return data.get("segment","tucson")

    def set_strategy(self,segment):
        if segment not in ("tucson","remote"):
            raise ValueError("Only Tucson or US remote are accepted priorities")
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO preferences(key,encrypted_value,approved_at) VALUES(?,?,?)",
                            ("search_priority",self.encrypt({"segment":segment}),utcnow()))

    def close(self):
        self.db.close()
