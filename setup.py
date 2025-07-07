from setuptools import setup, find_packages

setup(
    name="geopolrisk-py",
    version="2.0",
    description="Python library for geopolitical supply risk assessment (GeoPolRisk)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Anish Koyamparambath, Thomas Schraml",
    author_email="anish.koyamparambath@u-bordeaux.fr, Thomas.Schraml@uni-bayreuth.de",
    url="https://github.com/akoyamp/geopolrisk-py",
    license="GPL-3.0-or-later",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords=["LCA", "criticality", "geopolitical", "supply-risk", "raw-materials"],
    python_requires=">=3.10",
    packages=find_packages(where="src", include=["geopolrisk*"]),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "pandas==2.2.2",
        "tqdm==4.66.4",
        "geopy==2.4.1",
        "openpyxl==3.1.2",
    ],
    project_urls={
        "Home": "https://github.com/akoyamp/geopolrisk-py",
        "Documentation": "https://github.com/akoyamp/geopolrisk-py#readme",
        "Repository": "https://github.com/akoyamp/geopolrisk-py",
    },
)
