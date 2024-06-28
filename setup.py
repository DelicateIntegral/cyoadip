from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='cyoatools',
    version='0.3.0',
    description='Tools to mess with ICC jsons',
    author='DelicateIntegral',
    author_email='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DelicateIntegral/cyoadip",
    packages=find_packages(),
    install_requires=[
        'pyyaml',
        'aiohttp',
        'Pillow',
        'rich'
        ],
    entry_points={
        'console_scripts': [
            'cyoatools=cyoatools.run:run_main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: AGPLv3 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
