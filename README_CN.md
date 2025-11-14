# Git Client - 支持 SSH 的简易 Git 客户端

[English](README.md) | 简体中文

一个功能完整、用户友好的 Git 客户端，使用 Python 构建，提供完整的 SSH 支持用于 GitHub。适合学习 Git 内部原理或作为标准 Git CLI 的轻量级替代品。

## 功能特性

### 核心功能
- **基础 Git 操作**：init、clone、add、commit、push、pull
- **分支管理**：创建、切换、删除、合并分支
- **历史查看**：log、diff、status、show commits
- **远程管理**：添加和列出远程仓库
- **SSH 密钥管理**：生成、管理和测试 SSH 密钥
- **配置管理**：持久化用户设置

### 特色亮点
- 美观的终端 UI，带彩色输出
- 自动 SSH 密钥检测和设置
- GitHub SSH 连接测试
- 全面的错误处理
- Rich 格式化的详细提交历史
- 支持所有标准 Git 工作流

## 安装

### 前置要求
- Python 3.8 或更高版本
- pip（Python 包管理器）
- OpenSSH（用于 SSH 操作）

### 从源码安装

```bash
# 克隆仓库
git clone git@github.com:build-your-own-x-with-ai/AI_Git.git
cd AI_Git

# 安装依赖
pip install -r requirements.txt

# 安装包
pip install -e .
```

安装后，您可以在任何地方使用 `gitc` 命令。

## 快速开始

### 1. 生成 SSH 密钥（首次设置）

```bash
# 生成新的 SSH 密钥
gitc ssh keygen --email your-email@example.com

# 公钥将被显示，复制并添加到 GitHub：
# https://github.com/settings/ssh/new

# 测试 GitHub SSH 连接
gitc ssh test
```

### 2. 初始化仓库

```bash
# 创建新仓库
gitc init

# 或克隆现有仓库
gitc clone git@github.com:username/repo.git
```

### 3. 基础工作流

```bash
# 查看仓库状态
gitc status

# 添加文件到暂存区
gitc add --all

# 提交更改
gitc commit -m "Your commit message"

# 推送到 GitHub
gitc push -u origin main
```

## 命令参考

### SSH 管理

```bash
# 生成 SSH 密钥
gitc ssh keygen --email your@email.com

# 显示公钥
gitc ssh show

# 添加 SSH 密钥到 agent
gitc ssh add

# 测试 GitHub 连接
gitc ssh test
```

### 仓库操作

```bash
# 初始化新仓库
gitc init [path]

# 克隆仓库
gitc clone <url> [destination] [-b branch]

# 查看仓库状态
gitc status

# 添加文件到暂存区
gitc add <files>          # 添加特定文件
gitc add --all            # 添加所有文件

# 提交更改
gitc commit -m "message" [--author-name "Name"] [--author-email "email"]

# 推送到远程
gitc push [--remote origin] [--branch main] [-u]

# 从远程拉取
gitc pull [--remote origin] [--branch main]
```

### 分支管理

```bash
# 列出分支
gitc branch list           # 仅本地分支
gitc branch list --all     # 包括远程分支

# 创建新分支
gitc branch create <name> [--start-point ref]

# 切换分支
gitc branch switch <name>        # 切换到现有分支
gitc branch switch -c <name>     # 创建并切换

# 删除分支
gitc branch delete <name>        # 安全删除
gitc branch delete -f <name>     # 强制删除

# 合并分支
gitc branch merge <name> [-m "message"] [--no-ff]
```

### 历史和检查

```bash
# 查看提交历史
gitc log [-n count] [--branch name] [--author name] [--since date]

# 显示差异
gitc diff                  # 未暂存的更改
gitc diff --cached         # 已暂存的更改
gitc diff <commit1> <commit2>  # 两次提交之间
gitc diff --file <path>    # 特定文件

# 显示提交详情
gitc show <commit-hash>
```

### 远程管理

```bash
# 添加远程
gitc remote add <name> <url>

# 列出远程
gitc remote list
```

## 实现原理

### 架构设计

Git Client 采用模块化的分层架构，将功能明确分离到不同的层次：

