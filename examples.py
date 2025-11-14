#!/usr/bin/env python3
"""
Example script demonstrating how to use Git Client as a Python library
"""
from git_client import (
    GitOperations,
    BranchManager,
    HistoryViewer,
    SSHKeyManager,
    ConfigManager
)


def example_basic_workflow():
    """Example: Basic Git workflow"""
    print("=== Example 1: Basic Git Workflow ===\n")

    # Initialize a repository
    git_ops = GitOperations("./example_repo")
    success, msg = git_ops.init()
    print(f"Init: {msg}")

    # Add files
    success, msg = git_ops.add(all_files=True)
    print(f"Add: {msg}")

    # Commit
    success, msg = git_ops.commit("Initial commit", "Your Name", "your@email.com")
    print(f"Commit: {msg}")

    # Check status
    success, status = git_ops.status()
    print(f"Status: Branch={status['branch']}, Clean={len(status['unstaged']) == 0}")

    print()


def example_branch_management():
    """Example: Branch management"""
    print("=== Example 2: Branch Management ===\n")

    branch_mgr = BranchManager("./example_repo")

    # Create a new branch
    success, msg = branch_mgr.create_branch("feature/new-feature")
    print(f"Create branch: {msg}")

    # Switch to the branch
    success, msg = branch_mgr.switch_branch("feature/new-feature")
    print(f"Switch branch: {msg}")

    # List all branches
    success, branches = branch_mgr.list_branches()
    print("Branches:")
    for branch in branches:
        current = "* " if branch['current'] else "  "
        print(f"{current}{branch['name']} ({branch['commit']})")

    # Switch back to main
    success, msg = branch_mgr.switch_branch("main", create=True)
    print(f"Switch to main: {msg}")

    print()


def example_history_viewing():
    """Example: View history"""
    print("=== Example 3: View History ===\n")

    history = HistoryViewer("./example_repo")

    # Get commit log
    success, commits = history.log(max_count=5)
    if success:
        print("Recent commits:")
        for commit in commits:
            print(f"  {commit['hash']} - {commit['message']}")
            print(f"  Author: {commit['author']}")
            print(f"  Date: {commit['date']}\n")

    # Get diff
    success, diff_text = history.diff()
    if success and diff_text != "No differences found":
        print("Changes:")
        print(diff_text[:200])  # Print first 200 chars

    print()


def example_ssh_management():
    """Example: SSH key management"""
    print("=== Example 4: SSH Key Management ===\n")

    ssh_mgr = SSHKeyManager()

    # Check if SSH key exists
    if ssh_mgr.check_ssh_key_exists():
        print("SSH key exists")

        # Show public key
        pub_key = ssh_mgr.get_public_key()
        print(f"Public key (first 50 chars): {pub_key[:50]}...")

        # Test GitHub connection
        success, msg = ssh_mgr.test_github_connection()
        print(f"GitHub connection: {msg}")
    else:
        print("No SSH key found. Generate one with:")
        print("  gitc ssh keygen --email your@email.com")

    print()


def example_config_management():
    """Example: Configuration management"""
    print("=== Example 5: Configuration Management ===\n")

    config = ConfigManager()

    # Set configuration values
    config.set("user.name", "John Doe")
    config.set("user.email", "john@example.com")

    # Get configuration values
    name = config.get("user.name")
    email = config.get("user.email")
    print(f"User: {name} <{email}>")

    # List all configuration
    print("\nAll configuration:")
    all_config = config.list_config()
    print(f"  Defaults: {all_config.get('defaults')}")
    print(f"  Preferences: {all_config.get('preferences')}")

    print()


def example_complete_workflow():
    """Example: Complete workflow from init to push"""
    print("=== Example 6: Complete Workflow ===\n")

    # Note: This is a demonstration. Actual push requires valid GitHub repo

    git_ops = GitOperations("./my_project")

    # Initialize
    print("1. Initializing repository...")
    git_ops.init()

    # Add remote
    print("2. Adding remote...")
    git_ops.add_remote("origin", "git@github.com:username/my_project.git")

    # List remotes
    success, remotes = git_ops.list_remotes()
    print(f"   Remotes: {[r['name'] for r in remotes]}")

    # Create a file (simulated - you would actually create files)
    print("3. Adding files...")
    # In real usage, you'd create actual files here

    # Add all files
    git_ops.add(all_files=True)

    # Commit
    print("4. Committing...")
    git_ops.commit("Initial commit", "Your Name", "your@email.com")

    # Push (would actually push if remote is valid)
    print("5. Ready to push to remote")
    print("   Command: gitc push -u origin main")

    print()


if __name__ == "__main__":
    print("Git Client - Python Library Examples\n")
    print("=" * 50)
    print()

    # Run examples (comment out the ones you don't want to run)

    # example_basic_workflow()
    # example_branch_management()
    # example_history_viewing()
    example_ssh_management()
    example_config_management()
    # example_complete_workflow()

    print("=" * 50)
    print("\nFor more examples, see the README.md file")
    print("For CLI usage, run: gitc --help")
