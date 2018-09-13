from setuptools import setup

setup(
   name='sudachen-gdrive',
   version='1.1',
   description='google colab GDrive interface',
   author='Alexey Sudachen',
   author_email='alexey.sudachen@vacasa.com',
   packages=['gdrive'],
   install_requires=['pandas', 'singleton-decorator', 'pydrive', 'oauth2client'], 
)