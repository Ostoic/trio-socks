from setuptools import setup

setup(
	name='trio-socks',
	version='0.1.0',
	packages=['trio_socks', 'trio_socks.socks5'],
	url='https://github.com/Ostoic/trio-socks',
	license='MIT',
	author='Shaun Ostoic',
	author_email='ostoic@uwindsor.ca',
	keywords=['socks5', 'trio-socks', 'trio'],
	download_url='https://github.com/Ostoic/trio-socks/archive/v_001.tar.gz',
	description='trio-socks provides a trio.abc.HalfCloseableStream that routes its traffic through a SOCKS proxy server',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',  # Define that your audience are developers
		'Topic :: Software Development :: Build Tools',
		'License :: OSI Approved :: MIT License',  # Again, pick a license
		'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
		'Programming Language :: Python :: 3.6',
	],
)
