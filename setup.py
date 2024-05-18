import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

setuptools.setup(
    name="roadbook",
    version='0.1.0',
    author="D'Harréville Renaud",
    author_email=["r.dharreville@valier.ovh"],
    description="Road book automation tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
    classifiers=[],
    # tests_requires=["pytest"],
    include_package_data=True,
    entry_points={'console_scripts': ['road-book=roadbook.main:main']},
    install_requires=[req.split(" ")[0] for req in requirements if req[0] != "#"],
    extras_require={
        'dev': ['jupyter', 'pytest', "sphinx", "sphinx-rtd-theme", "wheel"],
    },
    python_requires=">=3.12"
)


