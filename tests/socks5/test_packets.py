from trio_socks import socks5

def test_client_greeting():
	greeting = socks5.packets.ClientGreeting.parse(b'\x05\x01\x00')
	assert greeting.version == 5
	assert greeting.auth_methods == [socks5.packets.auth_methods.no_auth]

