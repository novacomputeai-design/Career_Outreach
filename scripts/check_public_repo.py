"""Fail if obvious secret values or disallowed private storage enter tracked source."""
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BANNED_PREFIXES=("private/","data/","reports/")
PATTERNS=[
    re.compile(r"tvly-[A-Za-z0-9_-]{24,}"),
    re.compile(r"sk-proj-[A-Za-z0-9_-]{24,}"),
    re.compile(r"(?i)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
def check():
    tracked=subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0")
    bad=[]
    for path in filter(None,tracked):
        if path.startswith(BANNED_PREFIXES) or path.endswith((".sqlite",".sqlite3",".db",".pem",".key",".env")):
            bad.append("disallowed tracked path: "+path)
            continue
        p=ROOT/path
        if not p.is_file() or p.stat().st_size>2_000_000:
            continue
        try: content=p.read_text(encoding="utf-8")
        except UnicodeDecodeError: continue
        for pat in PATTERNS:
            if pat.search(content):
                bad.append("potential secret in "+path+" (pattern only; value withheld)")
    return bad
if __name__=="__main__":
    errors=check()
    for e in errors: print("FAIL:",e)
    if errors: raise SystemExit(1)
    print("PASS: tracked-path and known credential-pattern hygiene (not a comprehensive secret audit)")
