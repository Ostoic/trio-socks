# trio-socks
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)
[![PyPi Version](https://img.shields.io/pypi/v/trio-socks.svg)](https://pypi.python.org/pypi/trio-socks/)

trio-socks provides a trio.abc.HalfCloseableStream that routes its traffic through a SOCKS proxy server

# Example 
```python
import trio
from trio_socks import socks5

async def parse_public_ip(stream):
	await stream.send_all('GET / HTTP/1.1\r\nHost: api.ipify.org\r\n\r\n'.encode())
	text = (await stream.receive_some()).decode()
	i = text.rfind('\r\n\r\n')
	my_ip = text[i + 4:]
	print(f'{my_ip=}')

async def print_public_ip():
	async with socks5.Socks5Stream(destination=('api.ipify.org', 80), proxy=('10.179.205.114', 1664)) as stream:
		await parse_public_ip(stream)

	async with await trio.open_tcp_stream('api.ipify.org', 80) as stream:
		await parse_public_ip(stream)

trio.run(print_public_ip)
```
Output:
```
my_ip='132.202.81.51'
my_ip='91.143.60.163'
```