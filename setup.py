import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="itunes-app-scraper-dmi",
    version="0.9.4",
    author="Digital Methods Initiative",
    author_email="stijn.peeters@uva.nl",
    description="A lightweight iTunes App Store scraper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/digitalmethodsinitiative/itunes-app-scraper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)