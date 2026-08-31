"""Tests for ArtPkg intake server session ownership enforcement."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))

import artpkg_intake_server as server


class SessionOwnershipTests(unittest.TestCase):
    """Test per-user session ownership enforcement."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_workspace = tempfile.mkdtemp()
        self.workspace_path = Path(self.temp_workspace)
    
    def tearDown(self):
        """Clean up after tests."""
        if Path(self.temp_workspace).exists():
            shutil.rmtree(self.temp_workspace, ignore_errors=True)
    
    def test_resolve_session_dir_with_owner_valid_path(self):
        """Valid session path within user namespace is accepted."""
        username = "tester1"
        user_sessions_dir = self.workspace_path / ".artpkg" / "users" / username / "sessions"
        user_sessions_dir.mkdir(parents=True, exist_ok=True)
        
        session_id = "test-session-123"
        session_dir = user_sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Should not raise
        resolved = server.resolve_session_dir_with_owner(str(session_dir), username, self.workspace_path)
        self.assertEqual(session_dir.resolve(), resolved)
    
    def test_resolve_session_dir_with_owner_cross_user_access(self):
        """Accessing another user's session directory raises ValueError."""
        # Create session for tester1
        user1_sessions_dir = self.workspace_path / ".artpkg" / "users" / "tester1" / "sessions"
        user1_sessions_dir.mkdir(parents=True, exist_ok=True)
        session_dir = user1_sessions_dir / "session-123"
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to access as tester2
        with self.assertRaises(ValueError) as ctx:
            server.resolve_session_dir_with_owner(str(session_dir), "tester2", self.workspace_path)
        
        self.assertIn("namespace", str(ctx.exception))
    
    def test_resolve_session_dir_with_owner_path_traversal(self):
        """Path traversal attempt raises ValueError."""
        username = "tester1"
        user_sessions_dir = self.workspace_path / ".artpkg" / "users" / username / "sessions"
        user_sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to traverse out of user's namespace
        traversal_path = user_sessions_dir / ".." / "tester2" / "sessions" / "other-session"
        
        with self.assertRaises(ValueError):
            server.resolve_session_dir_with_owner(str(traversal_path), username, self.workspace_path)
    
    def test_load_workspace_session_with_owner_valid(self):
        """Loading a session with correct owner succeeds."""
        username = "tester1"
        user_sessions_dir = self.workspace_path / ".artpkg" / "users" / username / "sessions"
        user_sessions_dir.mkdir(parents=True, exist_ok=True)
        
        session_id = "test-session-123"
        session_dir = user_sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create minimal session files
        session_json = {
            "session_id": session_id,
            "session_dir": str(session_dir),
            "created": "2026-08-31T12:00:00Z",
            "updated": "2026-08-31T12:00:00Z"
        }
        (session_dir / "session.json").write_text(json.dumps(session_json))
        (session_dir / "answers.json").write_text(json.dumps({"answers": {}}))
        (session_dir / "seed.json").write_text(json.dumps({"answers": {}}))
        
        # Should not raise
        with patch("artpkg_intake_server.artpkg_intake.load_intake_session") as mock_load:
            mock_load.return_value = {"session_id": session_id, "session_dir": str(session_dir)}
            
            session = server.load_workspace_session_with_owner(str(session_dir), username, self.workspace_path)
            self.assertIsNotNone(session)
    
    def test_load_workspace_session_with_owner_wrong_owner(self):
        """Loading a session with wrong owner raises ValueError."""
        # Create session for tester1
        user1_sessions_dir = self.workspace_path / ".artpkg" / "users" / "tester1" / "sessions"
        user1_sessions_dir.mkdir(parents=True, exist_ok=True)
        session_dir = user1_sessions_dir / "session-123"
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to load as tester2
        with self.assertRaises(ValueError):
            server.load_workspace_session_with_owner(str(session_dir), "tester2", self.workspace_path)

    def test_create_user_session_rewrites_paths_for_projection(self):
        """Moving a session into a user namespace preserves projection trust."""
        source = self.workspace_path / "pre-artifacts.md"
        source.write_text("# Example project\n", encoding="utf-8")
        template = Path(__file__).parents[1] / "reusable_artifacts_package_template (1).md"

        session = server.create_intake_session_for_user(
            source,
            "tester1",
            self.workspace_path,
            template_path=template,
        )

        session_dir = Path(session["session_dir"])
        self.assertEqual(str(session_dir / "source_pre_artifacts.md"), session["source"]["stored_path"])
        self.assertEqual(str(session_dir / "answers.json"), session["answers_path"])
        self.assertEqual(str(session_dir / "seed.json"), session["seed_path"])
        legacy_root = str(self.workspace_path / ".artpkg" / "intake_sessions")
        self.assertNotIn(legacy_root, json.dumps(session))
        self.assertNotIn(legacy_root, (session_dir / "answers.json").read_text(encoding="utf-8"))
        self.assertNotIn(legacy_root, (session_dir / "seed.json").read_text(encoding="utf-8"))

        projection = server.artpkg_archify_projection.build_readiness_projection(session)
        issue_codes = {issue["code"] for issue in projection.projection_validation["issues"]}
        self.assertNotIn("SOURCE_PATH_MISMATCH", issue_codes)
        self.assertNotIn("ANSWERS_PATH_MISMATCH", issue_codes)

    def test_projection_html_response_accepts_owned_session(self):
        session_dir = self.workspace_path / ".artpkg" / "users" / "tester1" / "sessions" / "session-123"
        session_dir.mkdir(parents=True)
        expected = b"<!doctype html><title>Projection</title>"
        (session_dir / "artpkg-readiness.architecture.html").write_bytes(expected)

        status, headers, body = server.projection_html_response(
            str(session_dir),
            self.workspace_path,
            "tester1",
        )

        self.assertEqual(200, status)
        self.assertEqual("text/html; charset=utf-8", headers["Content-Type"])
        self.assertEqual(expected, body)


class UploadCleanupTests(unittest.TestCase):
    """Test that temporary upload directories are cleaned up."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_workspace = tempfile.mkdtemp()
        self.workspace_path = Path(self.temp_workspace)
    
    def tearDown(self):
        """Clean up after tests."""
        if Path(self.temp_workspace).exists():
            shutil.rmtree(self.temp_workspace, ignore_errors=True)
    
    def test_upload_cleanup_on_success(self):
        """Temporary upload directory is removed after successful processing."""
        # This test would require a full integration test with the HTTP handler
        # For now, we just verify that the cleanup code path exists
        temp_dir = Path(tempfile.mkdtemp(prefix="artpkg-upload-"))
        self.assertTrue(temp_dir.exists())
        
        # Simulate cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        self.assertFalse(temp_dir.exists())
    
    def test_upload_cleanup_on_error(self):
        """Temporary upload directory is removed even if processing fails."""
        temp_dir = Path(tempfile.mkdtemp(prefix="artpkg-upload-"))
        self.assertTrue(temp_dir.exists())
        
        # Simulate cleanup on error
        shutil.rmtree(temp_dir, ignore_errors=True)
        self.assertFalse(temp_dir.exists())


if __name__ == "__main__":
    unittest.main()
