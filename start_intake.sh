#!/bin/bash
export ARTPKG_INTAKE_CREDENTIALS='tester1:secret1,tester2:secret2,tester3:secret3'
export ARTPKG_ARCHIFY_ROOT="${ARTPKG_ARCHIFY_ROOT:-/home/rootux/Downloads/archifypro/archify}"
export ARTPKG_NODE="${ARTPKG_NODE:-$(command -v node || echo node)}"
python tools/artpkg_intake_server.py --workspace . --host 0.0.0.0 --port 8765
