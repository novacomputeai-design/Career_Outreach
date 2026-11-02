"""Owner-side corroboration of public webpage text, independent of Codex claims.

This verifies that a bounded HTTPS public page actually contains the supplied
excerpt; it does NOT authenticate publisher claims, role status, ownership,
hiring intent or Codex skill execution. It never grants outreach permissions.
"""
from __future__ import annotations

import hashlib
import hmac
from html.parser import HTMLParser
import ipaddress
import json
import re
import socket
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

import requests

MAX_BYTES = 1024 * 1024
MAX_CLAIMS = 35
MAX_ALLOWED_HOSTS = 12
STATUS = {"TEXT_REPRODUCED", "TEXT_NOT_FOUND", "FETCH_UNAVAILABLE", "HOST_NOT_APPROVED"}
SESSION_CONTEXT = b"CAREER_V22_SOURCE_WITNESS_V1\0"


def canonical(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def digest(data):
    return hashlib.sha256(canonical(data)).hexdigest()


class _VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.words = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in ("script", "style", "svg", "noscript"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag.lower() in ("script", "style", "svg", "noscript") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.words.append(data)


def text_body(content, content_type):
    if "html" in content_type:
        parser = _VisibleText()
        parser.feed(content)
        content = " ".join(parser.words)
    return re.sub(r"\s+", " ", content).casefold().strip()


def safe_public_host(url, allowed_hosts, resolver=socket.getaddrinfo):
    """One exact allowlisted HTTPS hostname; no redirect, credentials or IP URL."""
    try:
        u = urlsplit(url)
        host = (u.hostname or "").lower().rstrip(".")
        if (u.scheme != "https" or u.username or u.password or u.port not in (None, 443)
                or not host or host not in allowed_hosts
                or u.fragment or "\\" in url or any(ord(x) < 32 for x in url)):
            return False
    except (ValueError, TypeError, AttributeError):
        return False
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        return False
    if host in {"localhost", "metadata.google.internal"} or host.endswith((".local", ".internal")):
        return False
    try:
        addresses = resolver(host, 443, type=socket.SOCK_STREAM)
        if not addresses:
            return False
        for item in addresses:
            address = ipaddress.ip_address(item[4][0])
            if not address.is_global:
                return False
    except (OSError, ValueError, IndexError):
        return False
    return True


def _pinned_curl_command(url, ip, binary, header_path):
    """Use a prevalidated public IP, preserving TLS SNI/hostname verification.

    --resolve prevents a second DNS answer from choosing the socket target.
    No proxy, redirect, file://, implicit user shell or certificate bypass.
    """
    u = urlsplit(url)
    host = (u.hostname or "").lower().rstrip(".")
    if (u.scheme != "https" or not host or u.username or u.password
            or u.port not in (None, 443) or u.fragment):
        raise ValueError("SOURCE_HTTPS_HOST_REQUIRED")
    ip_obj = ipaddress.ip_address(ip)
    if not ip_obj.is_global:
        raise ValueError("NONPUBLIC_SOCKET_ADDRESS_REJECTED")
    address = "[" + str(ip_obj) + "]" if ip_obj.version == 6 else str(ip_obj)
    return [
        binary, "--disable", "--silent", "--show-error", "--fail",
        "--proto", "=https", "--noproxy", "*",
        "--max-redirs", "0", "--connect-timeout", "4", "--max-time", "14",
        "--max-filesize", str(MAX_BYTES),
        "--resolve", host + ":443:" + address,
        "--dump-header", str(header_path),
        "--user-agent", "CareerPublicSourceWitness/1.0",
        url,
    ]


def bounded_fetch(url, *, resolver=socket.getaddrinfo, runner=subprocess.run,
                  curl_path=None):
    """Read one capped HTTPS public page with DNS-pinned TLS and no redirects.

    A missing pinned curl binary is a HOLD, never an unpinned requests fallback.
    """
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    if (parsed.scheme != "https" or not host or parsed.username or parsed.password
            or parsed.port not in (None, 443) or parsed.fragment):
        raise ValueError("SOURCE_HTTPS_HOST_REQUIRED")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError("NUMERIC_HOST_DISALLOWED")
    if host in {"localhost", "metadata.google.internal"} or host.endswith(
            (".local", ".internal")):
        raise ValueError("LOCAL_HOST_DISALLOWED")
    addresses = resolver(host, 443, type=socket.SOCK_STREAM)
    if not addresses:
        raise ValueError("DNS_UNAVAILABLE")
    validated = []
    for info in addresses:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            raise ValueError("NONPUBLIC_DNS_ANSWER_REJECTED")
        validated.append(str(ip))
    binary = curl_path or shutil.which("curl.exe" if os.name == "nt" else "curl")
    if not binary:
        raise ValueError("PINNED_TLS_CLIENT_UNAVAILABLE")
    with tempfile.TemporaryDirectory(prefix="career-public-witness-") as tmp:
        headers = Path(tmp) / "headers"
        with tempfile.TemporaryFile() as target:
            command = _pinned_curl_command(url, validated[0], binary, headers)
            try:
                process = runner(command, stdout=target, stderr=subprocess.PIPE,
                                 timeout=20, check=False)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise ValueError("SOURCE_FETCH_FAILED") from exc
            if process.returncode:
                raise ValueError("SOURCE_HTTP_UNAVAILABLE")
            target.seek(0, 2)
            if target.tell() > MAX_BYTES:
                raise ValueError("SOURCE_TOO_LARGE")
            target.seek(0)
            payload = target.read(MAX_BYTES + 1)
        raw_headers = headers.read_bytes() if headers.exists() else b""
        if len(raw_headers) > 65536:
            raise ValueError("SOURCE_HEADERS_TOO_LARGE")
        statuses = re.findall(rb"^HTTP/[0-9.]+\s+([0-9]{3})\b", raw_headers,
                              flags=re.MULTILINE)
        if not statuses or statuses[-1] != b"200":
            raise ValueError("SOURCE_HTTP_NOT_200")
        match = re.findall(rb"^content-type:\s*([^\r\n;]+)",
                           raw_headers, flags=re.MULTILINE | re.IGNORECASE)
        ct = match[-1].decode("ascii", errors="ignore").lower().strip() if match else ""
        if not (ct.startswith("text/") or ct == "application/xhtml+xml"):
            raise ValueError("UNSUPPORTED_SOURCE_CONTENT_TYPE")
        return payload.decode("utf-8", errors="replace"), ct

def witness_sources(packet, approved_hosts, *, fetch=bounded_fetch,
                    resolver=socket.getaddrinfo):
    """Source-text evidence only; untrusted data never controls network host trust."""
    from .career_contribution import validate_v22_packet
    validate_v22_packet(packet)
    hosts = {h.strip().lower() for h in approved_hosts}
    if not hosts or len(hosts) > MAX_ALLOWED_HOSTS or any(
        not re.fullmatch(r"[a-z0-9][a-z0-9.-]*[a-z0-9]", h) for h in hosts
    ):
        raise ValueError("OPERATOR_HOST_ALLOWLIST_REQUIRED")
    claims = [(index, claim) for index, record in enumerate(packet["opportunities"])
              for claim in record["claims"]]
    if len(claims) > MAX_CLAIMS:
        raise ValueError("SOURCE_CLAIM_BUDGET_EXCEEDED")
    cache = {}
    results = []
    for index, claim in claims:
        url = claim["source_url"]
        if not safe_public_host(url, hosts, resolver=resolver):
            status, page_digest = "HOST_NOT_APPROVED", None
        else:
            if url not in cache:
                try:
                    body, ct = fetch(url)
                    if len(body.encode("utf-8")) > MAX_BYTES:
                        raise ValueError("SOURCE_TOO_LARGE")
                    cache[url] = (text_body(body, ct), hashlib.sha256(
                        body.encode("utf-8")).hexdigest())
                except (requests.RequestException, OSError, ValueError, UnicodeError):
                    cache[url] = None
            result = cache[url]
            if result is None:
                status, page_digest = "FETCH_UNAVAILABLE", None
            else:
                normalized, page_digest = result
                excerpt = re.sub(r"\s+", " ", claim["excerpt"]).casefold().strip()
                statement = re.sub(r"\s+", " ", claim["claim_text"]).casefold().strip()
                # Reproducing text is necessary, never sufficient for true claims.
                status = ("TEXT_REPRODUCED" if excerpt in normalized and
                          statement in normalized else "TEXT_NOT_FOUND")
        results.append({"index": index, "claim_id": claim["claim_id"],
                        "url": url, "status": status, "source_sha256": page_digest})
    return {
        "version": "1.0", "project_id": "PERSONAL_CAREER_OUTREACH",
        "run_id": packet["run_id"], "packet_sha256": digest(packet),
        "results": results,
        "all_source_text_reproduced": bool(results) and all(
            r["status"] == "TEXT_REPRODUCED" for r in results),
        "source_truth_independently_verified": False,
        "semantic_claims_verified": False, "native_skill_activation_verified": False,
        "owner_identity_authenticated": False, "contact_ready": False,
        "send_authorized": False,
        "assurance": "BOUNDED_OWNER_SESSION_PUBLIC_TEXT_RETRIEVAL_ONLY",
    }


def sign_witness(receipt, secret):
    if not isinstance(secret, (bytes, bytearray)) or len(secret) < 32:
        raise ValueError("OWNER_SESSION_KEY_REQUIRED")
    unsigned = dict(receipt)
    unsigned.pop("owner_session_hmac", None)
    result = dict(unsigned)
    result["owner_session_hmac"] = hmac.new(
        secret, SESSION_CONTEXT + canonical(unsigned), hashlib.sha256).hexdigest()
    return result


def verify_witness(receipt, packet, secret):
    if not isinstance(receipt, dict) or receipt.get("packet_sha256") != digest(packet):
        return False
    tag = receipt.get("owner_session_hmac")
    if not isinstance(tag, str) or not re.fullmatch(r"[0-9a-f]{64}", tag):
        return False
    unsigned = dict(receipt)
    unsigned.pop("owner_session_hmac", None)
    expected = sign_witness(unsigned, secret)["owner_session_hmac"]
    return hmac.compare_digest(tag, expected)
