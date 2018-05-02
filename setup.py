from setuptools import setup, find_packages

with open('README.md') as file:
    long_description = file.read()

setup(
    name='datmo',
    version='0.0.2-dev',
    author='datmo developers',
    author_email='developer@datmo.com',
    packages=find_packages(
        exclude=["templates.*", "*.tests", "*.tests.*", "tests.*", "tests"]),
    url="https://github.com/datmo/datmo",
    license='See LICENSE.txt',
    description='Open source model tracking tool for developers',
    long_description=long_description,
    install_requires=[
        "future>=0.16.0", "enum34>=1.1.6", "glob2>=0.5", "docker>=2.2.1",
        "pyyaml>=3.12", "requests>=2.11.1", "prettytable>=0.7.2",
        "rsfile>=2.1", "humanfriendly>=3.6.1", "python-slugify>=1.2.4",
        "giturlparse.py>=0.0.5", "blitzdb>=0.2.12", "kids.cache>=0.0.7",
        "pymongo>=3.6.0", "checksumdir>=1.1.4", "semver>=2.7.8",
        "pipreqs>=0.4.9", "backports.ssl-match-hostname>=3.5.0.1"
    ],
    tests_require=["pytest==3.0.4"],
    entry_points={'console_scripts': ['datmo = datmo.cli.main:main']},
    include_package_data=True,
)
