# ArtPkg Container Deployment

This container layer packages the current ArtPkg v0.3 functional baseline for a standalone Linux runtime image tagged `artpkg:0.3.1-linux-amd64`. The `0.3.1` tag is a containerization reconciliation tag derived from the current v0.3 source behavior; formal package versioning remains separate.

The image keeps the ArtPkg roles separate:

- `artpkg serve` runs only the read-only HTTP status service.
- `artpkg healthcheck` checks the local status service.
- `artpkg questionnaire ...` runs the existing CLI package-generation and validation commands.

The default container command is `artpkg serve --host 0.0.0.0 --port 8080`.

## Build

```sh
docker build --platform linux/amd64 -t artpkg:0.3.1-linux-amd64 .
```

Do not rebuild or retag `artpkg:0.3-linux-amd64`; it remains the rollback image.

## Read-Only Status Service

The container exposes only read-only status over HTTP:

```text
GET /healthz
```

Expected response:

```json
{"status":"ok","service":"artpkg","mode":"read-only-status"}
```

The status service does not generate packages, accept uploads, change review state, modify sessions, invoke Archify, execute commands, or grant authority.

## Persistent Storage

The runtime data contract is:

```text
/data/input
/data/output
```

For LittleEngine, Portainer mounts host storage as:

```text
/home/rootux/artpkg-data:/data
```

This host path belongs in deployment configuration only. It is not hard-coded in application source.

Canonical compact outputs remain:

```text
artifacts_package_answers.json
artifacts_package.md
artifacts_package_validation.md
```

## Portainer Stack Configuration

Use [compose.portainer.yml](../compose.portainer.yml) as the LittleEngine stack definition.

The stack supports environment variable configuration for portability:

| Variable | Default | Purpose |
|----------|---------|---------|
| `ARTPKG_DATA_PATH` | `/home/rootux/artpkg-data` | Host data directory bind mount source |
| `ARTPKG_BIND_ADDRESS` | `127.0.0.1` | Container port binding address (loopback-only by default for security) |
| `ARTPKG_PORT` | `8555` | Published port number on host |

**Default behavior** (loopback-only, LittleEngine compatible):
```yaml
ARTPKG_BIND_ADDRESS=127.0.0.1
ARTPKG_PORT=8555
ARTPKG_DATA_PATH=/home/rootux/artpkg-data
# Result: 127.0.0.1:8555:8080 (local access only)
```

**For remote LAN browser access** (after network security review):
```bash
export ARTPKG_BIND_ADDRESS=0.0.0.0
docker compose -f compose.portainer.yml up -d
# Result: 0.0.0.0:8555:8080 (all interfaces)
```

**For custom data directory**:
```bash
export ARTPKG_DATA_PATH=/mnt/artpkg-storage
docker compose -f compose.portainer.yml up -d
```

The stack keeps the proven local-image deployment model:

```text
image: artpkg:0.3.1-linux-amd64
pull_policy: never
${ARTPKG_BIND_ADDRESS:-127.0.0.1}:${ARTPKG_PORT:-8555}:8080
${ARTPKG_DATA_PATH:-/home/rootux/artpkg-data}:/data
```

The stack intentionally does not include `security_opt: ["no-new-privileges:true"]` because that setting was incompatible with the LittleEngine Snap Docker/AppArmor environment.

## Runtime User and Security

The image defines a non-root `artpkg` user by default. The LittleEngine Compose file overrides the runtime identity to `1000:1000` so the process can write to the existing bind-mounted data directory.

The Compose security controls are:

```text
user: "1000:1000"
read_only: true
tmpfs: /tmp
cap_drop: ALL
privileged: false
```

The Compose file does not mount `/var/run/docker.sock`, does not use host networking, and does not use the host PID namespace.

## CLI Generation Example

Package generation remains a CLI/application function. Use an existing answer file under `/data/input` and write generated artifacts under `/data/output`:

```sh
docker run --rm \
  --platform linux/amd64 \
  --user 1000:1000 \
  --read-only \
  --tmpfs /tmp \
  --cap-drop ALL \
  -v "$PWD/test-data:/data" \
  artpkg:0.3.1-linux-amd64 \
  questionnaire generate --answers /data/input/artifacts_package_answers.json --yes
```

Do not use the status HTTP service as a generation interface.

## Save and Transfer

For local-image Portainer deployment, no registry is required:

```sh
docker save artpkg:0.3.1-linux-amd64 -o artpkg-0.3.1-linux-amd64.tar
sha256sum artpkg-0.3.1-linux-amd64.tar
docker load -i artpkg-0.3.1-linux-amd64.tar
```

Only update the Portainer stack after independent review and explicit deployment authorization.