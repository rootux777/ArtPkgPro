import http.client
import json
import re
import sys
import threading
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import artifacts_package_questionnaire as questionnaire
import artpkg_status_server as status_server


class ContainerizationContractTests(unittest.TestCase):
    def test_dockerfile_uses_python_310_non_root_status_entrypoint(self):
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

        self.assertIn("python:3.10-slim", dockerfile)
        self.assertIn("pip install --no-cache-dir -r requirements.txt", dockerfile)
        self.assertIn("mkdir -p /data/input /data/output", dockerfile)
        self.assertIn("EXPOSE 8080", dockerfile)
        self.assertIn("USER artpkg:artpkg", dockerfile)
        self.assertIn('ENTRYPOINT ["artpkg"]', dockerfile)
        self.assertIn('CMD ["serve", "--host", "0.0.0.0", "--port", "8080"]', dockerfile)
        self.assertNotIn("no-new-privileges", dockerfile)

    def test_compose_preserves_littleengine_runtime_contract(self):
        compose = (ROOT / "compose.portainer.yml").read_text(encoding="utf-8")

        self.assertIn("image: artpkg:0.3.1-linux-amd64", compose)
        self.assertIn("pull_policy: never", compose)
        self.assertIn('user: "1000:1000"', compose)
        # Port binding uses environment variables for configurability
        self.assertIn("${ARTPKG_BIND_ADDRESS:-127.0.0.1}:${ARTPKG_PORT:-8555}:8080", compose)
        # Data path uses environment variable for portability
        self.assertIn("${ARTPKG_DATA_PATH:-/home/rootux/artpkg-data}", compose)
        self.assertIn("target: /data", compose)
        self.assertIn("read_only: true", compose)
        self.assertRegex(compose, r"tmpfs:\s*\n\s*- /tmp")
        self.assertRegex(compose, r"cap_drop:\s*\n\s*- ALL")
        self.assertIn("privileged: false", compose)
        self.assertNotIn("privileged: true", compose)
        self.assertNotIn("/var/run/docker.sock", compose)
        self.assertNotIn("network_mode: host", compose)
        self.assertNotIn("pid: host", compose)
        self.assertNotIn("no-new-privileges", compose)

    def test_status_server_healthz_contract_and_no_mutation_methods(self):
        server = status_server.ThreadingHTTPServer(("127.0.0.1", 0), status_server.StatusHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
            connection.request("GET", "/healthz")
            response = connection.getresponse()
            body = response.read().decode("utf-8")
            self.assertEqual(200, response.status)
            self.assertEqual(status_server.STATUS_PAYLOAD, json.loads(body))

            connection.request("POST", "/api/intake", body=b"{}")
            response = connection.getresponse()
            self.assertEqual(405, response.status)
            self.assertEqual({"error": "method not allowed"}, json.loads(response.read().decode("utf-8")))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_status_server_has_no_mutable_http_route_names(self):
        source = (TOOLS / "artpkg_status_server.py").read_text(encoding="utf-8")

        self.assertNotIn("/api/intake", source)
        self.assertNotIn("/api/session", source)
        self.assertNotIn("build_projection_summary", source)
        self.assertNotIn("artpkg_intake_server", source)
        self.assertNotIn("artpkg_archify", source)

    def test_canonical_output_names_remain_unchanged(self):
        source = (TOOLS / "artifacts_package_questionnaire.py").read_text(encoding="utf-8")

        self.assertIn('"artifacts_package_answers.json"', source)
        self.assertIn('"artifacts_package.md"', source)
        self.assertIn('"artifacts_package_validation.md"', source)
        self.assertEqual("0.2", questionnaire.SCHEMA_VERSION)

    def test_dockerignore_excludes_runtime_and_generated_state(self):
        dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")

        for pattern in [
            ".git",
            ".artpkg",
            "**/.artpkg",
            "__pycache__/",
            "*.pyc",
            ".pytest_cache/",
            ".venv/",
            "venv/",
            "*.log",
            "artifacts_package_answers.json",
            "artifacts_package.md",
            "artifacts_package_validation.md",
            "artpkg-data/",
            "data/",
        ]:
            self.assertIn(pattern, dockerignore)

    def test_runtime_dependencies_remain_declared(self):
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

        self.assertIn("jsonschema", requirements)
        self.assertIn("COPY requirements.txt ./", dockerfile)
        self.assertIn("-r requirements.txt", dockerfile)


if __name__ == "__main__":
    unittest.main()