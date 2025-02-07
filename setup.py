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
    description='Light and Fast ETL Framework',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Baboomba/boomba',
    python_requires='>=3.12'
)