```
┌─────────────────────────────────────────┐
│           CLI Layer (cli/)              │
│   命令行界面、参数解析、输出格式化         │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Core Layer (core/)              │
│   Git 操作、分支管理、历史查看            │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Utils Layer (utils/)             │
│   SSH 管理、配置、日志、错误处理           │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      External Libraries                 │
│   GitPython、Paramiko、Cryptography     │
└─────────────────────────────────────────┘
```

### 核心模块详解

#### 1. Git 操作模块 (git_operations.py)

**设计思路**：
- 封装 GitPython 库，提供统一的接口
- 所有方法返回 `Tuple[bool, str/dict]` 格式，便于错误处理
- 自动检测 Git 仓库，提供友好的错误提示

**核心实现**：

```python
class GitOperations:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.repo: Optional[Repo] = None
        if self._is_git_repo():
            self.repo = Repo(self.repo_path)
```

**关键技术点**：

1. **仓库检测**：使用 `InvalidGitRepositoryError` 异常判断
2. **状态管理**：通过 `repo.index.diff()` 获取暂存和未暂存的更改
3. **推送检测**：检查 `PushInfo` 标志位（ERROR、REJECTED、REMOTE_FAILURE 等）

```python
def push(self, remote: str = "origin", branch: Optional[str] = None,
         set_upstream: bool = False) -> Tuple[bool, str]:
    # 检查推送结果的各种状态标志
    if push_info.flags & push_info.ERROR:
        return False, f"Push failed: {error_msg}"
    elif push_info.flags & push_info.REJECTED:
        return False, f"Push rejected (non-fast-forward)"
    # ... 更多状态检查
```

#### 2. 分支管理模块 (branch_manager.py)

**设计思路**：
- 独立的分支操作类，职责单一
- 支持本地和远程分支的统一管理
- 安全的分支删除（检查是否已合并）

**核心实现**：

```python
def switch_branch(self, branch_name: str, create: bool = False):
    # 检查分支是否存在
    branch_exists = branch_name in [b.name for b in self.repo.branches]

    if not branch_exists and create:
        self.repo.create_head(branch_name)

    # 切换分支
    self.repo.heads[branch_name].checkout()
```

**关键技术点**：

1. **分支列表**：遍历 `repo.branches` 和 `repo.remotes[].refs`
2. **合并操作**：使用 `merge_base()` 查找共同祖先，`merge_tree()` 执行合并
3. **冲突检测**：捕获 GitCommandError，检查是否包含 "conflict"

#### 3. 历史查看模块 (history_viewer.py)

**设计思路**：
- 提供丰富的历史查询功能
- 支持过滤（作者、时间、分支）
- 格式化输出，便于阅读

**核心实现**：

```python
def log(self, max_count: int = 10, branch: Optional[str] = None,
        author: Optional[str] = None, since: Optional[str] = None):
    kwargs = {'max_count': max_count}
    if author:
        kwargs['author'] = author

    commits = []
    for commit in self.repo.iter_commits(**kwargs):
        commits.append({
            "hash": commit.hexsha[:7],
            "author": f"{commit.author.name}",
            "date": datetime.fromtimestamp(commit.committed_date),
            "message": commit.message.strip()
        })
```

**关键技术点**：

1. **差异计算**：使用 `diff()` 方法比较提交、暂存区、工作目录
2. **语法高亮**：集成 Rich 的 Syntax 类显示彩色 diff
3. **Blame 功能**：使用 `repo.blame()` 追踪每行代码的修改者

#### 4. SSH 密钥管理模块 (ssh_manager.py)

**设计思路**：
- 完整的 SSH 密钥生命周期管理
- 使用 cryptography 库生成高强度密钥
- 自动配置 SSH 环境

**核心实现**：

```python
def generate_ssh_key(self, email: str, overwrite: bool = False):
    # 生成 4096 位 RSA 密钥
    key = rsa.generate_private_key(
        backend=default_backend(),
        public_exponent=65537,
        key_size=4096
    )

    # 保存私钥（PEM 格式）
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    )

    # 设置正确的权限
    os.chmod(self.private_key_path, 0o600)
```

**关键技术点**：

1. **密钥格式**：
   - 私钥：OpenSSH PEM 格式，无加密
   - 公钥：OpenSSH 格式，附带邮箱标识

2. **权限设置**：
   - 私钥：0o600（仅所有者可读写）
   - 公钥：0o644（所有者可读写，其他人可读）
   - SSH 目录：0o700（仅所有者访问）

