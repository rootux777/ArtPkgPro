# Pipeline-A Phase 1 integration

## Runtime contract

ArtPkg invokes Pipeline-A only after the existing ArtPkg sealing gate returns `READY_TO_SEAL` and the human accepts the exact sealing confirmation. The server seals one immutable package, invokes Pipeline-A with a subprocess argument array, and treats Pipeline-A's durable `ADMISSION_RECEIPT.json` plus `ADMISSION_COMPLETE.json` as authoritative.

The integration does not grant implementation authority or dispatch semantic assessment, discovery, planning, packaging, implementation, deployment, or a general command API.

## Required configuration

All five variables are required. Admission fails closed if a path is absent, unreadable, non-executable where applicable, or if custody overlaps the sealed package directory.

```bash
PIPELINE_A_PYTHON=/home/rootux/.venvs/sdlc-harness-phase1-py311/bin/python
PIPELINE_A_ADMISSION_CLI=/home/rootux/Downloads/Pipeline-A/pipeline_artpkg_admission.py
PIPELINE_A_CUSTODY_ROOT=/var/lib/artpkg/pipeline-a-custody
SDLC_PHASE1_PYTHON=/home/rootux/.venvs/sdlc-harness-phase1-py311/bin/python
SDLC_PHASE1_CLI=/home/rootux/SDLC-Harness/tools/sdlc_artpkg_intake.py
```

`PIPELINE_A_CUSTODY_ROOT` must be dedicated writable storage outside the ArtPkg source tree and outside every sealed-package directory. The configured Python path is preserved as written so virtual-environment package resolution remains active.

The supplied `/home/rootux/pipeline-a-option-a-linux-amd64` path is a deployment bundle and does not contain `pipeline_artpkg_admission.py`. The authoritative source checkout currently containing the requested commit `5955e57c90421a131f59f3e1cf0278823b517c60` and tree `fb34f3452be07eef01b47f2d40bb7cf1ae55a35b` is `/home/rootux/Downloads/Pipeline-A`.

## Invocation boundary

The server executes this argv shape with `shell=False`, stdin disabled, a 60-second timeout, and inherited `PYTHONPATH` removed:

```text
PIPELINE_A_PYTHON
PIPELINE_A_ADMISSION_CLI
admit
--package SEALED_PACKAGE_DIRECTORY
--expected-package-sha256 MANIFEST_FILE_SHA256
--custody-root PIPELINE_A_CUSTODY_ROOT
--sdlc-python SDLC_PHASE1_PYTHON
--sdlc-cli SDLC_PHASE1_CLI
```

Package content is never placed in arguments, stdout, or stderr. A zero exit code is insufficient: ArtPkg independently loads the deterministic durable receipt path, validates its closed schema and completion-marker hash, and verifies package, submission, custody, handoff, output-path, status, authority, and next-action bindings.

## Current host deployment

The service runs directly on the host as `artpkg-intake.service`, under user and group `rootux`, with `NoNewPrivileges=true` and `PrivateTmp=true`. It is not containerized. The process can read host paths allowed to `rootux`; no mount changes are needed. Enabling admission requires adding the five variables to the systemd service environment and choosing/creating the dedicated custody directory. Applying those changes requires a separately authorized daemon reload and service restart.

## Container boundary

If ArtPkg is containerized later, use only these explicit mounts:

- sealed ArtPkg session storage, writable only as required for ArtPkg sealing;
- the Pipeline-A admission source or executable, read-only;
- the SDLC Phase 1 CLI, read-only;
- interpreter/runtime files required by those CLIs, read-only;
- one dedicated Pipeline-A custody mount, writable and separate from ArtPkg session storage.

Do not mount the Docker socket, use privileged mode, expose a general command API, or place custody under the ArtPkg source-package directory.
