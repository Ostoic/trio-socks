from enum import Enum

from generic_struct.parsers.StaticField import StaticFieldParser, UnsignedIntFormats
from generic_struct.structs.GenericStruct import build_struct
from generic_struct.parsers.DynamicSizeList import DynamicSizeListParser

class AuthMethods(Enum):
	no_auth = 0x0
	gssap  = 0x1
	username_password = 0x2

@build_struct
class ClientGreeting:
	version = StaticFieldParser(UnsignedIntFormats.BYTE)
	auth_methods = DynamicSizeListParser(
		element_parser=FactoryFieldParser(Factory=AuthMethods),
		size_parser=StaticFieldParser(UnsignedIntFormats.BYTE)
	)