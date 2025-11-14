from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="git-client",
    version="0.1.0",
    author="Your Name",
    description="A simple Git client with SSH support for GitHub",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "GitPython>=3.1.40",
        "click>=8.1.7",
        "paramiko>=3.4.0",
        "cryptography>=41.0.7",
        "rich>=13.7.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "gitc=git_client.cli.main:cli",
        ],
    },
)
