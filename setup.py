from setuptools import setup

setup(
	name='trio-socks',
	version='0.1.0',
	packages=['trio_socks', 'trio_socks.socks5'],
	url='https://github.com/Ostoic/trio-socks',
	license='MIT',
	author='Shaun Ostoic',
	author_email='ostoic@uwindsor.ca',
	description='trio-socks provides a HalfCloseableStream for use with the trio async library'
)