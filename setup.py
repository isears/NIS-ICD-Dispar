import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nisicd",
    version="0.0.1",
    author="Isaac Sears",
    author_email="isaac.j.sears@gmail.com",
    description="NIS ICD Disparities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/isears/nis-icd-dispar",
    project_urls={
        "Bug Tracker": "https://github.com/isears/nis-icd-dispar/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    install_requires=["dask", "pandas", "numpy"],
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
