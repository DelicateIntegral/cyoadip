from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='cyoadip',
    version='0.1.0',
    description='A module to refresh urls of images linked to discord in ICC jsons',
    author='DelicateIntegral',
    author_email='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DelicateIntegral/cyoadip",
    packages=find_packages(),
    install_requires=[
        'pyyaml',
        'aiohttp',
        'Pillow'
        ],
    entry_points={
        'console_scripts': [
            'cyoadip=cyoadip.run:run_main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: AGPLv3 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
