"""
SSH Key Management Module
Handles SSH key generation, detection, and configuration for Git operations
"""
import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


class SSHKeyManager:
    """Manages SSH keys for Git authentication"""

    def __init__(self, key_path: Optional[str] = None):
        """
        Initialize SSH Key Manager

        Args:
            key_path: Custom path to SSH key. Defaults to ~/.ssh/id_rsa
        """
        self.ssh_dir = Path.home() / ".ssh"
        if key_path:
            self.private_key_path = Path(key_path)
        else:
            self.private_key_path = self.ssh_dir / "id_rsa"
        self.public_key_path = Path(str(self.private_key_path) + ".pub")

    def check_ssh_key_exists(self) -> bool:
        """
        Check if SSH key pair exists

        Returns:
            True if both private and public keys exist
        """
        return self.private_key_path.exists() and self.public_key_path.exists()

    def generate_ssh_key(self, email: str, overwrite: bool = False) -> Tuple[bool, str]:
        """
        Generate a new SSH key pair

        Args:
            email: Email address for the key
            overwrite: Whether to overwrite existing keys

        Returns:
            Tuple of (success, message)
        """
        if self.check_ssh_key_exists() and not overwrite:
            return False, f"SSH key already exists at {self.private_key_path}"

        # Create .ssh directory if it doesn't exist
        self.ssh_dir.mkdir(mode=0o700, exist_ok=True)

        try:
            # Generate RSA key pair
            key = rsa.generate_private_key(
                backend=default_backend(),
                public_exponent=65537,
                key_size=4096
            )

            # Write private key
            private_pem = key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.OpenSSH,
                encryption_algorithm=serialization.NoEncryption()
            )

            with open(self.private_key_path, 'wb') as f:
                f.write(private_pem)
            os.chmod(self.private_key_path, 0o600)

            # Write public key
            public_key = key.public_key()
            public_ssh = public_key.public_bytes(
                encoding=serialization.Encoding.OpenSSH,
                format=serialization.PublicFormat.OpenSSH
            )

            with open(self.public_key_path, 'wb') as f:
                f.write(public_ssh + f" {email}".encode())
            os.chmod(self.public_key_path, 0o644)

            return True, f"SSH key generated successfully at {self.private_key_path}"

        except Exception as e:
            return False, f"Error generating SSH key: {str(e)}"

    def get_public_key(self) -> Optional[str]:
        """
        Get the public key content

        Returns:
            Public key content or None if not found
        """
        if not self.public_key_path.exists():
            return None

        try:
            with open(self.public_key_path, 'r') as f:
                return f.read().strip()
        except Exception:
            return None

    def add_key_to_ssh_agent(self) -> Tuple[bool, str]:
        """
        Add SSH key to ssh-agent

        Returns:
            Tuple of (success, message)
        """
        if not self.private_key_path.exists():
            return False, "SSH key not found"

        try:
            # Start ssh-agent if not running
            try:
                subprocess.run(
                    ["ssh-add", "-l"],
                    check=False,
                    capture_output=True
                )
            except FileNotFoundError:
                return False, "ssh-add command not found. Please install OpenSSH."

            # Add key to agent
            result = subprocess.run(
                ["ssh-add", str(self.private_key_path)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return True, "SSH key added to agent successfully"
            else:
                return False, f"Failed to add key to agent: {result.stderr}"

        except Exception as e:
            return False, f"Error adding key to agent: {str(e)}"

    def test_github_connection(self) -> Tuple[bool, str]:
        """
        Test SSH connection to GitHub

        Returns:
            Tuple of (success, message)
        """
        try:
            result = subprocess.run(
                ["ssh", "-T", "git@github.com", "-o", "StrictHostKeyChecking=no"],
                capture_output=True,
                text=True,
                timeout=10
            )

            # GitHub returns exit code 1 even on successful auth
            # Check if the output contains success message
            output = result.stdout + result.stderr
            if "successfully authenticated" in output.lower():
                return True, "GitHub SSH connection successful"
            elif "permission denied" in output.lower():
                return False, "GitHub SSH connection failed: Permission denied. Please add your SSH key to GitHub."
            else:
                return False, f"GitHub SSH connection test inconclusive: {output}"

        except subprocess.TimeoutExpired:
            return False, "GitHub SSH connection timed out"
        except Exception as e:
            return False, f"Error testing GitHub connection: {str(e)}"

    def setup_ssh_config(self) -> Tuple[bool, str]:
        """
        Setup SSH config for GitHub

        Returns:
            Tuple of (success, message)
        """
        config_path = self.ssh_dir / "config"
        github_config = """
# GitHub SSH Configuration
Host github.com
    HostName github.com
    User git
    IdentityFile {}
    IdentitiesOnly yes
""".format(self.private_key_path)

        try:
            # Read existing config
            existing_config = ""
            if config_path.exists():
                with open(config_path, 'r') as f:
                    existing_config = f.read()

            # Check if GitHub config already exists
            if "Host github.com" not in existing_config:
                with open(config_path, 'a') as f:
                    f.write(github_config)
                os.chmod(config_path, 0o600)
                return True, "SSH config updated for GitHub"
            else:
                return True, "GitHub SSH config already exists"

        except Exception as e:
            return False, f"Error updating SSH config: {str(e)}"
