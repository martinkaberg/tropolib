from setuptools import setup

setup(name='tropolib',
      version='0.1',
      description='Troposphere library',
      url='http://github.com/martinkaberg/tropolib',
      author='Martin Kaberg',
      author_email='martin.kaberg@nordcloud.se',
      license='BSD',
      packages=['tropolib'],
      install_requires=[
          'troposphere',
      ],
      zip_safe=False)
