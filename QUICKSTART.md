# Quick Start Guide

This guide will help you get started with Git Client in just a few minutes.

## Installation

```bash
# Install from source
pip install -e .
```

After installation, the `gitc` command will be available.

## First Time Setup

### 1. Generate SSH Key for GitHub

```bash
# Generate a new SSH key
gitc ssh keygen --email your-email@example.com

# The command will display your public key
# Copy it and add to GitHub: https://github.com/settings/ssh/new
```

### 2. Test Your SSH Connection

```bash
# Test GitHub SSH connection
gitc ssh test

# If successful, you'll see:
# ✓ GitHub SSH connection successful
```

## Basic Workflow Example

### Create a New Repository

```bash
# Create a new project directory
mkdir my-awesome-project
cd my-awesome-project

# Initialize Git repository
gitc init

# Create some files
echo "# My Awesome Project" > README.md
echo "print('Hello, World!')" > hello.py

# Check status
gitc status
# Output shows untracked files

# Add files to staging
gitc add --all

# Commit
gitc commit -m "Initial commit"

# View history
gitc log
```

### Connect to GitHub

```bash
# Create a repository on GitHub first, then:
gitc remote add origin git@github.com:username/my-awesome-project.git

# Push your code
gitc push -u origin main
```

## Working with Branches

```bash
# Create a new feature branch
gitc branch create feature/amazing-feature

# Switch to the branch
gitc branch switch feature/amazing-feature
# Or create and switch in one command:
# gitc branch switch -c feature/amazing-feature

# Make changes, add, and commit
echo "def amazing_function():\n    pass" >> feature.py
gitc add --all
gitc commit -m "Add amazing feature"

# Push feature branch
gitc push -u origin feature/amazing-feature

# Switch back to main
gitc branch switch main

# Merge feature branch
gitc branch merge feature/amazing-feature

# Delete feature branch (optional)
gitc branch delete feature/amazing-feature
```

## Common Commands Cheat Sheet

### Repository Operations
```bash
gitc init                    # Initialize repository
gitc clone <url>             # Clone repository
gitc status                  # Check status
```

### Staging and Committing
```bash
gitc add file1.py file2.py   # Add specific files
gitc add --all               # Add all files
gitc commit -m "message"     # Commit with message
```

### Remote Operations
```bash
gitc remote add origin <url> # Add remote
gitc remote list             # List remotes
gitc push                    # Push to remote
gitc pull                    # Pull from remote
```

### Branch Management
```bash
gitc branch list             # List branches
gitc branch create <name>    # Create branch
gitc branch switch <name>    # Switch branch
gitc branch delete <name>    # Delete branch
gitc branch merge <name>     # Merge branch
```

### History and Inspection
```bash
gitc log                     # View commit history
gitc log -n 5                # Last 5 commits
gitc diff                    # View unstaged changes
gitc diff --cached           # View staged changes
gitc show <commit-hash>      # Show commit details
```

### SSH Management
```bash
gitc ssh keygen --email <email>  # Generate SSH key
gitc ssh show                    # Show public key
gitc ssh test                    # Test GitHub connection
gitc ssh add                     # Add key to agent
```

## Tips and Tricks

### 1. Viewing Beautiful Diffs
```bash
# View differences with syntax highlighting
gitc diff
```

### 2. Checking What Will Be Committed
```bash
# Always check status before committing
gitc status

# View staged changes
gitc diff --cached
```

### 3. Working with Specific Files
```bash
# Add only specific files
gitc add src/main.py src/utils.py

# View diff for specific file
gitc diff --file src/main.py
```

### 4. View Commit History
```bash
# View recent commits
gitc log -n 10

# View commits by specific author
gitc log --author "John Doe"
```

## Troubleshooting

### Issue: "Not a git repository"
**Solution**: Make sure you're in a directory that has been initialized with `gitc init` or cloned.

### Issue: SSH authentication failed
**Solutions**:
1. Make sure you've generated an SSH key: `gitc ssh keygen`
2. Add your public key to GitHub
3. Test connection: `gitc ssh test`
4. Add key to agent: `gitc ssh add`

### Issue: Command not found
**Solution**: After installation, restart your terminal or run:
```bash
source ~/.bashrc  # or ~/.zshrc
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [examples.py](examples.py) for Python library usage
- Explore all commands with `gitc --help` and `gitc <command> --help`

## Need Help?

Run any command with `--help` to see detailed options:
```bash
gitc --help
gitc branch --help
gitc ssh --help
```

Happy coding!
