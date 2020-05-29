from setuptools import setup

setup(
	name='trio-socks',
	version='0.1.0',
	packages=['trio_socks', 'trio_socks.socks5'],
	url='https://github.com/Ostoic/trio-socks',
	license='MIT',
	author='Shaun Ostoic',
	author_email='shaun.ostoic@gmail.ca',
	keywords=['socks5', 'trio-socks', 'trio'],
	download_url='https://github.com/Ostoic/trio_socks/archive/v0.1.0.tar.gz',
	description='trio-socks provides a trio.abc.HalfCloseableStream that routes its traffic through a SOCKS proxy server',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',  # Define that your audience are developers
		'License :: OSI Approved :: MIT License',  # Again, pick a license
		'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
		'Programming Language :: Python :: 3.6',
		'Topic :: Software Development :: Libraries',
		'Framework :: Trio',
		'Topic :: System :: Networking',
	],
)
