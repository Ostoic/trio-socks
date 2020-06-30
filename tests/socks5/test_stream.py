from uuid import uuid4

import trio
import tests
from trio_socks import socks5

async def test_protocol_auth():
	(client_stream, server_stream) = trio.testing.memory_stream_pair()
	with trio.move_on_after(1) as scope:
		cancel_scope = scope
		async with trio.open_nursery() as nursery:
			nursery.start_soon(tests.socks5.server.run, server_stream)
			nursery.start_soon(tests.socks5.client.run, client_stream, 'user', 'pass')

	assert not cancel_scope.cancel_called

async def test_protocol_noauth():
	(client_stream, server_stream) = trio.testing.memory_stream_pair()
	with trio.move_on_after(1) as scope:
		cancel_scope = scope
		async with trio.open_nursery() as nursery:
			nursery.start_soon(tests.socks5.server.run, server_stream)
			nursery.start_soon(tests.socks5.client.run, client_stream, 'user', 'pass')

	assert not cancel_scope.cancel_called

async def test_interface():
	key = str(uuid4())
	async def server_receive_once(stream):
		data = await stream.receive_some()
		print(f'server received: {data}')
		assert data.decode() == key

	async def test(mem_stream):
		async with socks5.Socks5Stream(destination=('dst', 56), proxy=('proxy', 1080), stream=mem_stream) as stream:
			socks_stream = stream
			assert not stream._negotiated.is_set()
			await stream.send_all(key.encode())
			assert stream._negotiated.is_set()

		assert socks_stream._stream is None
		assert not socks_stream._negotiated.is_set()

	(client_stream, server_stream) = trio.testing.memory_stream_pair()
	with trio.move_on_after(1) as scope:
		cancel_scope = scope
		async with trio.open_nursery() as nursery:
			nursery.start_soon(lambda : tests.socks5.server.run(server_stream, after=server_receive_once))
			nursery.start_soon(test, client_stream)

	assert not cancel_scope.cancel_called