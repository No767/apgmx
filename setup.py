from setuptools import setup

setup(
    name="apgmx",
    author="No767",
    version="0.0.1-git",
    url="https://github.com/No767/apgmx",
    packages=["apgmx"],
    license="GPL-3.0",
    description="A database migrations tool for asyncpg",
    install_requires=["asyncpg>=0.27.0", "typer[all]>=0.9.0"],
    python_requires=">=3.8.0",
)
