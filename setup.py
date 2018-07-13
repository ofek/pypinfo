from setuptools import find_packages, setup

with open('pypinfo/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('= ')[1].strip("'")
            break

setup(
    name='pypinfo',
    version=version,
    description='View PyPI download statistics with ease.',
    long_description=open('README.rst', 'r').read(),
    author='Ofek Lev',
    author_email='ofekmeister@gmail.com',
    maintainer='Ofek Lev',
    maintainer_email='ofekmeister@gmail.com',
    url='https://github.com/ofek/pypinfo',
    download_url='https://github.com/ofek/pypinfo',
    license='MIT',
    keywords=('pypi', 'downloads', 'stats', 'bigquery'),
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ),
    python_requires='>=3.5',
    install_requires=('appdirs', 'binary', 'click', 'google-cloud-bigquery>=0.29.0', 'tinydb', 'tinyrecord'),
    tests_require=['pytest'],
    packages=find_packages(),
    entry_points={'console_scripts': ('pypinfo = pypinfo.cli:pypinfo',)},
)
