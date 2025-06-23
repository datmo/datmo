import os, sys
from setuptools import setup, find_packages

project_root = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(project_root, 'README.md')) as file:
    long_description = file.read()

with open(os.path.join(project_root, 'datmo', 'VERSION')) as file:
    __version__ = file.read()

# Modern Python 3.7+ dependencies
prerequisites = [
    "future>=0.18.0", 
    "glob2>=0.7", 
    "docker>=6.0.0",
    "pyyaml>=6.0", 
    "pytz>=2022.1", 
    "tzlocal>=4.0", 
    "rsfile>=2.1",
    "humanfriendly>=10.0", 
    "python-slugify>=6.0.0",
    "giturlparse.py>=0.0.5", 
    "blitzdb>=0.4.0", 
    "kids.cache>=0.0.7",
    "pymongo>=4.0.0", 
    "checksumdir>=1.2.0", 
    "semver>=2.13.0",
    "timeout-decorator>=0.5.0",
    "cerberus>=1.3.0", 
    "pathspec>=0.9.0", 
    "psutil>=5.8.0",
    "flask>=2.0.0", 
    "jinja2>=3.0.0", 
    "markupsafe>=2.0.0",
    "werkzeug>=2.0.0", 
    "beautifulsoup4>=4.10.0", 
    "gunicorn>=20.0.0",
    "itsdangerous>=2.0.0", 
    "six>=1.16.0", 
    "urllib3>=1.26.0,<2.0.0",
    "chardet>=4.0.0", 
    "prettytable>=3.0.0",
    "requests>=2.28.0", 
    "plotly>=5.0.0",
    "jsonschema>=4.0.0", 
    "celery>=5.2.0", 
    "numpy>=1.21.0"
]

setup(
    name='datmo',
    version=__version__,
    author='datmo developers',
    author_email='developer@datmo.com',
    packages=find_packages(
        exclude=["templates.*", "*.tests", "*.tests.*", "tests.*", "tests"]),
    url="https://github.com/datmo/datmo",
    license='See LICENSE.txt',
    description='Open source model tracking tool for developers',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=prerequisites,
    tests_require=["pytest>=7.0.0"],
    python_requires='>=3.7',
    entry_points={'console_scripts': ['datmo = datmo.cli.main:main']},
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
