"""
History Viewer Module
Handles Git history and diff operations
"""
from typing import List, Optional, Tuple
from datetime import datetime
from git import Repo, GitCommandError, InvalidGitRepositoryError
from pathlib import Path


class HistoryViewer:
    """Handles Git history and diff operations"""

    def __init__(self, repo_path: str = "."):
        """
        Initialize History Viewer

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

    def log(self, max_count: int = 10, branch: Optional[str] = None,
            author: Optional[str] = None, since: Optional[str] = None) -> Tuple[bool, List[dict]]:
        """
        Get commit history

        Args:
            max_count: Maximum number of commits to show
            branch: Specific branch to show history for
            author: Filter by author
            since: Show commits since date (e.g., '2 weeks ago')

        Returns:
            Tuple of (success, list of commits)
        """
        if not self.repo:
            return False, [{"error": "Not a git repository"}]

        try:
            # Build kwargs for iter_commits
            kwargs = {'max_count': max_count}

            if branch:
                kwargs['rev'] = branch
            if author:
                kwargs['author'] = author
            if since:
                kwargs['since'] = since

            commits = []
            for commit in self.repo.iter_commits(**kwargs):
                commits.append({
                    "hash": commit.hexsha[:7],
                    "full_hash": commit.hexsha,
                    "author": f"{commit.author.name} <{commit.author.email}>",
                    "date": datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M:%S'),
                    "message": commit.message.strip(),
                    "parents": [p.hexsha[:7] for p in commit.parents]
                })

            return True, commits

        except GitCommandError as e:
            return False, [{"error": f"Git log error: {e.stderr}"}]
        except Exception as e:
            return False, [{"error": f"Error getting log: {str(e)}"}]

    def diff(self, commit1: Optional[str] = None, commit2: Optional[str] = None,
             cached: bool = False, file_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Show differences between commits, commit and working tree, etc.

        Args:
            commit1: First commit (default: HEAD)
            commit2: Second commit (default: working directory)
            cached: Show staged changes
            file_path: Specific file to diff

        Returns:
            Tuple of (success, diff_text)
        """
        if not self.repo:
            return False, "Not a git repository"

        try:
            diff_text = ""

            if cached:
                # Staged changes
                if self.repo.head.is_valid():
                    diff_index = self.repo.index.diff(self.repo.head.commit)
                else:
                    diff_index = self.repo.index.diff(None)

                for diff_item in diff_index:
                    diff_text += f"\n--- a/{diff_item.a_path}\n+++ b/{diff_item.b_path}\n"
                    if diff_item.diff:
                        diff_text += diff_item.diff.decode('utf-8', errors='replace')

            elif commit1 and commit2:
                # Diff between two commits
                commit_obj1 = self.repo.commit(commit1)
                commit_obj2 = self.repo.commit(commit2)
                diff_index = commit_obj1.diff(commit_obj2)

                for diff_item in diff_index:
                    diff_text += f"\n--- a/{diff_item.a_path}\n+++ b/{diff_item.b_path}\n"
                    if diff_item.diff:
                        diff_text += diff_item.diff.decode('utf-8', errors='replace')

            elif commit1:
                # Diff between commit and working directory
                commit_obj = self.repo.commit(commit1)
                diff_index = commit_obj.diff(None)

                for diff_item in diff_index:
                    diff_text += f"\n--- a/{diff_item.a_path}\n+++ b/{diff_item.b_path}\n"
                    if diff_item.diff:
                        diff_text += diff_item.diff.decode('utf-8', errors='replace')

            else:
                # Unstaged changes (working directory vs index)
                diff_index = self.repo.index.diff(None)

                for diff_item in diff_index:
                    diff_text += f"\n--- a/{diff_item.a_path}\n+++ b/{diff_item.b_path}\n"
                    if diff_item.diff:
                        diff_text += diff_item.diff.decode('utf-8', errors='replace')

            # Filter by file path if specified
            if file_path and diff_text:
                lines = diff_text.split('\n')
                filtered_lines = []
                include = False
                for line in lines:
                    if line.startswith('---') or line.startswith('+++'):
                        include = file_path in line
                    if include:
                        filtered_lines.append(line)
                diff_text = '\n'.join(filtered_lines)

            if not diff_text:
                diff_text = "No differences found"

            return True, diff_text

        except GitCommandError as e:
            return False, f"Git diff error: {e.stderr}"
        except Exception as e:
            return False, f"Error getting diff: {str(e)}"

    def show_commit(self, commit_hash: str) -> Tuple[bool, dict]:
        """
        Show detailed information about a commit

        Args:
            commit_hash: Commit hash or reference

        Returns:
            Tuple of (success, commit_info)
        """
        if not self.repo:
            return False, {"error": "Not a git repository"}

        try:
            commit = self.repo.commit(commit_hash)

            commit_info = {
                "hash": commit.hexsha,
                "short_hash": commit.hexsha[:7],
                "author": f"{commit.author.name} <{commit.author.email}>",
                "date": datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M:%S'),
                "message": commit.message.strip(),
                "parents": [p.hexsha[:7] for p in commit.parents],
                "stats": commit.stats.total,
                "files": []
            }

            # Get changed files
            if commit.parents:
                diffs = commit.parents[0].diff(commit)
                for diff_item in diffs:
                    commit_info["files"].append({
                        "path": diff_item.b_path or diff_item.a_path,
                        "change_type": diff_item.change_type,
                        "insertions": diff_item.diff.decode('utf-8', errors='replace').count('\n+') if diff_item.diff else 0,
                        "deletions": diff_item.diff.decode('utf-8', errors='replace').count('\n-') if diff_item.diff else 0,
                    })

            return True, commit_info

        except Exception as e:
            return False, {"error": f"Error showing commit: {str(e)}"}

    def blame(self, file_path: str, line_start: Optional[int] = None,
              line_end: Optional[int] = None) -> Tuple[bool, List[dict]]:
        """
        Show what revision and author last modified each line of a file

        Args:
            file_path: Path to file
            line_start: Starting line number
            line_end: Ending line number

        Returns:
            Tuple of (success, list of blame info)
        """
        if not self.repo:
            return False, [{"error": "Not a git repository"}]

        try:
            blame_info = []
            blame_list = self.repo.blame('HEAD', file_path)

            for commit, lines in blame_list:
                for i, line in enumerate(lines, 1):
                    if line_start and i < line_start:
                        continue
                    if line_end and i > line_end:
                        break

                    blame_info.append({
                        "line_number": i,
                        "commit": commit.hexsha[:7],
                        "author": commit.author.name,
                        "date": datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d'),
                        "content": line
                    })

            return True, blame_info

        except GitCommandError as e:
            return False, [{"error": f"Git blame error: {e.stderr}"}]
        except Exception as e:
            return False, [{"error": f"Error getting blame: {str(e)}"}]

    def get_tags(self) -> Tuple[bool, List[dict]]:
        """
        List all tags

        Returns:
            Tuple of (success, list of tags)
        """
        if not self.repo:
            return False, [{"error": "Not a git repository"}]

        try:
            tags = []
            for tag in self.repo.tags:
                tags.append({
                    "name": tag.name,
                    "commit": tag.commit.hexsha[:7],
                    "message": tag.tag.message if hasattr(tag, 'tag') and tag.tag else ""
                })

            return True, tags

        except Exception as e:
            return False, [{"error": f"Error getting tags: {str(e)}"}]

    def create_tag(self, tag_name: str, message: Optional[str] = None,
                   commit: Optional[str] = None) -> Tuple[bool, str]:
        """
        Create a new tag

        Args:
            tag_name: Name of the tag
            message: Tag message (creates annotated tag)
            commit: Commit to tag (default: HEAD)

        Returns:
            Tuple of (success, message)
        """
        if not self.repo:
            return False, "Not a git repository"

        try:
            if commit:
                commit_obj = self.repo.commit(commit)
            else:
                commit_obj = self.repo.head.commit

            if message:
                # Annotated tag
                self.repo.create_tag(tag_name, ref=commit_obj, message=message)
            else:
                # Lightweight tag
                self.repo.create_tag(tag_name, ref=commit_obj)

            return True, f"Tag '{tag_name}' created"

        except Exception as e:
            return False, f"Error creating tag: {str(e)}"
