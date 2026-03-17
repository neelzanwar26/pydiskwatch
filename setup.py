from setuptools import setup, find_packages

setup(
    name='pydiskwatch',
    version='1.0.0',
    description='Disk health monitor & report generator',
    author='Neel Zanwar',
    packages=find_packages(),
    install_requires=[
        'psutil>=5.9.0',
        'Jinja2>=3.0.0',
        'plyer>=2.0.0',
        'PyYAML>=6.0',
        'rich>=13.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov',
        ]
    },
    entry_points={
        'console_scripts': [
            'pydiskwatch=pydiskwatch.cli:main',
        ],
    },
)
