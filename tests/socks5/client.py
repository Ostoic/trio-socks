from trio_socks import socks5

async def run(client_stream, username=None, password=None):
	print('client start')
	stream = socks5.Socks5Stream(
		destination=('api.ipify.org', 80), proxy=('192.168.0.103', 1080),
		username=username, password=password,
		stream=client_stream
	)

	if username is not None and password is not None:
		our_choice = socks5.packets.auth_methods.username_password
	else:
		our_choice = socks5.packets.auth_methods.no_auth

	await stream._send_greeting([our_choice])
	print('client greeting sent')

	print('client waiting for response')
	data = await stream._receive_server_choice()
	auth_choice = socks5.packets.ServerChoice.parse(data).auth_choice

	print(f'client received auth choice: {auth_choice}')
	assert auth_choice == our_choice
	await stream._authenticate(auth_choice)

	print('client connection request sending')
	await stream._send_connection_request(socks5.packets.Socks5Command.tcp_connect, stream._destination)
	print('client connection request sent')

	await stream._receive_connection_response()
	assert stream._negotiated.is_set()
	await stream.aclose()