#!/bin/bash
export ARTPKG_INTAKE_CREDENTIALS='tester1:secret1,tester2:secret2,tester3:secret3'
python tools/artpkg_intake_server.py --workspace . --port 8765
