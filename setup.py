from setuptools import setup, find_packages

setup(
    name="borrowed_book_system",
    version="0.1.0",
    packages=find_packages(exclude=[".venv", "tests*"]),
    install_requires=[],
    description="FastAPI service for managing borrowed books",
    author="AI",
) 
