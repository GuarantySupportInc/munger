from setuptools import setup, find_packages

setup(
    name="munger",
    packages=find_packages(),
    install_requires=[
        "cerberus",
        "tqdm",
        "pendulum",
    ],
)
