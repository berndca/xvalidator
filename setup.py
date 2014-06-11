from distutils.core import setup

setup(
    name='xvalidator',
    version='0.1',
    packages=['xvalidator'],
    url='http://packages.python.org/xvalidator',
    license='BSD',
    author='Bernd Meyer',
    author_email='berndca@gmail.com',
    description='Validators for the creation of xml files.',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ),
    tests_require=['nose', 'six'],
)
