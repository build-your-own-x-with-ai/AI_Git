"""
Main CLI Application
Command-line interface for the Git client
"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from pathlib import Path
import sys
import os

from git_client.core.git_operations import GitOperations
from git_client.core.branch_manager import BranchManager
from git_client.core.history_viewer import HistoryViewer
from git_client.utils.ssh_manager import SSHKeyManager

console = Console()
error_console = Console(stderr=True)


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Simple Git Client with SSH support for GitHub"""
    pass


# SSH Management Commands
@cli.group()
def ssh():
    """SSH key management commands"""
    pass


@ssh.command()
@click.option('--email', '-e', required=True, help='Email address for the SSH key')
@click.option('--overwrite', is_flag=True, help='Overwrite existing SSH key')
def keygen(email, overwrite):
    """Generate a new SSH key pair"""
    ssh_manager = SSHKeyManager()

    success, message = ssh_manager.generate_ssh_key(email, overwrite)

    if success:
        console.print(f"[green]✓[/green] {message}")

        # Show public key
        pub_key = ssh_manager.get_public_key()
        if pub_key:
            console.print("\n[bold]Your public SSH key:[/bold]")
            console.print(Panel(pub_key, border_style="blue"))
            console.print("\n[yellow]→[/yellow] Add this key to your GitHub account:")
            console.print("  https://github.com/settings/ssh/new")
    else:
        error_console.print(f"[red]✗[/red] {message}")
        sys.exit(1)


@ssh.command()
def add():
    """Add SSH key to ssh-agent"""
    ssh_manager = SSHKeyManager()

    success, message = ssh_manager.add_key_to_ssh_agent()

    if success:
        console.print(f"[green]✓[/green] {message}")
    else:
        error_console.print(f"[red]✗[/red] {message}")
        sys.exit(1)


@ssh.command()
def test():
    """Test SSH connection to GitHub"""
    ssh_manager = SSHKeyManager()

    console.print("[yellow]Testing GitHub SSH connection...[/yellow]")
    success, message = ssh_manager.test_github_connection()

    if success:
        console.print(f"[green]✓[/green] {message}")
    else:
        error_console.print(f"[red]✗[/red] {message}")
        sys.exit(1)


@ssh.command()
def show():
    """Show public SSH key"""
    ssh_manager = SSHKeyManager()

    pub_key = ssh_manager.get_public_key()
    if pub_key:
        console.print("[bold]Your public SSH key:[/bold]")
        console.print(Panel(pub_key, border_style="blue"))
    else:
        error_console.print("[red]✗[/red] No SSH key found. Generate one with: gitc ssh keygen")
        sys.exit(1)


# Basic Git Operations
@cli.command()
@click.option('--bare', is_flag=True, help='Create a bare repository')
@click.argument('path', default='.')
def init(bare, path):
    """Initialize a new Git repository"""
    git_ops = GitOperations(path)
    success, message = git_ops.init(bare)

    if success:
        console.print(f"[green]✓[/green] {message}")
    else:
        error_console.print(f"[red]✗[/red] {message}")
        sys.exit(1)


@cli.command()
@click.argument('url')
@click.argument('destination', required=False)
@click.option('--branch', '-b', help='Clone specific branch')
def clone(url, destination, branch):
    """Clone a repository"""
    git_ops = GitOperations()

    console.print(f"[yellow]Cloning repository...[/yellow]")
    success, message = git_ops.clone(url, destination, branch)

    if success:
        console.print(f"[green]✓[/green] {message}")
    else:
        error_console.print(f"[red]✗[/red] {message}")
        sys.exit(1)


@cli.command()
@click.argument('files', nargs=-1)
@click.option('--all', '-A', 'all_files', is_flag=True, help='Add all files')
@click.option('--path', default='.', help='Repository path')
def add(files, all_files, path):
    """Add files to staging area"""
    git_ops = GitOperations(path)

    success, message = git_ops.add(list(files) if files else None, all_files)

    if success:
        console.print(f"[green]✓[/green] {message}")
    else:
        error_console.print(f"[red]✗[/red] {message}")
        sys.exit(1)


@cli.command()
@click.option('--message', '-m', required=True, help='Commit message')
@click.option('--author-name', help='Author name')
@click.option('--author-email', help='Author email')
@click.option('--path', default='.', help='Repository path')
def commit(message, author_name, author_email, path):
    """Commit staged changes"""
    git_ops = GitOperations(path)

    success, msg = git_ops.commit(message, author_name, author_email)

    if success:
        console.print(f"[green]✓[/green] {msg}")
    else:
        error_console.print(f"[red]✗[/red] {msg}")
        sys.exit(1)


