from setuptools import setup, find_packages

setup(
    name="league-ranker",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'league-ranker=src.cli_wrapper:run_cli',
        ],
    },
    description="A command-line application that calculates league rankings",
    author="Ehsan Manouchehri",
    author_email="dpkhavaran@gmail.com",
    url="https://github.com/E4M9i/league-ranker",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 