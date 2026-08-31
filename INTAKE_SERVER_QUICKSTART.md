# ArtPkgPro Intake Server — Authenticated LAN Pilot

## Quick Start

### Step 1: Configure Credentials

**Option A: Environment Variable (Simple)**
```bash
export ARTPKG_INTAKE_CREDENTIALS='tester1:pilot_secret_1,tester2:pilot_secret_2,tester3:pilot_secret_3'
```

**Option B: Credentials File (Recommended)**
```bash
cat > credentials.json <<EOF
{
  "tester1": "pilot_secret_1",
  "tester2": "pilot_secret_2",
  "tester3": "pilot_secret_3"
}
EOF

export ARTPKG_INTAKE_CREDENTIALS_FILE=/path/to/credentials.json
```

### Step 2: Start the Service

**Loopback Only (default)**:
```bash
cd /path/to/ArtPkgPro
python tools/artpkg_intake_server.py --workspace . --port 8765
```

**LAN Accessible** (after security review):
```bash
python tools/artpkg_intake_server.py --workspace . --host 0.0.0.0 --port 8765
```

### Step 3: Access via Browser

Open a browser and navigate to `http://localhost:8765/`

When prompted by the browser's Basic Auth dialog, enter:
- **Username**: `tester1` (or `tester2`, `tester3`)
- **Password**: `pilot_secret_1` (or corresponding password)

## Command-Line Testing

### Test Authentication

```bash
# No credentials → 401
curl http://localhost:8765/

# Valid credentials
curl -u tester1:pilot_secret_1 http://localhost:8765/

# Wrong password → 401
curl -u tester1:wrongpass http://localhost:8765/

# Different user, different session
curl -u tester2:pilot_secret_2 http://localhost:8765/api/session?dir=tester1_session_path
# → 403 Forbidden (cross-user access denied)
```

### Session Ownership

Each authenticated user can only:
- Create sessions in their own namespace (`.artpkg/users/{username}/sessions/`)
- Read/modify their own sessions
- Upload files to their own sessions

Sessions created by tester1 are NOT accessible to tester2 or tester3.

## Directory Layout After Use

```
.artpkg/
└── users/
    ├── tester1/
    │   └── sessions/
    │       └── 2026-0831-pre-artifacts-{hash}/
    │           ├── session.json
    │           ├── answers.json
    │           ├── seed.json
    │           ├── source_pre_artifacts.md
    │           └── (projection outputs if generated)
    ├── tester2/
    │   └── sessions/
    └── tester3/
        └── sessions/
```

## Security Notes

- **Credentials**: Store securely. Never commit to Git.
- **HTTPS**: Not used in pilot. LAN-only deployment recommended.
- **Session Isolation**: Enforced at application level. Filesystem permissions also recommended.
- **Upload Limit**: 10 MiB per upload.
- **Temporary Files**: Automatically cleaned up after upload processing.

## Troubleshooting

### "No credentials configured"

Error: `ERROR: No credentials configured. Set ARTPKG_INTAKE_CREDENTIALS or ARTPKG_INTAKE_CREDENTIALS_FILE.`

**Solution**: Set one of the credential environment variables before starting the server.

### 401 Unauthorized

**Cause**: Missing or invalid Authorization header

**Solution**: Include credentials in request:
```bash
curl -u username:password http://localhost:8765/
```

### 403 Forbidden

**Cause**: Attempting to access another user's session

**Solution**: Only access sessions created by your authenticated user. Session paths are not user-guessable.

### Upload too large

Error: `"payload too large (max 10MiB)"`

**Solution**: Split your pre-artifacts file or remove unnecessary content.

## Testing the Pilot

### Single User Test
```bash
# Start server
export ARTPKG_INTAKE_CREDENTIALS='alice:pilot_secret_1'
python tools/artpkg_intake_server.py --workspace . --host 0.0.0.0 --port 8765

# Authenticate and create session
curl -u alice:pilot_secret_1 -F "file=@test.md" http://localhost:8765/api/intake
```

### Three-User Concurrent Test
```bash
# Configure three users
export ARTPKG_INTAKE_CREDENTIALS='tester1:pilot_secret_1,tester2:pilot_secret_2,tester3:pilot_secret_3'
python tools/artpkg_intake_server.py --workspace . --host 0.0.0.0 --port 8765

# In separate terminals, each user can:
curl -u tester1:pilot_secret_1 -F "file=@file1.md" http://localhost:8765/api/intake
curl -u tester2:pilot_secret_2 -F "file=@file2.md" http://localhost:8765/api/intake
curl -u tester3:pilot_secret_3 -F "file=@file3.md" http://localhost:8765/api/intake

# Verify cross-user access is blocked
curl -u tester1:pilot_secret_1 http://localhost:8765/api/session?dir=<tester2_session_path>
# → 403 Forbidden
```

## What's New in This Version

- **Authentication**: HTTP Basic Auth required on all routes
- **Session Ownership**: Each user can only access their own sessions
- **Session Namespace**: Sessions stored per-user (`.artpkg/users/{username}/sessions/`)
- **Upload Limits**: 10 MiB maximum upload size (checked before reading body)
- **Temp Cleanup**: Temporary upload directories automatically deleted
- **Audit Identity**: Authenticated username recorded instead of generic "UI reviewer"
- **Error Responses**:
  - 401 Unauthorized (missing/invalid auth)
  - 403 Forbidden (cross-user access)
  - 413 Payload Too Large (oversized upload)

## What Hasn't Changed

- Archify projection generation (same behavior)
- Archify viewer on :8666 (read-only, unchanged)
- File type validation (Markdown/text only)
- Authority model (intake UI doesn't grant implementation authority)
- Existing project review logic

## Next Steps (After Security Review)

1. LAN binding authorization
2. Three-user pilot testing
3. Concurrent session validation
4. Portainer deployment
5. Production hardening (HTTPS, audit logging, etc.)

---

For detailed implementation documentation, see [IMPLEMENTATION_REPORT.md](IMPLEMENTATION_REPORT.md).
