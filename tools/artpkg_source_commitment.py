"""Private local seal commitments, independent of the untrusted package history.

Only seal_session may populate this store after explicit confirmation. Verification
never creates it or imports history. Protect/back up this sidecar with the server's
OS account; local HMACs are not remote signatures or protection from that account.
"""
from contextlib import contextmanager
import fcntl
import hashlib
import hmac
import json
import os
from pathlib import Path
import stat


def safe(path):
    path = Path(path).absolute()
    if ".." in path.parts:
        raise ValueError("source commitment path traversal")
    for part in reversed((path, *path.parents)):
        if part.is_symlink():
            raise ValueError("source commitment Symlink forbidden")
        if part.exists() and not part.is_dir():
            info = part.stat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ValueError("source commitment requires regular unlinked files")
    return path


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def file_hashes(files):
    return {name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(files.items())}


class Store:
    def __init__(self, session_dir):
        self.session = safe(session_dir)
        # Separate from sealed_packages, upload data, and UX review/render custody.
        self.root = safe(self.session / ".artpkg-source-custody")
        self.key = b""

    @contextmanager
    def locked(self, create=False):
        safe(self.root)
        if not self.root.exists():
            if not create:
                raise ValueError("trusted source commitment unavailable; never import seal history")
            history = safe(self.session / "sealed_packages")
            if history.exists() and any(history.iterdir()):
                raise ValueError("source custody missing for existing history; manual recovery required")
            self.root.mkdir(parents=True, mode=0o700)
            for name, raw in (("key", os.urandom(32)), ("lock", b"")):
                fd = os.open(self.root / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "wb") as handle:
                    handle.write(raw)
                    handle.flush()
                    os.fsync(handle.fileno())
            self.key = (self.root / "key").read_bytes()
            self.write({"version": "0.1", "session": str(self.session), "current": None, "seals": {}})
            self.key = b""
        for name in ("key", "lock", "ledger.json"):
            path = safe(self.root / name)
            if not path.is_file() or path.stat().st_mode & 0o077:
                raise ValueError("source custody files missing or not private; manual recovery required")
        if self.root.stat().st_mode & 0o077:
            raise ValueError("source custody directory must be private")
        with (self.root / "lock").open("rb") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                self.key = (self.root / "key").read_bytes()
                if len(self.key) != 32:
                    raise ValueError("invalid source custody key")
                record = json.loads((self.root / "ledger.json").read_bytes())
                signature = record.pop("signature", None)
                expected = hmac.new(self.key, encoded(record), hashlib.sha256).hexdigest()
                if not isinstance(signature, str) or not hmac.compare_digest(signature, expected):
                    raise ValueError("source commitment signature mismatch")
                if (set(record) != {"version", "session", "current", "seals"}
                        or record["version"] != "0.1" or record["session"] != str(self.session)):
                    raise ValueError("source commitment session/schema mismatch")
                yield record
            finally:
                self.key = b""
                fcntl.flock(lock, fcntl.LOCK_UN)

    def write(self, record):
        if not self.key:
            raise ValueError("source custody write requires lock")
        signed = {**record, "signature": hmac.new(self.key, encoded(record), hashlib.sha256).hexdigest()}
        pending = safe(self.root / "ledger.pending")
        fd = os.open(pending, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded(signed))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(pending, self.root / "ledger.json")
        fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def commit(self, ledger, handoff, files, reviewer):
        sealed_id = hashlib.sha256(files["MANIFEST.json"]).hexdigest()
        entry = {"handoff": handoff, "files": file_hashes(files), "reviewer": reviewer}
        if sealed_id in ledger["seals"] and ledger["seals"][sealed_id] != entry:
            raise ValueError("conflicting source commitment")
        ledger["seals"][sealed_id] = entry
        ledger["current"] = sealed_id
        self.write(ledger)


def current(session_dir, reviewer):
    store = Store(session_dir)
    with store.locked() as ledger:
        sealed_id = ledger["current"]
        entry = ledger["seals"].get(sealed_id)
        if not entry or entry["reviewer"] != reviewer:
            raise ValueError("current source commitment missing or wrong owner")
        return sealed_id, entry