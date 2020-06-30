from enum import Enum
from typing import Tuple

import construct
import ipaddress

class IPAddressAdapter(construct.Adapter):
	def _decode(self, obj, context, path):
		return str(ipaddress.ip_address(obj))

	def _encode(self, obj, context, path):
		return ipaddress.ip_address(obj).packed

IPv4Address = IPAddressAdapter(construct.Bytes(4))

IPv6Address = IPAddressAdapter(construct.Bytes(16))

class ConstructEnumAdapter(construct.Enum):
	def __init__(self, enum_type, subcon, *merge, **mapping):
		super().__init__(subcon, *merge, **mapping)
		self.enum_type = enum_type

	def _decode(self, obj, context, path):
		return self.enum_type(super()._decode(obj, context, path))

	def _encode(self, obj, context, path):
		try:
			obj = obj.value
		except AttributeError:
			pass

		if type(obj) is tuple:
			obj = obj[0]

		return super()._encode(int(obj), context, path)

PackEnum = lambda enum_type, subcon=construct.Byte: ConstructEnumAdapter(enum_type=enum_type, subcon=subcon)

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

# TODO: IPv6 parsing
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