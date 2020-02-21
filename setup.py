from distutils.core import setup
setup(
  name = 'coppertop',
  packages = [
    'coppertop',
    'coppertop._std',
    'coppertop.examples',
    'coppertop.examples.tests',
    'coppertop.tests',
  ],
  version = 'v0.1.5',
  license='Apache 2.0',
  description = 'Some batteries Python didn\'t come with - a pipe operator, d language style ranges, and more',
  author = 'DangerMouseB',
  author_email = 'coppertop@forwarding.cc',
  url = 'https://github.com/DangerMouseB/coppertop',
  download_url = 'https://github.com/DangerMouseB/coppertop/archive/v0.1.5.tar.gz',
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