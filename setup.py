from setuptools import setup, find_packages

setup(
    name="boomba",
    version="0.1.0b1",
    packages=find_packages(),
    install_requires=['polars', 'pyarrow', 'SQLAlchemy'],
    entry_points={
        'console_scripts': [
            'boomba=boomba.main:main',
        ]
    },
    author="SungEun An",
    author_email="bach0918@gmail.com",
)