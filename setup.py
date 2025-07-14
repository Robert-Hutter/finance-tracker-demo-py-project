from setuptools import setup, find_packages

setup(
    name="finance_tracker",
    version="0.2.0",
    packages=find_packages(),
    install_requires=["pandas", "matplotlib"],
    author="Your Name",
    description="An enhanced personal finance tracker with user authentication and reporting",
    python_requires=">=3.8",
)