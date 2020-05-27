import construct

Version = construct.Enum(construct.Byte, v4=0x4, v5=0x5)
versions = Version