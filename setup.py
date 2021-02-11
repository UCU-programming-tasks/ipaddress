import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ipaddress-dyaroshevych",
    version="0.0.1",
    author="Dmytro Yaroshevych",
    author_email="dyaroshevych@gmail.com",
    description="A Python module for getting information about IP addresses.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dyaroshevych/ipaddress",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