3. **连接测试**：
   ```python
   def test_github_connection(self):
       result = subprocess.run(
           ["ssh", "-T", "git@github.com",
            "-o", "StrictHostKeyChecking=no"],
           capture_output=True, text=True, timeout=10
       )
       # GitHub 认证成功返回 exit code 1
       if "successfully authenticated" in output.lower():
           return True, "Connection successful"
   ```

4. **SSH Config 配置**：
   ```
   Host github.com
       HostName github.com
       User git
       IdentityFile ~/.ssh/id_rsa
       IdentitiesOnly yes
   ```

#### 5. CLI 界面模块 (main.py)

**设计思路**：
- 使用 Click 框架构建命令行界面
- 使用 Rich 库美化输出
- 分离正常输出和错误输出

**核心实现**：

```python
# 创建两个控制台实例
console = Console()              # 标准输出
error_console = Console(stderr=True)  # 错误输出

@cli.command()
@click.option('--message', '-m', required=True)
def commit(message, author_name, author_email, path):
    git_ops = GitOperations(path)
    success, msg = git_ops.commit(message, author_name, author_email)

    if success:
        console.print(f"[green]✓[/green] {msg}")
    else:
        error_console.print(f"[red]✗[/red] {msg}")
        sys.exit(1)
```

**关键技术点**：

1. **命令组织**：使用 Click 的 `@group` 装饰器组织子命令
   ```python
   @cli.group()
   def branch():
       """Branch management commands"""
       pass

   @branch.command('list')
   def list_branches():
       # 实现
   ```

2. **表格输出**：使用 Rich 的 Table 类
   ```python
   table = Table(title="Branches")
   table.add_column("Name", style="magenta")
   table.add_column("Commit", style="yellow")

   for br in branches:
       table.add_row(br['name'], br['commit'])

   console.print(table)
   ```

3. **语法高亮**：使用 Rich 的 Syntax 类
   ```python
   syntax = Syntax(diff_text, "diff",
                   theme="monokai",
                   line_numbers=False)
   console.print(syntax)
   ```

#### 6. 配置管理模块 (config_manager.py)

**设计思路**：
- JSON 格式存储配置
- 支持点号分隔的键名（如 `user.name`）
- 提供配置验证功能

**核心实现**：

```python
class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".gitc"
        self.config_file = self.config_dir / "config.json"
        self.config = self._load_config()

    def set(self, key: str, value: Any):
        keys = key.split('.')
        config = self.config

        # 导航到目标键的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # 设置值
        config[keys[-1]] = value
        return self.save_config()
```

**配置结构**：

```json
{
  "user": {
    "name": "Your Name",
    "email": "your@email.com"
  },
  "ssh": {
    "key_path": "/Users/xxx/.ssh/id_rsa"
  },
  "defaults": {
    "remote": "origin",
    "branch": "main"
  },
  "preferences": {
    "auto_add_ssh_key": true,
    "verbose": false,
    "color": true
  }
}
```

### 技术实现细节

#### 错误处理策略

**三层错误处理机制**：

1. **异常捕获**：
   ```python
   try:
       # Git 操作
   except GitCommandError as e:
       return False, f"Git error: {e.stderr}"
   except Exception as e:
       return False, f"Error: {str(e)}"
   ```

2. **返回值检查**：
   ```python
   success, message = git_ops.commit(msg)
   if not success:
       error_console.print(f"[red]✗[/red] {message}")
       sys.exit(1)
   ```

3. **用户友好提示**：
   - 提供具体的错误原因
   - 建议可能的解决方案
   - 错误输出到 stderr，便于脚本处理

#### 推送状态检测

**PushInfo 标志位系统**：

GitPython 返回的 PushInfo 对象包含多个标志位，需要正确检测：

```python
# 错误标志（优先级最高）
ERROR           = 1 << 0   # 推送错误
REJECTED        = 1 << 1   # 被拒绝（非快进）
REMOTE_REJECTED = 1 << 2   # 远程拒绝
REMOTE_FAILURE  = 1 << 3   # 远程失败

# 成功标志
UP_TO_DATE      = 1 << 4   # 已是最新
NEW_TAG         = 1 << 5   # 新标签
NEW_HEAD        = 1 << 6   # 新分支
FAST_FORWARD    = 1 << 7   # 快进合并
FORCED_UPDATE   = 1 << 8   # 强制更新
```

