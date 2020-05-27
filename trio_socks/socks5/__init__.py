from .stream import Socks5Stream
from . import error
from . import packets
from .error import ProtocolError, AuthError

from contextlib import asynccontextmanager

@asynccontextmanager
async def make_tcp_stream(destination, proxy):
	stream = None
	try:
		stream = Socks5Stream(destination=destination, proxy=proxy)
		yield stream
	finally:
		if stream is not None:
			await stream.aclose()

