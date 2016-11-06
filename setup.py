from setuptools import setup, find_packages
 
setup(
    name = "subshell",
    version = "1.0",
    packages = find_packages(),
    install_requires=[
		'docopt==0.6.2',
		'readline==6.2.4.1',
		'requests==2.7.0',
		'tabulate==0.7.5'
    ]

    )