**检测顺序**：
1. 先检查错误标志
2. 再检查成功标志
3. 提取具体的错误信息

#### SSH 密钥生成算法

**RSA 密钥参数选择**：

```python
# 参数说明
public_exponent=65537  # 标准的公钥指数（F4）
key_size=4096         # 密钥长度（4096 位更安全）
```

**为什么选择这些参数**：

1. **公钥指数 65537**：
   - 是一个质数（第 4 个费马数）
   - 二进制表示简单：10000000000000001
   - 加密运算快速
   - 是 RSA 标准推荐值

2. **密钥长度 4096**：
   - GitHub 推荐最小 2048 位
   - 4096 位提供更高安全性
   - 适合长期使用
   - 性能开销可接受

#### 并发和性能优化

**优化策略**：

1. **懒加载**：
   ```python
   def __init__(self, repo_path: str = "."):
       self.repo: Optional[Repo] = None
       if self._is_git_repo():
           self.repo = Repo(self.repo_path)  # 仅在需要时加载
   ```

2. **缓存配置**：
   ```python
   class ConfigManager:
       def __init__(self):
           self.config = self._load_config()  # 加载一次，重复使用
   ```

3. **批量操作**：
   ```python
   def add(self, files: List[str], all_files: bool = False):
       if all_files:
           self.repo.git.add(A=True)  # 一次性添加所有文件
       else:
           self.repo.index.add(files)  # 批量添加指定文件
   ```

### 关键技术挑战及解决方案

#### 挑战 1：Rich Console 的 stderr 输出

**问题**：Rich 的 `Console.print()` 不支持 `err=True` 参数

**解决方案**：
```python
console = Console()                    # 正常输出
error_console = Console(stderr=True)   # 错误输出

# 使用不同的控制台
console.print("[green]Success")
error_console.print("[red]Error")
```

#### 挑战 2：路径管理

**问题**：开发模式和安装模式的导入路径不一致

**解决方案**：
- 移除 `sys.path.insert()`
- 使用标准的包导入：`from git_client.core import GitOperations`
- 通过 `setup.py` 正确安装包

#### 挑战 3：推送失败检测

**问题**：GitPython 即使推送失败也返回结果对象

**解决方案**：
```python
result = origin.push(branch)
push_info = result[0]

# 检查所有可能的错误标志
if push_info.flags & (push_info.ERROR |
                      push_info.REJECTED |
                      push_info.REMOTE_REJECTED |
                      push_info.REMOTE_FAILURE):
    return False, "Push failed"
```

#### 挑战 4：SSH 密钥权限

**问题**：不正确的文件权限导致 SSH 拒绝使用密钥

**解决方案**：
```python
# SSH 要求严格的权限设置
os.chmod(private_key_path, 0o600)  # 私钥：仅所有者读写
os.chmod(public_key_path, 0o644)   # 公钥：所有者读写，其他人只读
os.chmod(ssh_dir, 0o700)           # SSH 目录：仅所有者访问
```

### 测试策略

虽然当前版本主要进行了手动测试，但设计时已考虑可测试性：

**单元测试设计**：
```python
def test_init_repository():
    git_ops = GitOperations("/tmp/test_repo")
    success, message = git_ops.init()
    assert success == True
    assert "Initialized" in message

def test_commit_without_changes():
    git_ops = GitOperations("/tmp/test_repo")
    success, message = git_ops.commit("test")
    assert success == False
    assert "nothing to commit" in message.lower()
```

**集成测试设计**：
```python
def test_complete_workflow():
    # 初始化 -> 添加 -> 提交 -> 推送
    git_ops = GitOperations("/tmp/test_repo")
    git_ops.init()
    git_ops.add(all_files=True)
    git_ops.commit("Initial commit")
    success, _ = git_ops.push()
    assert success == True
```

### 扩展性设计

**插件系统（未来）**：
```python
# 可通过继承扩展功能
class CustomGitOps(GitOperations):
    def custom_operation(self):
        # 自定义操作
        pass

# 或通过装饰器添加功能
@git_operation
def my_custom_command(repo):
    # 自定义命令
    pass
```