@cli.command()
@click.option('--remote', default='origin', help='Remote name')
@click.option('--branch', help='Branch name')
@click.option('--set-upstream', '-u', is_flag=True, help='Set upstream tracking')
@click.option('--path', default='.', help='Repository path')
def push(remote, branch, set_upstream, path):
    """Push commits to remote"""
    git_ops = GitOperations(path)

    console.print(f"[yellow]Pushing to {remote}...[/yellow]")
    success, message = git_ops.push(remote, branch, set_upstream)

    if success:
        console.print(f"[green]✓[/green] {message}")
    else:
        error_console.print(f"[red]✗[/red] {message}")
        sys.exit(1)


@cli.command()
@click.option('--remote', default='origin', help='Remote name')
@click.option('--branch', help='Branch name')
@click.option('--path', default='.', help='Repository path')
def pull(remote, branch, path):
    """Pull changes from remote"""
    git_ops = GitOperations(path)

    console.print(f"[yellow]Pulling from {remote}...[/yellow]")
    success, message = git_ops.pull(remote, branch)

    if success:
        console.print(f"[green]✓[/green] {message}")
    else:
        error_console.print(f"[red]✗[/red] {message}")
        sys.exit(1)


@cli.command()
@click.option('--path', default='.', help='Repository path')
def status(path):
    """Show repository status"""
    git_ops = GitOperations(path)

    success, status_dict = git_ops.status()

    if not success:
        error_console.print(f"[red]✗[/red] {status_dict.get('error', 'Unknown error')}")
        sys.exit(1)

    # Display status
    console.print(f"\n[bold]On branch:[/bold] {status_dict['branch']}\n")

    if status_dict['staged']:
        console.print("[bold green]Staged files:[/bold green]")
        for item in status_dict['staged']:
            console.print(f"  [green]●[/green] {item['path']} ({item['change_type']})")
        console.print()

    if status_dict['unstaged']:
        console.print("[bold yellow]Unstaged changes:[/bold yellow]")
        for item in status_dict['unstaged']:
            console.print(f"  [yellow]●[/yellow] {item['path']} ({item['change_type']})")
        console.print()

    if status_dict['untracked']:
        console.print("[bold red]Untracked files:[/bold red]")
        for file in status_dict['untracked']:
            console.print(f"  [red]●[/red] {file}")
        console.print()

    if not (status_dict['staged'] or status_dict['unstaged'] or status_dict['untracked']):
        console.print("[green]Working tree clean[/green]")


# Branch Management Commands
@cli.group()
def branch():
    """Branch management commands"""
    pass


