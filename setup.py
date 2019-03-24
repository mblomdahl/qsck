from setuptools import setup, find_packages
from os import path


def _read_files_from_root_dir(*file_basenames: [str]) -> str:
    """Open and read *file_basenames* from project root dir."""

    return '\n'.join(
        [open(path.join(path.dirname(__file__), name), encoding='utf8').read()
         for name in file_basenames]
    )


setup(
    name='qsck',
    version='0.2',
    packages=find_packages(include=('qsck',)),
    url='https://github.com/mblomdahl/qsck',
    license='The Unlicense',
    author='Mats Blomdahl',
    author_email='mats.blomdahl@gmail.com',
    description='The shitty ".qs" file (de-)serializer',
    long_description=_read_files_from_root_dir('README.md'),
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'qs-parse = qsck.parse_cli:qs_parse',
            'qs-format = qsck.format_cli:qs_format'
        ]
    },
    setup_requires=[
        'pytest-runner'
    ],
    install_requires=[
        'Click',
        'ujson'
    ],
    tests_require=[
        'pytest'
    ],
    # https://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Quality Assurance'
    ]
)
