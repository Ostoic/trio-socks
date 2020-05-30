from setuptools import setup

def load_readme():
	with open('README.md', 'r') as f:
		return ''.join(f)

setup(
	name='trio-socks',
	version='0.1.1',
	packages=['trio_socks', 'trio_socks.socks5'],
	install_requires=['trio', 'construct', 'ipaddress'],
	url='https://github.com/Ostoic/trio-socks',
	license='MIT',
	author='Shaun Ostoic',
	author_email='shaun.ostoic@gmail.com',
	keywords=['socks5', 'trio-socks', 'trio'],
	download_url='https://github.com/Ostoic/trio-socks/archive/v0.1.1.tar.gz',
	description='trio-socks provides a trio.abc.HalfCloseableStream that routes its traffic through a SOCKS proxy server',
	long_description=load_readme(),
	long_description_content_type='text/markdown',
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
