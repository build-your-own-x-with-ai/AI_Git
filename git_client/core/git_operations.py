"""
Git Operations Module
Core Git functionality for repository management
"""
import os
from pathlib import Path
from typing import List, Optional, Tuple
import git
from git import Repo, GitCommandError, InvalidGitRepositoryError


class GitOperations:
    """Handles core Git operations"""

    def __init__(self, repo_path: str = "."):
        """
        Initialize Git Operations

        Args:
            repo_path: Path to the Git repository
        """
        self.repo_path = Path(repo_path).resolve()
        self.repo: Optional[Repo] = None
        if self._is_git_repo():
            self.repo = Repo(self.repo_path)

    def _is_git_repo(self) -> bool:
        """Check if the current path is a Git repository"""
        try:
            Repo(self.repo_path)
            return True
        except InvalidGitRepositoryError:
            return False

    def init(self, bare: bool = False) -> Tuple[bool, str]:
        """
        Initialize a new Git repository

        Args:
            bare: Create a bare repository

        Returns:
            Tuple of (success, message)
        """
        try:
            if self._is_git_repo():
                return False, f"Repository already exists at {self.repo_path}"

            self.repo = Repo.init(self.repo_path, bare=bare)
            repo_type = "bare" if bare else "regular"
            return True, f"Initialized empty Git {repo_type} repository in {self.repo_path}/.git"

        except Exception as e:
            return False, f"Error initializing repository: {str(e)}"

    def clone(self, url: str, destination: Optional[str] = None, branch: Optional[str] = None) -> Tuple[bool, str]:
        """
        Clone a remote repository

        Args:
            url: Repository URL
            destination: Local destination path
            branch: Specific branch to clone

        Returns:
            Tuple of (success, message)
        """
        try:
            clone_kwargs = {}
            if branch:
                clone_kwargs['branch'] = branch

            dest_path = destination or self.repo_path
            self.repo = Repo.clone_from(url, dest_path, **clone_kwargs)
            self.repo_path = Path(dest_path).resolve()

            return True, f"Repository cloned successfully to {dest_path}"

        except GitCommandError as e:
            return False, f"Git clone error: {e.stderr}"
        except Exception as e:
            return False, f"Error cloning repository: {str(e)}"

    def add(self, files: Optional[List[str]] = None, all_files: bool = False) -> Tuple[bool, str]:
        """
        Add files to staging area

        Args:
            files: List of file paths to add
            all_files: Add all files (including untracked)

        Returns:
            Tuple of (success, message)
        """
        if not self.repo:
            return False, "Not a git repository"

        try:
            if all_files:
                self.repo.git.add(A=True)
                return True, "All files added to staging area"
            elif files:
                self.repo.index.add(files)
                return True, f"Added {len(files)} file(s) to staging area"
            else:
                return False, "No files specified. Use --all to add all files"

        except GitCommandError as e:
            return False, f"Git add error: {e.stderr}"
        except Exception as e:
            return False, f"Error adding files: {str(e)}"

    def commit(self, message: str, author_name: Optional[str] = None,
               author_email: Optional[str] = None) -> Tuple[bool, str]:
        """
        Commit staged changes

        Args:
            message: Commit message
            author_name: Author name (optional)
            author_email: Author email (optional)

        Returns:
            Tuple of (success, message)
        """
        if not self.repo:
            return False, "Not a git repository"

        try:
            # Set author if provided
            if author_name and author_email:
                author = git.Actor(author_name, author_email)
                commit = self.repo.index.commit(message, author=author)
            else:
                commit = self.repo.index.commit(message)

            return True, f"Committed: {commit.hexsha[:7]} - {message}"

        except GitCommandError as e:
            return False, f"Git commit error: {e.stderr}"
        except Exception as e:
            return False, f"Error committing: {str(e)}"

    def push(self, remote: str = "origin", branch: Optional[str] = None,
             set_upstream: bool = False) -> Tuple[bool, str]:
        """
        Push commits to remote repository

        Args:
            remote: Remote name
            branch: Branch name
            set_upstream: Set upstream tracking

        Returns:
            Tuple of (success, message)
        """
        if not self.repo:
            return False, "Not a git repository"

        try:
            if branch is None:
                branch = self.repo.active_branch.name

            push_kwargs = {}
            if set_upstream:
                push_kwargs['set_upstream'] = True

            origin = self.repo.remote(remote)
            result = origin.push(branch, **push_kwargs)

            # Check push result
            if result:
                push_info = result[0]

                # Check if push was rejected or had errors
                if push_info.flags & push_info.ERROR:
                    error_msg = push_info.summary or "Unknown error"
                    return False, f"Push failed: {error_msg}"
                elif push_info.flags & push_info.REJECTED:
                    return False, f"Push rejected (non-fast-forward). Try pulling first."
                elif push_info.flags & push_info.REMOTE_REJECTED:
                    return False, f"Push rejected by remote"
                elif push_info.flags & push_info.REMOTE_FAILURE:
                    return False, f"Remote failure during push"
                elif push_info.flags & (push_info.UP_TO_DATE | push_info.NEW_TAG |
                                       push_info.NEW_HEAD | push_info.FAST_FORWARD |
                                       push_info.FORCED_UPDATE):
                    return True, f"Successfully pushed to {remote}/{branch}"
                else:
                    return True, f"Successfully pushed to {remote}/{branch}"
            else:
                return False, "Push failed with no output"

        except GitCommandError as e:
            return False, f"Git push error: {e.stderr}"
        except Exception as e:
            return False, f"Error pushing: {str(e)}"

    def pull(self, remote: str = "origin", branch: Optional[str] = None) -> Tuple[bool, str]:
        """
        Pull changes from remote repository

        Args:
            remote: Remote name
            branch: Branch name

        Returns:
            Tuple of (success, message)
        """
        if not self.repo:
            return False, "Not a git repository"

        try:
            if branch is None:
                branch = self.repo.active_branch.name

            origin = self.repo.remote(remote)
            result = origin.pull(branch)

            if result:
                return True, f"Successfully pulled from {remote}/{branch}"
            else:
                return True, "Already up to date"

        except GitCommandError as e:
            return False, f"Git pull error: {e.stderr}"
        except Exception as e:
            return False, f"Error pulling: {str(e)}"

    def status(self) -> Tuple[bool, dict]:
        """
        Get repository status

        Returns:
            Tuple of (success, status_dict)
        """
        if not self.repo:
            return False, {"error": "Not a git repository"}

        try:
            status_dict = {
                "branch": self.repo.active_branch.name,
                "staged": [],
                "unstaged": [],
                "untracked": self.repo.untracked_files,
            }

            # Get staged files
            if self.repo.head.is_valid():
                for diff in self.repo.index.diff(self.repo.head.commit):
                    status_dict["staged"].append({
                        "path": diff.a_path,
                        "change_type": diff.change_type
                    })

            # Get unstaged files
            for diff in self.repo.index.diff(None):
                status_dict["unstaged"].append({
                    "path": diff.a_path,
                    "change_type": diff.change_type
                })

            return True, status_dict

        except Exception as e:
            return False, {"error": f"Error getting status: {str(e)}"}

    def add_remote(self, name: str, url: str) -> Tuple[bool, str]:
        """
        Add a remote repository

        Args:
            name: Remote name
            url: Remote URL

        Returns:
            Tuple of (success, message)
        """
        if not self.repo:
            return False, "Not a git repository"

        try:
            self.repo.create_remote(name, url)
            return True, f"Remote '{name}' added: {url}"

        except Exception as e:
            return False, f"Error adding remote: {str(e)}"

    def list_remotes(self) -> Tuple[bool, List[dict]]:
        """
        List all remotes

        Returns:
            Tuple of (success, list of remotes)
        """
        if not self.repo:
            return False, [{"error": "Not a git repository"}]

        try:
            remotes = []
            for remote in self.repo.remotes:
                remotes.append({
                    "name": remote.name,
                    "url": list(remote.urls)[0] if remote.urls else "No URL"
                })

            return True, remotes

        except Exception as e:
            return False, [{"error": f"Error listing remotes: {str(e)}"}]
