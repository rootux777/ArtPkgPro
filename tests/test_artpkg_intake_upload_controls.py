"""Tests for ArtPkg intake server upload controls."""
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))

import artpkg_intake_server as server


class UploadControlTests(unittest.TestCase):
    """Test upload size limits and file type validation."""
    
    def test_max_upload_size_constant(self):
        """MAX_UPLOAD_SIZE is configured to 10 MiB."""
        expected = 10 * 1024 * 1024
        self.assertEqual(expected, server.MAX_UPLOAD_SIZE)
    
    def test_max_upload_size_prevents_dos(self):
        """Upload size limit prevents memory exhaustion."""
        # Verify that the limit is less than 100 MiB (reasonable safety limit)
        self.assertLess(server.MAX_UPLOAD_SIZE, 100 * 1024 * 1024)
        
        # Verify that the limit is at least 1 MiB (allows typical files)
        self.assertGreaterEqual(server.MAX_UPLOAD_SIZE, 1 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
