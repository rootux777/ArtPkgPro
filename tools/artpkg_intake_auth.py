"""Authentication and authorization for ArtPkg LAN intake WebUI."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Optional, Tuple


def load_credentials_from_env() -> dict[str, str]:
    """
    Load credentials from environment variable.
    
    Format: ARTPKG_INTAKE_CREDENTIALS=alice:secret1,bob:secret2,tester3:secret3
    
    Returns: {username: password_hash, ...}
    """
    creds_env = os.environ.get('ARTPKG_INTAKE_CREDENTIALS', '')
    if not creds_env:
        return {}
    
    credentials = {}
    for entry in creds_env.split(','):
        entry = entry.strip()
        if not entry or ':' not in entry:
            continue
        username, password = entry.split(':', 1)
        username = username.strip()
        password = password.strip()
        if username and password:
            credentials[username] = password
    
    return credentials


def load_credentials_from_file(filepath: str | Path) -> dict[str, str]:
    """
    Load credentials from a JSON file.
    
    Format:
    {
      "alice": "secret1",
      "bob": "secret2",
      "tester3": "secret3"
    }
    
    Returns: {username: password, ...}
    """
    try:
        content = Path(filepath).read_text(encoding='utf-8')
        return json.loads(content)
    except Exception:
        return {}


def get_configured_credentials() -> dict[str, str]:
    """
    Get credentials from configured source.
    
    Priority:
    1. ARTPKG_INTAKE_CREDENTIALS_FILE (JSON file path)
    2. ARTPKG_INTAKE_CREDENTIALS (env string)
    3. Empty dict (no credentials)
    """
    creds_file = os.environ.get('ARTPKG_INTAKE_CREDENTIALS_FILE')
    if creds_file:
        return load_credentials_from_file(creds_file)
    
    return load_credentials_from_env()


def constant_time_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.
    """
    return hmac.compare_digest(a, b)


def validate_basic_auth(auth_header: str) -> Optional[str]:
    """
    Validate HTTP Basic Authentication header.
    
    Format: Authorization: Basic base64(username:password)
    
    Returns: username if valid, None otherwise
    
    Does NOT log the header value or decoded credentials.
    """
    if not auth_header or not auth_header.startswith('Basic '):
        return None
    
    try:
        encoded = auth_header[6:]  # Strip 'Basic '
        decoded = base64.b64decode(encoded).decode('utf-8')
        
        if ':' not in decoded:
            return None
        
        username, password = decoded.split(':', 1)
        username = username.strip()
        password = password.strip()
        
        if not username or not password:
            return None
        
        # Get configured credentials
        credentials = get_configured_credentials()
        
        # Check if username exists
        if username not in credentials:
            return None
        
        # Compare password in constant time
        if constant_time_compare(password, credentials[username]):
            return username
        
        return None
    
    except Exception:
        return None


def sanitize_username(username: str, max_length: int = 64) -> str:
    """
    Sanitize username for filesystem use.
    
    - Convert to lowercase
    - Keep only alphanumeric, hyphen, underscore
    - Truncate to max_length
    - Return original if invalid
    """
    sanitized = ''.join(c.lower() for c in username if c.isalnum() or c in '-_')
    
    if not sanitized:
        raise ValueError(f"Invalid username: {username}")
    
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized
