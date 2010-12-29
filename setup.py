from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(name='radiopanik.nonstop.config',
      version=version,
      description=("Basic package for parsing a "
                   "configuration file used by the non-stop management "
                   "scripts at radiopanik"),
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['radiopanik', 'radiopanik.nonstop'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
