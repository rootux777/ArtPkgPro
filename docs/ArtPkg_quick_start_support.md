# ArtPkg Quick Start (Support Staff)

Audience: on-call/support staff operating this host. Goal: get ArtPkg running and verify each moving part is actually up, using copy-pasteable terminal checks. This is an operational runbook, not a design document.

## Components On This Host

```text
ArtPkg container        -> host port 8555  (read-only status service, /healthz only)
Archify viewer container -> host port 8666  (read-only, serves already-delivered static HTML)
ArtPkg intake UI         -> local process, LAN pilot http://192.168.1.163:8765/ (not containerized, not always running)
```

The container never generates packages or accepts uploads over HTTP — that only happens via the CLI (`questionnaire ...`) or the local intake UI. See [container_deployment.md](container_deployment.md) for the full container contract.

## 0. Python Environment (pyenv)

This host uses `pyenv`. If `python` is not found even though `python3` works, the pyenv global version is likely set to `system` (which has no `python` binary).

```sh
pyenv versions
pyenv global
```

If `pyenv global` prints `system` and you need `python` to resolve, set a real version:

```sh
pyenv global 3.12.8
python --version
```

## 1. Verify The ArtPkg Container

Check the container is running:

```sh
sudo docker ps --filter name=artpkg --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'
```

Check its health endpoint directly (replace host/IP as needed):

```sh
curl -s -m 5 http://127.0.0.1:8555/healthz
curl -s -m 5 http://192.168.1.163:8555/healthz
```

Expected output:

```json
{"status":"ok","service":"artpkg","mode":"read-only-status"}
```

Check the container's own built-in healthcheck status:

```sh
sudo docker inspect --format '{{json .State.Health}}' artpkg
```

If the container isn't running, start the stack:

```sh
sudo docker compose -f compose.portainer.yml up -d
```

## 2. Verify The Archify Viewer Container

```sh
sudo docker ps --filter name=archify --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'
curl -s -m 5 -o /dev/null -w 'archify viewer HTTP %{http_code}\n' http://127.0.0.1:8666/
curl -s -m 5 -o /dev/null -w 'archify viewer HTTP %{http_code}\n' http://192.168.1.163:8666/
```

Expected: `archify viewer HTTP 200`. This container only serves already-delivered HTML; it does not run Archify commands and does not accept uploads.

## 3. Start And Verify The Local Intake UI (with Authentication)

The intake UI is not containerized and is not always running. It now requires HTTP Basic Authentication with three test users.

### 3a. Credentials Setup (Bounded Three-User LAN Pilot)

Create a credentials file before starting the server:

```sh
cat > artpkg-credentials.json <<'EOF'
{
  "tester1": "secret1",
  "tester2": "secret2",
  "tester3": "secret3"
}
EOF
```

This file contains credentials for the bounded three-user LAN pilot. Each user:
- Gets their own session namespace in `.artpkg/users/{username}/sessions/`
- Cannot access other users' sessions
- Has a 10 MiB upload size limit per request

See also: [.credentials.example.json](../../.credentials.example.json) for the canonical template.

### 3b. Starting the Server with Authentication

Start the intake server bound to all host interfaces for LAN access:

```sh
export ARTPKG_INTAKE_CREDENTIALS_FILE=./artpkg-credentials.json
export ARTPKG_ARCHIFY_ROOT=/home/rootux/Downloads/archifypro/archify
python tools/artpkg_intake_server.py --workspace . --host 0.0.0.0 --port 8765
```

Or as a one-liner:

```sh
ARTPKG_INTAKE_CREDENTIALS_FILE=./artpkg-credentials.json ARTPKG_ARCHIFY_ROOT=/home/rootux/Downloads/archifypro/archify python tools/artpkg_intake_server.py --workspace . --host 0.0.0.0 --port 8765
```

Expected output:

```text
ArtPkg intake UI running at http://0.0.0.0:8765/
Configured users: tester1, tester2, tester3
```

LAN users open `http://192.168.1.163:8765/`. The `0.0.0.0` address is only the server bind address and is not the address users enter in a browser. HTTP Basic Authentication is unencrypted, so this configuration is limited to the approved trusted-LAN test environment.

### 3c. Verify It's Listening

From another terminal, verify with Basic Auth:

```sh
# Unauthenticated request (should return 401 Unauthorized)
curl -s -m 3 -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:8765/

# Authenticated request (should return 200 OK)
curl -s -m 3 -u tester1:secret1 -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:8765/

# Authenticated request through the host LAN address (should return 200 OK)
curl -s -m 3 -u tester1:secret1 -o /dev/null -w 'LAN HTTP %{http_code}\n' http://192.168.1.163:8765/
```

