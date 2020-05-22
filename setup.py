from setuptools import setup

# read the contents of README.md file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'coppertop',
  packages = [
    'coppertop',
    'coppertop._std',
    'coppertop.examples',
    'coppertop.examples.tests',
    'coppertop.tests',
    'coppertop.time',
    'coppertop.time.tests',
  ],
  python_requires='>=3.6',
  version = 'v0.1.10',
  license='Apache 2.0',
  description = 'Some batteries Python didn\'t come with - a pipe operator, d language style ranges, and more',
  long_description_content_type='text/markdown',
  long_description=long_description,
  author = 'DangerMouseB',
  author_email = 'dangermouseb@forwarding.cc',
  url = 'https://github.com/DangerMouseB/coppertop',
  download_url = 'https://github.com/DangerMouseB/coppertop/archive/v0.1.7.tar.gz',
  keywords = ['piping', 'pipeline', 'pipe', 'functional', 'ranges'],
  install_requires=[],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Science/Research',
    'Topic :: Utilities',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)