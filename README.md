# Git Client - Simple Git Client with SSH Support

English | [简体中文](README_CN.md)

A simple, user-friendly Git client built with Python that provides essential Git functionality with full SSH support for GitHub. Perfect for learning Git internals or as a lightweight alternative to the standard Git CLI.

## Features

### Core Functionality
- **Basic Git Operations**: init, clone, add, commit, push, pull
- **Branch Management**: create, switch, delete, merge branches
- **History Viewing**: log, diff, status, show commits
- **Remote Management**: add and list remote repositories
- **SSH Key Management**: generate, manage, and test SSH keys
- **Configuration Management**: persistent user settings

### Highlights
- Beautiful terminal UI with color-coded output
- Automatic SSH key detection and setup
- GitHub SSH connection testing
- Comprehensive error handling
- Detailed commit history with rich formatting
- Support for all standard Git workflows

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- OpenSSH (for SSH operations)

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd AI_Git

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

After installation, you can use the `gitc` command from anywhere.

## Quick Start

### 1. Generate SSH Key (First Time Setup)

```bash
# Generate a new SSH key
gitc ssh keygen --email your-email@example.com

# The public key will be displayed. Copy it and add to GitHub:
# https://github.com/settings/ssh/new

# Test your GitHub SSH connection
gitc ssh test
```

### 2. Initialize a Repository

```bash
# Create a new repository
gitc init

# Or clone an existing repository
gitc clone git@github.com:username/repo.git
```

### 3. Basic Workflow

```bash
# Check repository status
gitc status

# Add files to staging
gitc add --all

# Commit changes
gitc commit -m "Your commit message"

# Push to GitHub
gitc push -u origin main
```

## Command Reference

### SSH Management

```bash
# Generate SSH key
gitc ssh keygen --email your@email.com

# Show public SSH key
gitc ssh show

# Add SSH key to agent
gitc ssh add

# Test GitHub connection
gitc ssh test
```

### Repository Operations

```bash
# Initialize new repository
gitc init [path]

# Clone repository
gitc clone <url> [destination] [-b branch]

# Check repository status
gitc status

# Add files to staging
gitc add <files>          # Add specific files
gitc add --all            # Add all files

# Commit changes
gitc commit -m "message" [--author-name "Name"] [--author-email "email"]

# Push to remote
gitc push [--remote origin] [--branch main] [-u]

# Pull from remote
gitc pull [--remote origin] [--branch main]
```

### Branch Management

```bash
# List branches
gitc branch list           # Local branches only
gitc branch list --all     # Include remote branches

# Create new branch
gitc branch create <name> [--start-point ref]

# Switch to branch
gitc branch switch <name>  # Switch to existing branch
gitc branch switch -c <name>  # Create and switch

# Delete branch
gitc branch delete <name>  # Safe delete
gitc branch delete -f <name>  # Force delete

# Merge branch
gitc branch merge <name> [-m "message"] [--no-ff]
```

### History and Inspection

```bash
# View commit history
gitc log [-n count] [--branch name] [--author name] [--since date]

# Show differences
gitc diff                  # Unstaged changes
gitc diff --cached         # Staged changes
gitc diff <commit1> <commit2>  # Between commits
gitc diff --file <path>    # Specific file

# Show commit details
gitc show <commit-hash>
```

### Remote Management

```bash
# Add remote
gitc remote add <name> <url>

# List remotes
gitc remote list
```

## Usage Examples

### Example 1: Create and Push a New Project

```bash
# Create a new directory and initialize
mkdir my-project
cd my-project
gitc init

# Create some files
echo "# My Project" > README.md

# Add and commit
gitc add --all
gitc commit -m "Initial commit"

# Add GitHub remote and push
gitc remote add origin git@github.com:username/my-project.git
gitc push -u origin main
```

### Example 2: Working with Branches

```bash
# Create and switch to feature branch
gitc branch switch -c feature/new-feature

# Make changes and commit
gitc add --all
gitc commit -m "Add new feature"

# Push feature branch
gitc push -u origin feature/new-feature

# Switch back to main and merge
gitc branch switch main
gitc branch merge feature/new-feature

# Delete feature branch
gitc branch delete feature/new-feature
```

### Example 3: Review Project History

```bash
# View last 5 commits
gitc log -n 5

# View changes in staging
gitc diff --cached

# View changes between commits
gitc show abc123

# Check current status
gitc status
```

## Configuration

The Git client stores configuration in `~/.gitc/config.json`. You can customize:

- User name and email
- Default remote name
- Default branch name
- SSH key path
- Preferences (verbose output, colors, etc.)

Configuration is automatically created on first run.

## Project Structure

```
git_client/
├── core/
│   ├── git_operations.py    # Basic Git operations
│   ├── branch_manager.py    # Branch management
│   └── history_viewer.py    # History and diff operations
├── utils/
│   ├── ssh_manager.py       # SSH key management
│   ├── config_manager.py    # Configuration handling
│   └── logger.py            # Logging and error handling
└── cli/
    └── main.py              # CLI interface
```

## Requirements

- GitPython >= 3.1.40
- click >= 8.1.7
- paramiko >= 3.4.0
- cryptography >= 41.0.7
- rich >= 13.7.0
- colorama >= 0.4.6

## Troubleshooting

### SSH Connection Issues

If you encounter SSH connection problems:

```bash
# Verify SSH key exists
gitc ssh show

# Test GitHub connection
gitc ssh test

# Add key to SSH agent
gitc ssh add

# Check SSH agent is running
eval "$(ssh-agent -s)"
```

### Permission Denied on Push

Make sure:
1. SSH key is added to your GitHub account
2. SSH agent has your key loaded (`gitc ssh add`)
3. Using SSH URL (git@github.com:...) not HTTPS

### Command Not Found

After installation, restart your terminal or run:
```bash
source ~/.bashrc  # or ~/.zshrc
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details

## Acknowledgments

Built with:
- [GitPython](https://github.com/gitpython-developers/GitPython) - Git interface
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [Paramiko](https://www.paramiko.org/) - SSH implementation

## Author

Your Name

## Support

For issues, questions, or contributions, please visit the GitHub repository.
