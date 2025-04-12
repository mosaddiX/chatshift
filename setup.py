from setuptools import setup

# Extract version from chatshift.py
with open("chatshift.py", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("Version:"):
            version = line.split(":")[1].strip()
            break

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chatshift",
    version=version,
    author="mosaddiX",
    author_email="mosaddix@example.com",
    description="Export Telegram chats to various text formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mosaddiX/chatshift",
    py_modules=["chatshift"],  # Single module instead of packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "telethon==1.34.0",
        "rich==13.7.0",
        "python-dotenv==1.0.1",
        "colorama==0.4.6",
        "termcolor==2.3.0",
        "pyfiglet==0.8.post1",
        "setuptools>=65.5.0",
    ],
    entry_points={
        "console_scripts": [
            "chatshift=chatshift:main",  # Point directly to the main function in chatshift.py
        ],
    },
)
