import trio
from trio_socks import socks5

async def print_public_ip():
	async with socks5.make_tcp_stream(destination=('api.ipify.org', 80), proxy=('10.179.205.114', 1664)) as stream:
		await stream.send_all('GET / HTTP/1.1\r\nHost: api.ipify.org\r\n\r\n'.encode())
		text = (await stream.receive_some()).decode()
		i = text.rfind('\r\n\r\n')
		my_ip = text[i+4:]
		print(f'{my_ip=}')

trio.run(print_public_ip)