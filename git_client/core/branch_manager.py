"""
Branch Management Module
Handles Git branch operations
"""
from typing import List, Optional, Tuple
from git import Repo, GitCommandError, InvalidGitRepositoryError
from pathlib import Path


class BranchManager:
    """Handles Git branch operations"""

    def __init__(self, repo_path: str = "."):
        """
        Initialize Branch Manager

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

    def create_branch(self, branch_name: str, start_point: Optional[str] = None) -> Tuple[bool, str]:
        """
        Create a new branch

        Args:
            branch_name: Name of the new branch
            start_point: Starting commit/branch (default: HEAD)

        Returns:
            Tuple of (success, message)
        """
        if not self.repo:
            return False, "Not a git repository"

        try:
            if branch_name in [b.name for b in self.repo.branches]:
                return False, f"Branch '{branch_name}' already exists"

            if start_point:
                new_branch = self.repo.create_head(branch_name, start_point)
            else:
                new_branch = self.repo.create_head(branch_name)

            return True, f"Branch '{branch_name}' created"

        except GitCommandError as e:
            return False, f"Git error: {e.stderr}"
        except Exception as e:
            return False, f"Error creating branch: {str(e)}"

    def switch_branch(self, branch_name: str, create: bool = False) -> Tuple[bool, str]:
        """
        Switch to a different branch

        Args:
            branch_name: Name of the branch to switch to
            create: Create branch if it doesn't exist

        Returns:
            Tuple of (success, message)
        """
        if not self.repo:
            return False, "Not a git repository"

        try:
            # Check if branch exists
            branch_exists = branch_name in [b.name for b in self.repo.branches]

            if not branch_exists and create:
                self.repo.create_head(branch_name)
            elif not branch_exists:
                return False, f"Branch '{branch_name}' does not exist. Use --create to create it"

            # Checkout the branch
            self.repo.heads[branch_name].checkout()
            return True, f"Switched to branch '{branch_name}'"

        except GitCommandError as e:
            return False, f"Git error: {e.stderr}"
        except Exception as e:
            return False, f"Error switching branch: {str(e)}"

    def delete_branch(self, branch_name: str, force: bool = False) -> Tuple[bool, str]:
        """
        Delete a branch

        Args:
            branch_name: Name of the branch to delete
            force: Force delete even if not merged

        Returns:
            Tuple of (success, message)
        """
        if not self.repo:
            return False, "Not a git repository"

        try:
            # Check if branch exists
            if branch_name not in [b.name for b in self.repo.branches]:
                return False, f"Branch '{branch_name}' does not exist"

            # Check if trying to delete current branch
            if self.repo.active_branch.name == branch_name:
                return False, f"Cannot delete the currently active branch '{branch_name}'"

            # Delete the branch
            self.repo.delete_head(branch_name, force=force)
            return True, f"Branch '{branch_name}' deleted"

        except GitCommandError as e:
            if "not fully merged" in str(e):
                return False, f"Branch '{branch_name}' is not fully merged. Use --force to delete anyway"
            return False, f"Git error: {e.stderr}"
        except Exception as e:
            return False, f"Error deleting branch: {str(e)}"

    def list_branches(self, all_branches: bool = False) -> Tuple[bool, List[dict]]:
        """
        List all branches

        Args:
            all_branches: Include remote branches

        Returns:
            Tuple of (success, list of branches)
        """
        if not self.repo:
            return False, [{"error": "Not a git repository"}]

        try:
            branches = []
            current_branch = self.repo.active_branch.name

            # Local branches
            for branch in self.repo.branches:
                branches.append({
                    "name": branch.name,
                    "type": "local",
                    "current": branch.name == current_branch,
                    "commit": branch.commit.hexsha[:7]
                })

            # Remote branches
            if all_branches:
                for remote in self.repo.remotes:
                    for ref in remote.refs:
                        branches.append({
                            "name": ref.name,
                            "type": "remote",
                            "current": False,
                            "commit": ref.commit.hexsha[:7]
                        })

            return True, branches

        except Exception as e:
            return False, [{"error": f"Error listing branches: {str(e)}"}]

    def merge_branch(self, branch_name: str, no_ff: bool = False,
                    commit_message: Optional[str] = None) -> Tuple[bool, str]:
        """
        Merge a branch into the current branch

        Args:
            branch_name: Name of the branch to merge
            no_ff: Create a merge commit even if fast-forward is possible
            commit_message: Custom merge commit message

        Returns:
            Tuple of (success, message)
        """
        if not self.repo:
            return False, "Not a git repository"

        try:
            # Check if branch exists
            if branch_name not in [b.name for b in self.repo.branches]:
                return False, f"Branch '{branch_name}' does not exist"

            current_branch = self.repo.active_branch.name

            # Get the branch to merge
            merge_branch = self.repo.heads[branch_name]

            # Perform merge
            base = self.repo.merge_base(self.repo.head.commit, merge_branch.commit)

            if not base:
                return False, "No common ancestor found"

            # Check if already up to date
            if self.repo.head.commit == merge_branch.commit:
                return True, "Already up to date"

            # Perform the merge
            merge_msg = commit_message or f"Merge branch '{branch_name}' into {current_branch}"

            try:
                self.repo.index.merge_tree(merge_branch.commit, base=base[0])
                self.repo.index.commit(
                    merge_msg,
                    parent_commits=(self.repo.head.commit, merge_branch.commit)
                )
                return True, f"Successfully merged '{branch_name}' into '{current_branch}'"
            except GitCommandError as e:
                # Check for conflicts
                if "conflict" in str(e).lower():
                    return False, f"Merge conflict! Please resolve conflicts and commit manually"
                raise

        except GitCommandError as e:
            return False, f"Git merge error: {e.stderr}"
        except Exception as e:
            return False, f"Error merging branch: {str(e)}"

    def get_current_branch(self) -> Tuple[bool, str]:
        """
        Get the current branch name

        Returns:
            Tuple of (success, branch_name)
        """
        if not self.repo:
            return False, "Not a git repository"

        try:
            return True, self.repo.active_branch.name
        except Exception as e:
            return False, f"Error getting current branch: {str(e)}"

    def rename_branch(self, old_name: str, new_name: str) -> Tuple[bool, str]:
        """
        Rename a branch

        Args:
            old_name: Current branch name
            new_name: New branch name

        Returns:
            Tuple of (success, message)
        """
        if not self.repo:
            return False, "Not a git repository"

        try:
            if old_name not in [b.name for b in self.repo.branches]:
                return False, f"Branch '{old_name}' does not exist"

            if new_name in [b.name for b in self.repo.branches]:
                return False, f"Branch '{new_name}' already exists"

            # Rename the branch
            branch = self.repo.heads[old_name]
            branch.rename(new_name)

            return True, f"Branch '{old_name}' renamed to '{new_name}'"

        except Exception as e:
            return False, f"Error renaming branch: {str(e)}"
