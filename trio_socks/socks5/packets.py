import construct
from enum import Enum
from trio_socks.socks5.constructs import PackEnum, IPv4Address, IPv6Address

class AuthMethod(Enum):
	no_auth = 0x0
	gssap  = 0x1
	username_password = 0x2

auth_methods = AuthMethod

ClientGreeting = construct.Struct(
	'version' / construct.Default(construct.Const(5, construct.Byte), 5),
	'auth_methods' / construct.PrefixedArray(construct.Byte, PackEnum(AuthMethod))
)

ServerChoice = construct.Struct(
	'version' / construct.Default(construct.Const(5, construct.Byte), 5),
	'auth_choice' / PackEnum(AuthMethod)
)

ClientAuthRequest = construct.Struct(
	'version' / construct.Default(construct.Byte, 1),
	'username' / construct.PascalString(construct.Byte, 'utf-8'),
	'password' / construct.PascalString(construct.Byte, 'utf-8'),
)

ServerAuthResponse = construct.Struct(
	'version' / construct.Default(construct.Byte, 1),
	'status' / construct.Flag,
)

class Socks5AddressType(Enum):
	ipv4_address = 0x01
	domain_name = 0x03
	ipv6_address = 0x06

Socks5Address = construct.Struct(
	'type' / PackEnum(Socks5AddressType),
	'address' / construct.Switch(construct.this.type, {
		Socks5AddressType.ipv4_address: IPv4Address,
		Socks5AddressType.domain_name: construct.PascalString(construct.Byte, 'utf-8'),
		Socks5AddressType.ipv6_address: IPv6Address,
	})
)

class Socks5Command(Enum):
	tcp_connect = 0x01
	tcp_bind_port = 0x02
	udp_bind_port = 0x03

ClientConnectionRequest = construct.Struct(
	'version' / construct.Default(construct.Const(5, construct.Byte), 5),
	'command' / PackEnum(Socks5Command),
	'reserved' / construct.Default(construct.Const(0, construct.Byte), 0),
	'address' / construct.Sequence(Socks5Address, construct.Short),
)

class ServerAuthStatus(Enum):
	request_granted = 0x00
	general_failure = 0x01
	connection_denied_ruleset = 0x02
	network_unreachable = 0x03
	host_unreachable = 0x04
	connection_refused = 0x05
	ttl_expired = 0x06
	protocol_error = 0x07
	address_error = 0x08

ServerConnectionResponse = construct.Struct(
	'version' / construct.Default(construct.Const(5, construct.Byte), 5),
	'status' / PackEnum(ServerAuthStatus),
	'reserved' / construct.Default(construct.Const(0, construct.Byte), 0),
	'server_bind_address' / construct.Sequence(Socks5Address, construct.Short),
)