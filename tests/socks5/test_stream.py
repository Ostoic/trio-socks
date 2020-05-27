from trio_socks import socks5
import trio

async def test_ipify():
	my_ip = None
	stream: trio.SocketStream = await trio.open_tcp_stream(host='api.ipify.org', port=80)
	async with stream:
		text = 'GET / HTTP/1.1\r\nHost: api.ipify.org\r\nConnection: keep-alive\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36\r\nAccept-Language: en-US,en;q=0.8\r\n\r\n'
		await stream.send_all(text.encode())
		data: bytes = await stream.receive_some()
		text = data.decode()
		i = text.rfind('\r\n')
		my_ip = text[i+2:]

	async with socks5.make_tcp_stream(destination=('api.ipify.org', 80), proxy=('10.179.205.114', 1664)) as stream:
		text = 'GET / HTTP/1.1\r\nHost: api.ipify.org\r\nConnection: keep-alive\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36\r\nAccept-Language: en-US,en;q=0.8\r\n\r\n'
		await stream.send_all(text.encode())
		data = await stream.receive_some()
		i = text.rfind('\r\n')
		proxy_ip = text[i+2:]

	assert proxy_ip != my_ip
