from setuptools import setup, find_packages
from chatshift import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chatshift",
    version=__version__,
    author="mosaddiX",
    author_email="mosaddix@example.com",
    description="Export Telegram chats to WhatsApp-like format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mosaddiX/chatshift",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "telethon>=1.34.0",
        "rich>=13.7.0",
        "python-dotenv>=1.0.1",
        "typer>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "chatshift=chatshift.cli:run",
        ],
    },
)
