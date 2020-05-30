from trio_socks import socks5

async def run(stream, after=None):
	print('server start')
	try:
		data = await stream.receive_some()
		greeting = socks5.packets.ClientGreeting.parse(data)
		print(f'server received: {greeting}')
		print(greeting.auth_methods)

		assert (socks5.packets.auth_methods.username_password in greeting.auth_methods
		        or socks5.packets.auth_methods.no_auth in greeting.auth_methods)

		print('server asserted?')
		auth_choice = greeting.auth_methods[0]
		choice_packet = socks5.packets.ServerChoice.build({
			'auth_choice': auth_choice
		})

		print(f'server sending auth choice: {choice_packet}')
		await stream.send_all(choice_packet)

		if auth_choice == socks5.packets.auth_methods.username_password:
			data = await stream.receive_some()
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
			await stream.send_all(auth_response)

		print('server waiting')
		data = await stream.receive_some()
		connection_request = socks5.packets.ClientConnectionRequest.parse(data)

		assert connection_request.command == socks5.packets.Socks5Command.tcp_connect
		# assert connection_request.address == ({'type':socks5.packets.Socks5AddressType.domain_name,'address':'api.ipify.org'}, 80)

		connection_response = socks5.packets.ServerConnectionResponse.build({
			'status': socks5.packets.ServerAuthStatus.request_granted,
			'server_bind_address': ({'type': socks5.packets.Socks5AddressType.domain_name, 'address': 'api.ipify.org'}, 80)
		})

		await stream.send_all(connection_response)

		if after is not None:
			await after(stream)

	except Exception as e:
		print(e)
