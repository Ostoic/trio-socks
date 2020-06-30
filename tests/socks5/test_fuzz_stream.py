import trio

async def test_fuzz_client():
	(client_stream, server_stream) = trio.testing.memory_stream_pair()

	# with trio.move_on_after(5):
	# 	async with trio.open_nursery() as nursery:
	# 		nursery.start_soon(fuzz_client, client_stream)