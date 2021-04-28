import construct
import trio
import ipaddress

from typing import Tuple, Optional, Iterable
from .error import ProtocolError, AuthError
from . import packets

def _determine_address_type(address):
	try:
		version = ipaddress.ip_address(address)
		if type(version) is ipaddress.IPv4Address:
			return packets.Socks5AddressType.ipv4_address

		elif type(version) is ipaddress.IPv6Address:
			return packets.Socks5AddressType.ipv6_address

	# On exception we assume the address is a domain name
	except (ValueError, TypeError):
		pass

	return packets.Socks5AddressType.domain_name

class Socks5Stream(trio.abc.HalfCloseableStream):
	def __init__(self, destination: Tuple[str, int], proxy: Tuple[str, int]=None, username=None, password=None, stream=None, negotiate=False):
		self._stream: Optional[trio.abc.HalfCloseableStream] = stream
		self._proxy = proxy
		self._username = username
		self._password = password
		self._destination = destination
		self._negotiated = trio.Event()
		self._init_negotiate = bool(negotiate)
		self._local_addr = '?'

	async def __aenter__(self):
		if self._init_negotiate:
			await self.negotiate()

		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		if self._stream is not None:
			await self.aclose()

	async def _authenticate(self, auth_choice):
		if auth_choice == packets.auth_methods.username_password:
			auth_request = packets.ClientAuthRequest.build({
				'username': self._username,
				'password': self._password
			})

			await self._stream.send_all(auth_request)

			data = await self._stream.receive_some(max_bytes=packets.ServerAuthResponse.sizeof())
			if data is None or len(data) == 0:
				raise ProtocolError('Connection closed unexpectedly')

			auth_response = packets.ServerAuthResponse.parse(data)

			if not auth_response.status:
				raise AuthError('Authentication denied')

		elif auth_choice == packets.auth_methods.no_auth:
			await trio.lowlevel.checkpoint()

		else:
			raise AuthError(f'Authentication method not supported: {auth_choice}')

	async def _send_greeting(self, auth_methods: Iterable):
		greeting = packets.ClientGreeting.build({
			'auth_methods': auth_methods
		})

		await self._stream.send_all(greeting)

	async def _receive_server_choice(self):
		data = await self._stream.receive_some(max_bytes=packets.ServerChoice.sizeof())
		if data is None or len(data) == 0:
			raise ProtocolError('Connection closed unexpectedly')
		return data

	async def _send_connection_request(self, command, address: Tuple[str, int]):
		address_type = _determine_address_type(address[0])

		connection_request = packets.ClientConnectionRequest.build({
			'command': command,
			'address': (
				{'type': address_type, 'address': address[0]},
				address[1]
			)
		})

		await self._stream.send_all(connection_request)

	async def _receive_connection_response(self) -> packets.ServerConnectionResponse:
		data = await self._stream.receive_some()
		if data is None or len(data) == 0:
			raise ProtocolError('Connection closed unexpectedly')

		connection_response = packets.ServerConnectionResponse.parse(data)
		if connection_response.status != packets.ServerAuthStatus.request_granted:
			raise ProtocolError(f'Server denied connection request: {connection_response.status}')

		self._negotiated.set()
		return connection_response

	async def _negotiate_connection(self, command: packets.Socks5Command, destination: Tuple[str, int]):
		"""
		Perform the command in association with the address through the established proxy server connection
		:param command: the Socks5 command to execute
		:param destination: the address
		:return:
		"""
		auth_methods = [packets.auth_methods.no_auth]
		if self._username is not None and self._password is not None:
			auth_methods.append(packets.auth_methods.username_password)

		try:
			await self._send_greeting(auth_methods)
			data = await self._receive_server_choice()
			if data is None or len(data) == 0:
				raise ProtocolError('Connection closed unexpectedly')

			packet = packets.ServerChoice.parse(data)
			auth_choice = packet.auth_choice

			await self._authenticate(auth_choice)
			await self._send_connection_request(command, destination)
			await self._receive_connection_response()

		except (construct.StreamError, construct.ConstError) as e:
			raise ProtocolError(e)

	async def _ensure_negotiated(self, command: packets.Socks5Command=packets.Socks5Command.tcp_connect):
		if self._stream is None:
			self._stream = await trio.open_tcp_stream(*self._proxy)
			self._local_addr = trio.socket.gethostname()

		if not self._negotiated.is_set():
			await self._negotiate_connection(command, self._destination)

	async def negotiate(self):
		if self._stream is None or not self._negotiated.is_set():
			await self._ensure_negotiated()

		await trio.lowlevel.checkpoint()

	async def receive_some(self, max_bytes=None):
		await self._ensure_negotiated()
		data = await self._stream.receive_some(max_bytes=max_bytes)
		if data is None or len(data) == 0:
			raise ProtocolError('Connection closed unexpectedly')
		return data

	async def send_all(self, data):
		await self._ensure_negotiated()
		await self._stream.send_all(data)

	async def wait_send_all_might_not_block(self):
		await self._ensure_negotiated()
		return await self._stream.wait_send_all_might_not_block()

	async def send_eof(self):
		if not self._negotiated.is_set():
			raise ProtocolError('Negotiation not yet completed')

		return await self._stream.send_eof()

	async def aclose(self):
		self._negotiated = trio.Event()
		await self._stream.aclose()
		self._stream = None
