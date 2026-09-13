from setuptools import setup, find_packages

setup(
    name='scutils',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'six>=1.10.0',
        'python-dateutil>=2.5.3',
        'pytz>=2016.10',
    ],
)