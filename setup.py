from distutils.core import setup
setup(
  name = 'batteries',
  packages = ['batteries'],
  version = 'v0.1.1',
  license='Apache 2.0',
  description = 'Some batteries Python didn\'t come with - a pipe operator, d language style ranges, and more',
  author = 'David Briant',
  author_email = 'batteries@forwarding.cc',
  url = 'https://github.com/DangerMouseB/batteries',
  download_url = 'https://github.com/DangerMouseB/batteries/archive/v0.1.1.tar.gz',
  keywords = ['piping', 'pipeline', 'pipe', 'functional', 'ranges'],
  install_requires=['numpy'],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: Apache 2.0',   # Again, pick a license
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)