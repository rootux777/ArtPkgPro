"""Tests for ArtPkg intake server authentication."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from base64 import b64encode

import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))

import artpkg_intake_server as server
import artpkg_intake_auth as auth


class AuthenticationTests(unittest.TestCase):
    """Test authentication and authorization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_credentials = {
            "tester1": "secret1",
            "tester2": "secret2",
            "tester3": "secret3",
        }
        
    def test_validate_basic_auth_missing_header(self):
        """Unauthenticated request with no Authorization header returns None."""
        result = auth.validate_basic_auth("")
        self.assertIsNone(result)
    
    def test_validate_basic_auth_invalid_scheme(self):
        """Authorization header with wrong scheme returns None."""
        result = auth.validate_basic_auth("Bearer token123")
        self.assertIsNone(result)
    
    def test_validate_basic_auth_invalid_encoding(self):
        """Invalid base64 in Authorization header returns None."""
        result = auth.validate_basic_auth("Basic !!!")
        self.assertIsNone(result)
    
    def test_validate_basic_auth_missing_colon(self):
        """Authorization without colon separator returns None."""
        encoded = b64encode(b"user_without_colon").decode()
        result = auth.validate_basic_auth(f"Basic {encoded}")
        self.assertIsNone(result)
    
    def test_validate_basic_auth_valid(self):
        """Valid credentials return username."""
        with patch.dict(os.environ, {"ARTPKG_INTAKE_CREDENTIALS": "alice:secret1"}):
            encoded = b64encode(b"alice:secret1").decode()
            result = auth.validate_basic_auth(f"Basic {encoded}")
            self.assertEqual("alice", result)
    
    def test_validate_basic_auth_wrong_password(self):
        """Correct username but wrong password returns None."""
        with patch.dict(os.environ, {"ARTPKG_INTAKE_CREDENTIALS": "alice:secret1"}):
            encoded = b64encode(b"alice:wrongpass").decode()
            result = auth.validate_basic_auth(f"Basic {encoded}")
            self.assertIsNone(result)
    
    def test_validate_basic_auth_unknown_user(self):
        """Unknown username returns None."""
        with patch.dict(os.environ, {"ARTPKG_INTAKE_CREDENTIALS": "alice:secret1"}):
            encoded = b64encode(b"bob:secret1").decode()
            result = auth.validate_basic_auth(f"Basic {encoded}")
            self.assertIsNone(result)
    
    def test_load_credentials_from_env(self):
        """Load credentials from environment variable."""
        with patch.dict(os.environ, {"ARTPKG_INTAKE_CREDENTIALS": "alice:secret1,bob:secret2"}):
            creds = auth.load_credentials_from_env()
            self.assertEqual({"alice": "secret1", "bob": "secret2"}, creds)
    
    def test_load_credentials_from_file(self):
        """Load credentials from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_file = Path(tmpdir) / "credentials.json"
            creds_file.write_text(json.dumps({"alice": "secret1", "bob": "secret2"}))
            
            creds = auth.load_credentials_from_file(creds_file)
            self.assertEqual({"alice": "secret1", "bob": "secret2"}, creds)
    
    def test_load_credentials_from_missing_file(self):
        """Load credentials from non-existent file returns empty dict."""
        creds = auth.load_credentials_from_file("/nonexistent/path.json")
        self.assertEqual({}, creds)
    
    def test_get_configured_credentials_file_priority(self):
        """Credentials file has priority over environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_file = Path(tmpdir) / "credentials.json"
            creds_file.write_text(json.dumps({"alice": "file_secret"}))
            
            with patch.dict(os.environ, {
                "ARTPKG_INTAKE_CREDENTIALS_FILE": str(creds_file),
                "ARTPKG_INTAKE_CREDENTIALS": "bob:env_secret"
            }):
                creds = auth.get_configured_credentials()
                self.assertEqual({"alice": "file_secret"}, creds)
    
    def test_sanitize_username_valid(self):
        """Valid usernames pass through unchanged (lowercase)."""
        self.assertEqual("tester1", auth.sanitize_username("Tester1"))
        self.assertEqual("tester_1", auth.sanitize_username("tester_1"))
        self.assertEqual("tester-1", auth.sanitize_username("tester-1"))
    
    def test_sanitize_username_invalid_chars(self):
        """Special characters are stripped."""
        self.assertEqual("tester1", auth.sanitize_username("tester@1$"))
        self.assertEqual("test", auth.sanitize_username("@#test$%"))
    
    def test_sanitize_username_empty_after_sanitize(self):
        """Sanitization that results in empty string raises ValueError."""
        with self.assertRaises(ValueError):
            auth.sanitize_username("@#$%^&*()")
    
    def test_constant_time_compare_equal(self):
        """Equal strings compare as equal."""
        self.assertTrue(auth.constant_time_compare("test", "test"))
    
    def test_constant_time_compare_not_equal(self):
        """Different strings compare as not equal."""
        self.assertFalse(auth.constant_time_compare("test", "wrong"))


class CredentialStorageTests(unittest.TestCase):
    """Test that credentials are not logged or exposed."""
    
    def test_no_credentials_in_validate_basic_auth_exceptions(self):
        """Validate_basic_auth does not raise exceptions containing credentials."""
        try:
            auth.validate_basic_auth("Basic !!!invalid!!!")
        except Exception as e:
            # If an exception is raised, it should not contain encoded credentials
            self.assertNotIn("Basic", str(e))
            self.assertNotIn("Authorization", str(e))


if __name__ == "__main__":
    unittest.main()
