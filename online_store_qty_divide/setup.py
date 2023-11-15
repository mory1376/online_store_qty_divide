from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in online_store_qty_divide/__init__.py
from online_store_qty_divide import __version__ as version

setup(
	name="online_store_qty_divide",
	version=version,
	description="store",
	author="mohebi",
	author_email="mohebi@duck.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
