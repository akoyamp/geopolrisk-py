import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Geopolrisk",
    version="0.5.2",
    author="Anish Koyamparambath",
    author_email="anish.koyamparambath@u-bordeaux.fr",
    description="A geopolrisk distro",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    data_files = [("lib",["src/geopolrisk/lib/Code.xlsx","src/geopolrisk/lib/Countries.xlsx",
                          "src/geopolrisk/lib/datarecords.db","src/geopolrisk/lib/hs.json",
                          "src/geopolrisk/lib/hs_prod.json","src/geopolrisk/lib/metalsg.csv",
                          "src/geopolrisk/lib/metalslist.json","src/geopolrisk/lib/NOR.xlsx",
                          "src/geopolrisk/lib/rep.json","src/geopolrisk/lib/reporterAreas.json"]),
                          ("logs",[]),("output",[]),],
    include_package_data=True,
)