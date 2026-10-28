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
USER_RELATIONSHIPS = {"FIRST_LEARNED", "PREVIOUSLY_MET"}

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def normalized(text):
    return " ".join(str(text or "").casefold().strip().split())

class PrivateStore:
    def __init__(self, path, key=None, identity_key=None, *, read_only=False):
        self.path = Path(path).expanduser().resolve()
        if self.path == REPO or REPO in self.path.parents:
            raise ValueError("Private database cannot be inside the public repository")
        secret = key or os.getenv("OUTREACH_STATE_KEY")
        identity = identity_key or os.getenv("OUTREACH_IDENTITY_KEY")
        if not secret or not identity or len(identity) < 32:
            raise RuntimeError("Missing encryption and independent >=32-character identity keys")
        self.crypt = Fernet(secret.encode() if isinstance(secret, str) else secret)
        self.identity_key = identity.encode() if isinstance(identity, str) else identity
        self.read_only = bool(read_only)
        existed = self.path.is_file()
        if existed and not self.read_only:
            # An existing legacy database must never be silently migrated by
            # simply opening it in writable mode. Use the explicit backup-first
            # owner-approved migration, not implicit CREATE TABLE.
            check = sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True)
            try:
                tables = {r[0] for r in check.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'")}
                mandatory = {"people", "events", "approvals", "preferences",
                             "recommendations", "runs", "governance_decisions"}
                if not mandatory.issubset(tables):
                    raise RuntimeError(
                        "Existing private database needs explicit owner-approved "
                        "schema migration; writable access refused")
            finally:
                check.close()
        if self.read_only:
            if not self.path.is_file():
                raise FileNotFoundError("Private database unavailable; cannot verify relationship")
            # SQLite read-only mode avoids initializing or modifying the private schema.
            # Do not use immutable=1, since that would ignore uncheckpointed WAL updates.
            self.db = sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True)
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            self.db = sqlite3.connect(str(self.path))
        self.db.row_factory = sqlite3.Row
        if not self.read_only and not existed:
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
            CREATE TABLE IF NOT EXISTS governance_decisions (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id TEXT NOT NULL,
                action TEXT NOT NULL,
                policy_version TEXT NOT NULL,
                verdict TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                encrypted_detail BLOB NOT NULL
            );
            """)
            self.db.commit()
        # A database is not safe to query or mutate with a different identity
        # key. Decrypt each existing record, independently recompute its stored
        # identity digests, and fail closed BEFORE any user operation.
        try:
            self.verify_identity_binding()
        except Exception:
            self.db.close()
            raise

    def verify_identity_binding(self) -> int:
        """Prove BOTH keys match every existing private identity, never sample."""
        checked = 0
        for row in self.db.execute(
            "SELECT name_digest,profile_digest,encrypted_record FROM people"):
            try:
                person = self.decrypt(row["encrypted_record"])
            except Exception as exc:
                raise RuntimeError(
                    "Cannot authenticate private record with the supplied state key"
                ) from exc
            if not isinstance(person, dict) or not isinstance(person.get("person_name"), str):
                raise RuntimeError("Private record identity missing or malformed")
            expected = self.digest(person["person_name"])
            if not hmac.compare_digest(expected, row["name_digest"]):
                raise RuntimeError("Private identity key mismatch; fail closed")
            profile = person.get("profile_url")
            expected_profile = self.digest(profile.rstrip("/")) if profile else None
            if bool(expected_profile) != bool(row["profile_digest"]):
                raise RuntimeError("Private identity profile binding mismatch")
            if expected_profile is not None and not hmac.compare_digest(
                    expected_profile, row["profile_digest"]):
                raise RuntimeError("Private identity key/profile mismatch")
            checked += 1
        return checked

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
        from .project_scope import scope_reasons
        errors = scope_reasons(person)
        if errors:
            raise ValueError("Personal career scope HOLD: " + ",".join(errors))
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


    def remember_relationship(self, name, relationship, *, profile_url=None, segment="tucson"):
        """Record a USER-REPORTED relationship, not a source-verified lead or outreach event.

        This intentionally avoids RECOMMENDED/CONTACTED/MEETING and never grants
        independent contact-readiness. Ambiguous names and conflicting claims fail closed.
        """
        name = " ".join(str(name or "").strip().split())
        profile_url = (profile_url or "").strip() or None
        relationship = str(relationship or "").upper().strip()
        if len(name.split()) < 2 or len(name) > 240:
            raise ValueError("Enter a full person name (at least two words)")
        if relationship not in USER_RELATIONSHIPS:
            raise ValueError("Relationship must be FIRST_LEARNED or PREVIOUSLY_MET")
        if segment not in SEGMENTS:
            raise ValueError("Invalid geographic segment")
        if profile_url and not profile_url.startswith(("https://", "http://")):
            raise ValueError("Profile URL must begin with https:// or http://")
        query = {"person_name": name, "profile_url": profile_url}
        matches = self.match(query)
        if len(matches) > 1:
            raise ValueError("Ambiguous identity; do not merge namesakes")
        now = utcnow()
        if matches:
            row = matches[0]
            if row["opted_out"]:
                raise ValueError("Suppressed identity; do not change relationship through this command")
            saved = self.decrypt(row["encrypted_record"])
            if normalized(saved.get("person_name")) != normalized(name):
                raise ValueError("Profile matches a different name; manual identity review required")
            old = saved.get("user_relationship_status")
            if old and old != relationship:
                raise ValueError("Conflicting relationship history; manual resolution required")
            old_url = saved.get("profile_url")
            if profile_url and old_url and self.digest(profile_url.rstrip("/")) != self.digest(old_url.rstrip("/")):
                raise ValueError("Same-name different-profile conflict; manual identity review required")
            if relationship == "FIRST_LEARNED":
                past = self.db.execute(
                    "SELECT 1 FROM events WHERE person_id=? AND kind IN "
                    "('CONTACTED','REPLIED','MEETING','INTRODUCTION','OPPORTUNITY','HIRED') LIMIT 1",
                    (row["person_id"],)).fetchone()
                if past:
                    raise ValueError("Recorded prior outreach conflicts with FIRST_LEARNED")
            if old == relationship and (not profile_url or old_url):
                return {"result": "ALREADY_RECORDED", "relationship": relationship,
                        "granted_contact_readiness": False, "messages_sent": 0}
            saved["user_relationship_status"] = relationship
            saved["user_relationship_basis"] = "USER_REPORTED"
            saved["user_relationship_recorded_at"] = now
            pd = row["profile_digest"]
            if profile_url and not old_url:
                saved["profile_url"] = profile_url
                pd = self.digest(profile_url.rstrip("/"))
                others = self.db.execute(
                    "SELECT 1 FROM people WHERE profile_digest=? AND person_id<>?",
                    (pd, row["person_id"])).fetchone()
                if others:
                    raise ValueError("Profile belongs to another stored identity")
            with self.db:
                self.db.execute(
                    "UPDATE people SET encrypted_record=?,profile_digest=?,updated_at=? WHERE person_id=?",
                    (self.encrypt(saved), pd, now, row["person_id"]))
                self._event(row["person_id"], "USER_REPORTED_RELATIONSHIP",
                            {"relationship": relationship, "basis": "USER_REPORTED"})
            return {"result": "UPDATED_EXISTING_RECORD", "relationship": relationship,
                    "granted_contact_readiness": False, "messages_sent": 0}
        person = {"person_name": name, "profile_url": profile_url,
                  "user_relationship_status": relationship,
                  "user_relationship_basis": "USER_REPORTED",
                  "user_relationship_recorded_at": now}
        name_digest = self.digest(name)
        profile_digest = self.digest(profile_url.rstrip("/")) if profile_url else None
        person_id = hashlib.sha256((name_digest + (profile_digest or "")).encode()).hexdigest()[:24]
        state = ("USER_REPORTED_FIRST_LEARNED" if relationship == "FIRST_LEARNED"
                 else "EXISTING_RELATIONSHIP")
        with self.db:
            self.db.execute(
                "INSERT INTO people VALUES (?,?,?,?,?,?,?,?,?)",
                (person_id, name_digest, profile_digest, self.encrypt(person),
                 segment, state, 0, now, now))
            self._event(person_id, "USER_REPORTED_RELATIONSHIP",
                        {"relationship": relationship, "basis": "USER_REPORTED"})
        return {"result": "RECORDED", "relationship": relationship,
                "granted_contact_readiness": False, "messages_sent": 0}

    def check_relationship(self, name, *, profile_url=None):
        """Minimal safe lookup; never implies absence here proves a person is new."""
        name = " ".join(str(name or "").strip().split())
        if not name:
            raise ValueError("Name is required")
        rows = self.match({"person_name": name, "profile_url": profile_url})
        if not rows:
            return {"result": "NOT_FOUND_IN_LOCAL_STORE", "novelty": "UNVERIFIED",
                    "granted_contact_readiness": False}
        if len(rows) != 1:
            return {"result": "AMBIGUOUS_IDENTITY_HOLD", "novelty": "UNVERIFIED",
                    "granted_contact_readiness": False}
        row = rows[0]
        saved = self.decrypt(row["encrypted_record"])
        if normalized(saved.get("person_name")) != normalized(name):
            return {"result": "IDENTITY_CONFLICT_HOLD", "novelty": "UNVERIFIED",
                    "granted_contact_readiness": False}
        old_url = saved.get("profile_url")
        if profile_url and old_url and self.digest(profile_url.rstrip("/")) != self.digest(old_url.rstrip("/")):
            return {"result": "POSSIBLE_NAMESAKE_HOLD", "novelty": "UNVERIFIED",
                    "granted_contact_readiness": False}
        relationship = saved.get("user_relationship_status", "NOT_USER_CLASSIFIED")
        return {"result": "EXISTING_RELATIONSHIP" if relationship == "PREVIOUSLY_MET" else "SEEN_IN_STORE",
                "user_reported_relationship": relationship,
                "suppressed": bool(row["opted_out"]),
                "novelty": "ALREADY_IN_LOCAL_STORE",
                "granted_contact_readiness": False}

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


    def _audit_governance(self, person_id, action, decision, draft_sha=None):
        """Append a local policy-versioned encrypted decision; no PII in plaintext detail."""
        self.db.execute(
            "INSERT INTO governance_decisions(person_id,action,policy_version,verdict,"
            "occurred_at,encrypted_detail) VALUES(?,?,?,?,?,?)",
            (person_id, action, decision["policy_version"], decision["decision"],
             utcnow(), self.encrypt({"reason_codes":decision["reasons"],
                                    "draft_sha256":draft_sha,
                                    "assurance":decision["assurance"]})))

    def review_contact(self, person_id, *, confirmed_role, confirmed_route, confirmed_fit):
        """Manual attestation AFTER structural source gate. Not proof of source truth."""
        from .governance import active_policy, structural_review_gate
        policy = active_policy()
        row = self.db.execute(
            "SELECT opted_out,encrypted_record FROM people WHERE person_id=?",
            (person_id,)).fetchone()
        if row is None:
            decision = {"decision":"HOLD","reasons":["UNKNOWN_PERSON"],
                        "policy_version":policy["version"],
                        "assurance":"LOCAL_OPERATOR_ATTESTATION_ONLY"}
            with self.db:
                self._audit_governance(person_id,"CONTACT_REVIEW",decision)
            raise ValueError("Governance HOLD: UNKNOWN_PERSON")
        evidence = self.decrypt(row["encrypted_record"])
        decision = structural_review_gate(evidence,opted_out=bool(row["opted_out"]),policy=policy)
        if not all(x is True for x in (confirmed_role, confirmed_route, confirmed_fit)):
            decision["decision"]="HOLD"
            decision["reasons"].append("INDEPENDENT_HUMAN_ATTESTATION_INCOMPLETE")
        if decision["decision"]!="PENDING_HUMAN_REVIEW":
            with self.db:
                self._audit_governance(person_id,"CONTACT_REVIEW",decision)
            raise ValueError("Governance HOLD: "+",".join(sorted(set(decision["reasons"]))))
        with self.db:
            self._event(person_id,"CONTACT_REVIEW_APPROVED",
                        {"human_attested_role":True,"human_attested_route":True,
                         "human_attested_fit":True,
                         "policy_version":decision["policy_version"],
                         "assurance":"OPERATOR_ATTESTATION_NOT_INDEPENDENTLY_AUTHENTICATED"})
            self._audit_governance(person_id,"CONTACT_REVIEW",
                                   {"decision":"ALLOW_REVIEW_RECORD","reasons":[],
                                    "policy_version":decision["policy_version"],
                                    "assurance":"LOCAL_OPERATOR_ATTESTATION_ONLY"})
            self.db.execute("UPDATE people SET state=?,updated_at=? WHERE person_id=?",
                            ("CONTACT_REVIEW_APPROVED",utcnow(),person_id))

    def approval(self, person_id, draft, stage):
        """Fail-closed human approval record, NOT a send operation or recipient verification."""
        from .governance import active_policy, structural_review_gate, approval_gate
        policy = active_policy()
        if stage not in ("CONTENT_APPROVED","SEND_AUTHORIZED"):
            raise ValueError("Invalid approval stage")
        row = self.db.execute(
            "SELECT opted_out,encrypted_record FROM people WHERE person_id=?",
            (person_id,)).fetchone()
        if row is None:
            decision = {"decision":"HOLD","reasons":["UNKNOWN_PERSON"],
                        "policy_version":policy["version"],
                        "assurance":"LOCAL_OPERATOR_ATTESTATION_ONLY"}
            with self.db:
                self._audit_governance(person_id,stage,decision)
            raise ValueError("Governance HOLD: UNKNOWN_PERSON")
        structural = structural_review_gate(
            self.decrypt(row["encrypted_record"]),opted_out=bool(row["opted_out"]),
            policy=policy)
        reviewed = self.db.execute(
            "SELECT 1 FROM events WHERE person_id=? AND kind='CONTACT_REVIEW_APPROVED'",
            (person_id,)).fetchone() is not None
        sha = hashlib.sha256(draft.encode()).hexdigest()
        existing = self.db.execute(
            "SELECT * FROM approvals WHERE person_id=? AND draft_sha=?",
            (person_id,sha)).fetchone()
        decision = approval_gate(
            structural,user_review_recorded=reviewed,stage=stage,
            draft_content_preapproved=(existing is not None and
                                       existing["content_approved"] is not None))
        if decision["decision"]=="HOLD":
            with self.db:
                self._audit_governance(person_id,stage,decision,draft_sha=sha)
            raise ValueError("Governance HOLD: "+",".join(decision["reasons"]))
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO approvals(person_id,draft_sha) VALUES(?,?)",
                            (person_id,sha))
            column = "content_approved" if stage=="CONTENT_APPROVED" else "sending_authorized"
            self.db.execute(f"UPDATE approvals SET {column}=? WHERE person_id=? AND draft_sha=?",
                            (utcnow(),person_id,sha))
            self._audit_governance(person_id,stage,decision,draft_sha=sha)
        return sha

    def recent_governance_decisions(self, *, limit=20):
        """Operator-only audit digest: no raw contact notes, private draft content or keys."""
        if not isinstance(limit,int) or not 1<=limit<=100:
            raise ValueError("Audit limit must be 1..100")
        rows=self.db.execute(
            "SELECT person_id,action,policy_version,verdict,occurred_at,encrypted_detail "
            "FROM governance_decisions ORDER BY audit_id DESC LIMIT ?",(limit,)).fetchall()
        results=[]
        for row in rows:
            detail=self.decrypt(row["encrypted_detail"])
            results.append({"person_id":row["person_id"],"action":row["action"],
                            "policy_version":row["policy_version"],"decision":row["verdict"],
                            "reason_codes":detail.get("reason_codes",[]),
                            "occurred_at":row["occurred_at"]})
        return results

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
        """Count operator-attested source/route/fit reviews, NOT proven-new contact-ready people."""
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
