import ipaddress
import construct

class IPAddressAdapter(construct.Adapter):
	def _decode(self, obj: bytes, context, path) -> str:
		if type(obj) == str:
			return str(ipaddress.ip_address(obj))

		return '.'.join(map(str, obj))

	def _encode(self, obj, context, path) -> bytes:
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
