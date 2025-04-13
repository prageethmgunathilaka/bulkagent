from setuptools import setup, find_packages

setup(
    name="agent-system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here, for example:
        # "flask",
        # "requests",
    ],
    python_requires=">=3.6",
    author="Your Name",
    author_email="your.email@example.com",
    description="An agent management system",
    keywords="agent, ai, management",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
