"""Git Client - A simple Git client with SSH support for GitHub"""

__version__ = '0.1.0'
__author__ = 'Your Name'

from git_client.core.git_operations import GitOperations
from git_client.core.branch_manager import BranchManager
from git_client.core.history_viewer import HistoryViewer
from git_client.utils.ssh_manager import SSHKeyManager
from git_client.utils.config_manager import ConfigManager
from git_client.utils.logger import Logger

__all__ = [
    'GitOperations',
    'BranchManager',
    'HistoryViewer',
    'SSHKeyManager',
    'ConfigManager',
    'Logger',
]