@branch.command('list')
@click.option('--all', '-a', 'all_branches', is_flag=True, help='Include remote branches')
@click.option('--path', default='.', help='Repository path')
def list_branches(all_branches, path):
    """List all branches"""
    branch_mgr = BranchManager(path)

    success, branches = branch_mgr.list_branches(all_branches)

    if not success:
        error_console.print(f"[red]✗[/red] {branches[0].get('error', 'Unknown error')}")
        sys.exit(1)

    # Create table
    table = Table(title="Branches")
    table.add_column("", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Commit", style="yellow")

    for br in branches:
        current = "●" if br.get('current') else " "
        table.add_row(current, br['name'], br['type'], br['commit'])

    console.print(table)


@branch.command('create')
@click.argument('name')
@click.option('--start-point', help='Starting commit/branch')
@click.option('--path', default='.', help='Repository path')
def create_branch(name, start_point, path):
    """Create a new branch"""
    branch_mgr = BranchManager(path)

    success, message = branch_mgr.create_branch(name, start_point)

    if success:
        console.print(f"[green]✓[/green] {message}")
    else:
        error_console.print(f"[red]✗[/red] {message}")
        sys.exit(1)


@branch.command('switch')
@click.argument('name')
@click.option('--create', '-c', is_flag=True, help='Create branch if it doesn\'t exist')
@click.option('--path', default='.', help='Repository path')
def switch_branch(name, create, path):
    """Switch to a branch"""
    branch_mgr = BranchManager(path)

    success, message = branch_mgr.switch_branch(name, create)

    if success:
        console.print(f"[green]✓[/green] {message}")
    else:
        error_console.print(f"[red]✗[/red] {message}")
        sys.exit(1)


@branch.command('delete')
@click.argument('name')
@click.option('--force', '-f', is_flag=True, help='Force delete')
@click.option('--path', default='.', help='Repository path')
def delete_branch(name, force, path):
    """Delete a branch"""
    branch_mgr = BranchManager(path)

    success, message = branch_mgr.delete_branch(name, force)

    if success:
        console.print(f"[green]✓[/green] {message}")
    else:
        error_console.print(f"[red]✗[/red] {message}")
        sys.exit(1)


@branch.command('merge')
@click.argument('name')
@click.option('--message', '-m', help='Merge commit message')
@click.option('--no-ff', is_flag=True, help='No fast-forward')
@click.option('--path', default='.', help='Repository path')
def merge_branch(name, message, no_ff, path):
    """Merge a branch into current branch"""
    branch_mgr = BranchManager(path)

    success, msg = branch_mgr.merge_branch(name, no_ff, message)

    if success:
        console.print(f"[green]✓[/green] {msg}")
    else:
        error_console.print(f"[red]✗[/red] {msg}")
        sys.exit(1)


# History Commands
@cli.command()
@click.option('--max-count', '-n', default=10, help='Maximum number of commits')
@click.option('--branch', help='Specific branch')
@click.option('--author', help='Filter by author')
@click.option('--since', help='Show commits since date')
@click.option('--path', default='.', help='Repository path')
def log(max_count, branch, author, since, path):
    """Show commit history"""
    history = HistoryViewer(path)

    success, commits = history.log(max_count, branch, author, since)

    if not success:
        error_console.print(f"[red]✗[/red] {commits[0].get('error', 'Unknown error')}")
        sys.exit(1)

    # Display commits
    for commit in commits:
        console.print(f"[yellow]commit {commit['full_hash']}[/yellow]")
        console.print(f"Author: {commit['author']}")
        console.print(f"Date:   {commit['date']}\n")
        console.print(f"    {commit['message']}\n")


@cli.command()
@click.argument('commit1', required=False)
@click.argument('commit2', required=False)
@click.option('--cached', is_flag=True, help='Show staged changes')
@click.option('--file', help='Specific file to diff')
@click.option('--path', default='.', help='Repository path')
def diff(commit1, commit2, cached, file, path):
    """Show differences"""
    history = HistoryViewer(path)

    success, diff_text = history.diff(commit1, commit2, cached, file)

    if not success:
        error_console.print(f"[red]✗[/red] {diff_text}")
        sys.exit(1)

    # Display diff with syntax highlighting
    syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=False)
    console.print(syntax)


@cli.command()
@click.argument('commit_hash')
@click.option('--path', default='.', help='Repository path')
def show(commit_hash, path):
    """Show commit details"""
    history = HistoryViewer(path)

    success, commit_info = history.show_commit(commit_hash)

    if not success:
        error_console.print(f"[red]✗[/red] {commit_info.get('error', 'Unknown error')}")
        sys.exit(1)

    # Display commit info
    console.print(f"\n[yellow]commit {commit_info['hash']}[/yellow]")
    console.print(f"Author: {commit_info['author']}")
    console.print(f"Date:   {commit_info['date']}\n")
    console.print(f"    {commit_info['message']}\n")

    if commit_info['files']:
        console.print("[bold]Changed files:[/bold]")
        for file in commit_info['files']:
            console.print(f"  {file['path']} (+{file['insertions']}, -{file['deletions']})")


# Remote Management
@cli.group()
def remote():
    """Remote repository management"""
    pass


@remote.command('add')
@click.argument('name')
@click.argument('url')
@click.option('--path', default='.', help='Repository path')
def add_remote(name, url, path):
    """Add a remote repository"""
    git_ops = GitOperations(path)

    success, message = git_ops.add_remote(name, url)

    if success:
        console.print(f"[green]✓[/green] {message}")
    else:
        error_console.print(f"[red]✗[/red] {message}")
        sys.exit(1)


@remote.command('list')
@click.option('--path', default='.', help='Repository path')
def list_remotes(path):
    """List all remotes"""
    git_ops = GitOperations(path)

    success, remotes = git_ops.list_remotes()

    if not success:
        error_console.print(f"[red]✗[/red] {remotes[0].get('error', 'Unknown error')}")
        sys.exit(1)

    if not remotes:
        console.print("[yellow]No remotes configured[/yellow]")
        return

    # Create table
    table = Table(title="Remotes")
    table.add_column("Name", style="cyan")
    table.add_column("URL", style="magenta")

    for r in remotes:
        table.add_row(r['name'], r['url'])

    console.print(table)


if __name__ == '__main__':
    cli()
