from distutils.core import setup
setup(
  name = 'coppertop',
  packages = ['coppertop'],
  version = 'v0.1.2',
  license='Apache 2.0',
  description = 'Some batteries Python didn\'t come with - a pipe operator, d language style ranges, and more',
  author = 'David Briant',
  author_email = 'coppertop@forwarding.cc',
  url = 'https://github.com/DangerMouseB/coppertop',
  download_url = 'https://github.com/DangerMouseB/coppertop/archive/v0.1.2.tar.gz',
  keywords = ['piping', 'pipeline', 'pipe', 'functional', 'ranges'],
  install_requires=['numpy'],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)