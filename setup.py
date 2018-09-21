from setuptools import setup

setup(
   name='codrv',
   version='1.1',
   description='Google Colab/Drive util functions',
   author='Alexey Sudachen',
   author_email='alexey.sudachen@vacasa.com',
   packages=['codrv'],
   install_requires=['pandas', 'singleton-decorator', 'pydrive', 'oauth2client'], 
)