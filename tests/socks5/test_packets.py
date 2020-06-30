from trio_socks import socks5

def test_client_greeting():
	greeting = socks5.packets.ClientGreeting.parse(b'\x05\x01\x00')
	assert greeting.version == 5
	assert greeting.auth_methods == [socks5.packets.auth_methods.no_auth]

def test_socks5_address():
	assert socks5.stream._determine_address_type('127.0.0.1') == socks5.packets.Socks5AddressType.ipv4_address
	assert socks5.stream._determine_address_type('10.179.205.114') == socks5.packets.Socks5AddressType.ipv4_address
	assert socks5.stream._determine_address_type('api.ipify.org') == socks5.packets.Socks5AddressType.domain_name
	assert socks5.stream._determine_address_type('www.github.com') == socks5.packets.Socks5AddressType.domain_name
	assert socks5.stream._determine_address_type('fe80::a533:6f0b:b5ec:3455') == socks5.packets.Socks5AddressType.ipv6_address