**钩子系统（未来）**：
```python
class GitHooks:
    def pre_commit(self):
        # 提交前检查
        pass

    def post_commit(self):
        # 提交后操作
        pass
```

## 项目统计

- **代码行数**：~1,857 行 Python
- **模块数量**：7 个核心模块
- **CLI 命令**：20+ 个命令
- **文档文件**：5 份完整指南

## 依赖库

### 核心依赖

- **GitPython** (3.1.40+)：Git 操作的 Python 接口
  - 提供完整的 Git 功能封装
  - 支持所有标准 Git 命令

- **Click** (8.1.7+)：命令行界面框架
  - 简洁的装饰器语法
  - 自动生成帮助文档
  - 类型验证和转换

- **Rich** (13.7.0+)：终端美化输出
  - 彩色输出
  - 表格和面板
  - 语法高亮
  - 进度条

- **Paramiko** (3.4.0+)：SSH 协议实现
  - SSH 连接管理
  - 密钥认证

- **Cryptography** (41.0.7+)：加密和密钥生成
  - RSA 密钥生成
  - 各种加密算法
  - X.509 证书支持

- **Colorama** (0.4.6+)：跨平台彩色输出
  - Windows 控制台颜色支持
  - ANSI 转义序列处理

## 使用示例

### 示例 1：创建并推送新项目

```bash
# 创建新目录并初始化
mkdir my-project
cd my-project
gitc init

# 创建文件
echo "# My Project" > README.md

# 添加并提交
gitc add --all
gitc commit -m "Initial commit"

# 添加 GitHub 远程并推送
gitc remote add origin git@github.com:username/my-project.git
gitc push -u origin main
```

### 示例 2：使用分支

```bash
# 创建并切换到特性分支
gitc branch switch -c feature/amazing-feature

# 进行更改并提交
gitc add --all
gitc commit -m "Add amazing feature"

# 推送特性分支
gitc push -u origin feature/amazing-feature

# 切换回 main 并合并
gitc branch switch main
gitc branch merge feature/amazing-feature

# 删除特性分支
gitc branch delete feature/amazing-feature
```

### 示例 3：查看项目历史

```bash
# 查看最近 5 次提交
gitc log -n 5

# 查看暂存区的更改
gitc diff --cached

# 查看两次提交之间的差异
gitc show abc123

# 检查当前状态
gitc status
```

## 故障排除

### SSH 连接问题

如果遇到 SSH 连接问题：

```bash
# 验证 SSH 密钥存在
gitc ssh show

# 测试 GitHub 连接
gitc ssh test

# 添加密钥到 SSH agent
gitc ssh add

# 检查 SSH agent 是否运行
eval "$(ssh-agent -s)"
```

### 推送被拒绝

确保：
1. SSH 密钥已添加到 GitHub 账户
2. SSH agent 已加载您的密钥（`gitc ssh add`）
3. 使用 SSH URL（git@github.com:...）而非 HTTPS

### 命令未找到

安装后，重启终端或运行：
```bash
source ~/.bashrc  # 或 ~/.zshrc
```

## 性能特点

- 快速初始化
- 高效的文件操作
- 相比标准 Git 开销最小
- 小内存占用
- 快速命令执行

## 兼容性

- **操作系统**：macOS、Linux、Windows
- **Python 版本**：3.8、3.9、3.10、3.11、3.12、3.13
- **Git 平台**：GitHub、GitLab、Bitbucket（通过 SSH）

## 贡献

欢迎贡献！请随时提交问题或拉取请求。

详细信息请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 鸣谢

构建使用：
- [GitPython](https://github.com/gitpython-developers/GitPython) - Git 接口
- [Click](https://click.palletsprojects.com/) - CLI 框架
- [Rich](https://github.com/Textualize/rich) - 终端美化
- [Paramiko](https://www.paramiko.org/) - SSH 实现

## 支持

如有问题、疑问或贡献，请访问 GitHub 仓库。

**仓库地址**：https://github.com/build-your-own-x-with-ai/AI_Git

## 相关文档

- [English Documentation](README.md) - 英文文档
- [Quick Start Guide](QUICKSTART.md) - 快速入门指南
- [Contributing Guide](CONTRIBUTING.md) - 贡献指南
- [Changelog](CHANGELOG.md) - 版本历史
- [Deployment Guide](DEPLOYMENT.md) - 部署说明
