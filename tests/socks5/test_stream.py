import trio
from trio_socks import socks5

async def test_protocol_auth():
	async def client(client_stream):
		with trio.move_on_after(5):
			print('client start')
			stream = socks5.Socks5Stream(
				destination=('api.ipify.org', 80), proxy=('192.168.0.103', 1080),
				username='user', password='pass',
				stream=client_stream
			)

			await stream._send_greeting(socks5.packets.auth_methods.username_password)
			print('client greeting sent')

			data = await stream._receive_server_choice()
			auth_choice = socks5.packets.ServerChoice.parse(data).auth_choice

			print(f'client received auth choice: {auth_choice}')
			assert auth_choice == socks5.packets.auth_methods.username_password
			await stream._authenticate(auth_choice)

			print ('client connection request sending')
			await stream._send_connection_request(socks5.packets.Socks5Command.tcp_connect)
			print('client connection request sent')

			connection_response = await stream._receive_connection_response()
			assert stream._negotiated.is_set()
			await stream.aclose()

	async def server(server_stream):
		with trio.move_on_after(5):
			print('server start')
			try:
				data = await server_stream.receive_some()
				greeting = socks5.packets.ClientGreeting.parse(data)
				print(f'server received: {greeting}')
				assert greeting.auth_methods == [socks5.packets.auth_methods.username_password]

				choice_packet = socks5.packets.ServerChoice.build({
					'auth_choice': socks5.packets.AuthMethod.username_password
				})

				print(f'server sending auth choice: {choice_packet}')
				await server_stream.send_all(choice_packet)

				data = await server_stream.receive_some()
				auth_request = socks5.packets.ClientAuthRequest.parse(data)
				print('server received auth request')
				print(f'user: {auth_request.username}')
				assert auth_request.username == 'user'
				assert auth_request.password == 'pass'

				auth_response = socks5.packets.ServerAuthResponse.build({
					'version': auth_request.version,
					'status': True
				})

				print('server sending auth response')
				await server_stream.send_all(auth_response)

				print('server waiting')
				data = await server_stream.receive_some()

				connection_request = socks5.packets.ClientConnectionRequest.parse(data)

				assert connection_request.command == socks5.packets.Socks5Command.tcp_connect
				# assert connection_request.address == ({'type':socks5.packets.Socks5AddressType.domain_name,'address':'api.ipify.org'}, 80)

				connection_response = socks5.packets.ServerConnectionResponse.build({
					'status': socks5.packets.ServerAuthStatus.request_granted,
					'server_bind_address': ({'type': socks5.packets.Socks5AddressType.domain_name, 'address':'api.ipify.org'}, 80)
				})

				await server_stream.send_all(connection_response)

			except Exception as e:
				print(e)

	(client_stream, server_stream) = trio.testing.memory_stream_pair()
	async with trio.open_nursery() as nursery:
		nursery.start_soon(server, server_stream)
		nursery.start_soon(client, client_stream)


async def test_protocol_noauth():
	async def client(client_stream):
		with trio.move_on_after(5):
			print('client start')
			stream = socks5.Socks5Stream(destination=('api.ipify.org', 80), proxy=('192.168.0.103', 1080), stream=client_stream)
			await stream._send_greeting(socks5.packets.auth_methods.no_auth)
			print('client greeting sent')

			data = await stream._receive_server_choice()
			auth_choice = socks5.packets.ServerChoice.parse(data).auth_choice

			print(f'client received auth choice: {auth_choice}')
			assert auth_choice == socks5.packets.auth_methods.no_auth
			await stream._authenticate(auth_choice)

			print ('client connection request sending')
			await stream._send_connection_request(socks5.packets.Socks5Command.tcp_connect)
			print('client connection request sent')

			connection_response = await stream._receive_connection_response()
			assert stream._negotiated.is_set()
			await stream.aclose()

	async def server(server_stream):
		with trio.move_on_after(5):
			print('server start')
			try:
				data = await server_stream.receive_some()
				greeting = socks5.packets.ClientGreeting.parse(data)
				print(f'server received: {greeting}')
				assert greeting.auth_methods == [socks5.packets.auth_methods.no_auth]

				choice_packet = socks5.packets.ServerChoice.build({
					'auth_choice': socks5.packets.AuthMethod.no_auth
				})

				print(f'server sending auth choice: {choice_packet}')
				await server_stream.send_all(choice_packet)

				print('server waiting')
				data = await server_stream.receive_some()

				connection_request = socks5.packets.ClientConnectionRequest.parse(data)

				assert connection_request.command == socks5.packets.Socks5Command.tcp_connect

				connection_response = socks5.packets.ServerConnectionResponse.build({
					'status': socks5.packets.ServerAuthStatus.request_granted,
					'server_bind_address': ({'type': socks5.packets.Socks5AddressType.domain_name, 'address':'api.ipify.org'}, 80)
				})

				await server_stream.send_all(connection_response)

			except Exception as e:
				print(e)

	(client_stream, server_stream) = trio.testing.memory_stream_pair()
	async with trio.open_nursery() as nursery:
		nursery.start_soon(server, server_stream)
		nursery.start_soon(client, client_stream)
