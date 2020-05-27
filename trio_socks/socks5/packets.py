import construct
import ipaddress

IPv4Address = construct.ExprAdapter(construct.RawCopy(construct.Byte[4]),
	decoder=lambda obj, ctx: ipaddress.IPv4Address(obj.data),
	encoder=lambda obj, ctx: ipaddress.IPv4Address(obj).packed,
)

IPv6Address = construct.ExprAdapter(construct.RawCopy(construct.Byte[16]),
	decoder=lambda obj, ctx: ipaddress.IPv6Address(obj.data),
	encoder=lambda obj, ctx: ipaddress.IPv6Address(obj).packed,
)

AuthMethod = construct.Enum(construct.Byte,
	no_auth = 0x0,
	gssap  = 0x1,
	username_password = 0x2,
)

auth_methods = AuthMethod

ClientGreeting = construct.Struct(
	'version' / construct.Const(5, construct.Byte),
	'auth_methods' / construct.PrefixedArray(construct.Byte, AuthMethod)
)

ServerChoice = construct.Struct(
	'version' / construct.Const(5, construct.Byte),
	'auth_choice' / AuthMethod
)

ClientAuthRequest = construct.Struct(
	'version' / construct.Byte,
	'username' / construct.PascalString(construct.Byte, 'ascii'),
	'password' / construct.PascalString(construct.Byte, 'ascii'),
)

ServerAuthResponse = construct.Struct(
	'version' / construct.Byte,
	'status' / construct.Flag,
)

Socks5AddressType = construct.Enum(construct.Byte,
	ipv4_address = 0x01,
	domain_name = 0x03,
	ipv6_address = 0x06,
)

# TODO: IPv6 parsing
Socks5Address = construct.Struct(
	'type' / Socks5AddressType,
	'address' / construct.Switch(construct.this.type, {
		Socks5AddressType.ipv4_address: IPv4Address,
		Socks5AddressType.domain_name: construct.PascalString(construct.Byte, 'ascii'),
		Socks5AddressType.ipv6_address: IPv6Address,
	})
)

Socks5Command = construct.Enum(construct.Byte,
	tcp_connect=0x01,
	tcp_bind_port=0x02,
    udp_bind_port=0x03,
)

ClientConnectionRequest = construct.Struct(
	'version' / construct.Default(construct.Const(5, construct.Byte), 5),
	'command' / Socks5Command,
	'reserved' / construct.Default(construct.Const(0, construct.Byte), 0),
	'address' / construct.Sequence(Socks5Address, construct.Short),
)

ServerAuthStatus = construct.Enum(construct.Byte,
	request_granted=0x00,
	general_failure=0x01,
	connection_denied_ruleset=0x02,
	network_unreachable=0x03,
	host_unreachable=0x04,
	connection_refused=0x05,
	ttl_expired=0x06,
	protocol_error=0x07,
	address_error=0x08,
)

ServerConnectionResponse = construct.Struct(
	'version' / construct.Const(5, construct.Byte),
	'status' / ServerAuthStatus,
	'reserved' / construct.Const(0, construct.Byte),
	'server_bind_address' / construct.Sequence(Socks5Address, construct.Short),
)