from setuptools import setup

setup(
   name='gdrive',
   version='1.0',
   description='google colab GDrive interface',
   author='Alexey Sudachen',
   author_email='alexey.sudachen@vacasa.com',
   packages=['gdrive'],
   install_requires=['pandas', 'singleton_decorator', 'pydrive', 'oauth2client'], 
)