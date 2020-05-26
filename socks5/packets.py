from construct import Enum, Struct, Byte, Const, this, PascalString, Flag, Switch, ExprAdapter, PrefixedArray, RawCopy, \
	Short
import ipaddress

IPv4Address = ExprAdapter(RawCopy(Byte[4]),
	decoder=lambda obj, ctx: ipaddress.IPv4Address(obj.data),
	encoder=lambda obj, ctx: ipaddress.IPv4Address(obj.data).packed,
)

IPv6Address = ExprAdapter(RawCopy(Byte[16]),
	decoder=lambda obj, ctx: ipaddress.IPv6Address(obj.data),
	encoder=lambda obj, ctx: ipaddress.IPv6Address(obj).packed,
)

AuthMethod = Enum(Byte,
	no_auth = 0x0,
	gssap  = 0x1,
	username_password = 0x2,
)

auth_methods = AuthMethod

ClientGreeting = Struct(
	'version' / Const(5, Byte),
	'auth_methods' / PrefixedArray(Byte, AuthMethod)
)

ServerChoice = Struct(
	'version' / Const(5, Byte),
	'auth_choice' / AuthMethod
)

ClientAuthRequest = Struct(
	'version' / Byte,
	'username' / PascalString(Byte, 'ascii')
)

ServerAuthResponse = Struct(
	'version' / Byte,
	'status' / Flag,
)



Socks5AddressType = Enum(Byte,
	ipv4_address = 0x01,
	domain_name = 0x03,
	ipv6_address = 0x06,
)

# TODO: IPv6 parsing
Socks5Address = Struct(
	'type' / Socks5AddressType,
	'address' / Switch(this.type, {
		Socks5AddressType.ipv4_address: IPv4Address,
		Socks5AddressType.domain_name: PascalString(Byte, 'ascii'),
		# Socks5AddressType.ipv6_address: IPv6Address,
	})
)

Socks5Command = Enum(Byte,
	tcp_connect=0x01,
	tcp_bind_port=0x02,
    udp_bind_port=0x03,
)

ClientConnectionRequest = Struct(
	'version' / Const(5, Byte),
	'cmd' / Socks5Command,
	'reserved' / Const(0, Byte),
	'dest_address' / Socks5Address,
	'dest_port' / Short
)