Expected: the unauthenticated request returns `401`; both authenticated requests return `200`.

Or use `ss` to check the port is listening:

```sh
ss -ltnp 2>/dev/null | grep -E '8765|8555|8666'
```

To stop the intake UI, press `Ctrl+C` in the terminal running it, or find and stop the process:

```sh
pkill -f artpkg_intake_server.py
```

## 4. Operational Verification

Run the standard verifier from the ArtPkg workspace:

```sh
python tools/artpkg_operational_check.py
```

The default deep check verifies:

- the ArtPkg status service returns its exact read-only `/healthz` payload;
- the Archify viewer returns non-empty HTTP 200 content;
- the intake UI rejects unauthenticated access and accepts configured Basic Auth;
- the calculator regression fixture can create a new questionnaire session;
- Archify validation and HTML delivery succeed;
- the generated projection HTML is authenticated, fetchable, and non-empty.

Expected summary:

```text
ArtPkg operational check: PASS (... passed, ... warnings, 0 failed)
```

The optional browser visual check is reported as `WARN` when Chrome or Chromium is unavailable. Validation, delivery, or HTML-fetch failures are `FAIL`. The process exits `0` when operational and `1` when any required check fails.

Deep mode creates a probe session under `.artpkg/users/{username}/sessions/` using the regression fixture. For frequent non-mutating availability checks, use shallow mode:

```sh
python tools/artpkg_operational_check.py --shallow
```

For another local service or monitoring process, request machine-readable output and use the exit code:

```sh
python tools/artpkg_operational_check.py --json
```

Credentials are read from `artpkg-credentials.json` by default. Select another configured user with `--username`, another credentials file with `--credentials-file`, or provide the password through the `ARTPKG_OPERATIONAL_PASSWORD` environment variable. Passwords are never printed.

Endpoints and the smoke fixture are configurable, which allows this script to serve as a reference implementation for similar local applications:

```sh
python tools/artpkg_operational_check.py \
  --status-url http://127.0.0.1:8555/healthz \
  --viewer-url http://127.0.0.1:8666/ \
  --intake-url http://127.0.0.1:8765 \
  --fixture tests/fixtures/basic-windows-calculator_preartifacts.md
```

### Manual fallback

```sh
echo "-- ArtPkg container --"
sudo docker ps --filter name=artpkg --format '{{.Names}}\t{{.Status}}'
curl -s -m 5 http://127.0.0.1:8555/healthz; echo

echo "-- Archify viewer container --"
sudo docker ps --filter name=archify --format '{{.Names}}\t{{.Status}}'
curl -s -m 5 -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:8666/

echo "-- Local intake UI --"
curl -s -m 3 -u tester1:secret1 -o /dev/null -w 'HTTP %{http_code}\n' http://192.168.1.163:8765/
```

## Common Issues

- **`python: command not found` but `python3` works** → pyenv global is `system`. Run `pyenv global 3.12.8` (see Section 0).
- **`curl` to `8555`/`8666` times out** → container isn't running; check with `docker ps`, then `docker compose -f compose.portainer.yml up -d`.
- **Intake UI returns 401 Unauthorized** → credentials not provided. Use `curl -u tester1:secret1 http://127.0.0.1:8765/` to authenticate.
- **Server exits with "No credentials configured"** → credentials file not found or `ARTPKG_INTAKE_CREDENTIALS_FILE` not set. Verify file exists and path is correct.
- **Visualization reports that Archify is not configured** → set `ARTPKG_ARCHIFY_ROOT=/home/rootux/Downloads/archifypro/archify`, verify `bin/archify.mjs` exists there, and restart the intake server.
- **Visualization fails with `No such file or directory: 'node'`** → Node is missing from the intake server's `PATH`, not necessarily from the machine. Set `ARTPKG_NODE` to the absolute executable path reported by `command -v node`. For systemd, add `Environment=ARTPKG_NODE=/absolute/path/to/node` under `[Service]` in a service override, reload systemd, and restart `artpkg-intake.service`. Systemd does not load your shell's NVM configuration; update the override if that Node version is removed.
- **LAN clients cannot connect to port 8765** → confirm the server was started with `--host 0.0.0.0`, then check the host firewall permits TCP port `8765` from the trusted LAN only.
- **Each user must authenticate separately** → each session is isolated per user in `.artpkg/users/{username}/sessions/`. Users cannot access each other's sessions.
- **`docker ps` shows nothing at all** → confirm you're using `sudo docker ps` (rootless vs. root Docker context can differ per user).

## What This Is Not

This quick start does not cover generating or approving artifacts packages, the intake UI's review-queue workflow, or the ArtPkg↔Archify integration contract. See [README.md](../README.md) and [docs/superpowers/specs/](superpowers/specs/) for that.
