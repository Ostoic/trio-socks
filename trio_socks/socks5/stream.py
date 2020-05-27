import sys
import construct
import trio
import ipaddress

from typing import Tuple, Optional
from . import packets
from . import error

import logging
logging.basicConfig(
	level=logging.DEBUG,
	stream=sys.stdout,
	format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
	datefmt='%H:%M:%S',
)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Socks5Stream:
	def __init__(self, destination: Tuple[str, int], proxy: Tuple[str, int]=None, username=None, password=None):
		self._stream: Optional[trio.SocketStream] = None
		self._proxy = proxy
		self._username = username
		self._password = password
		self._destination = destination
		self._negotiated = trio.Event()

	async def _authenticate(self, auth_choice):
		log.debug(f'authenticating via {auth_choice}')
		if auth_choice == packets.auth_methods.username_password:
			auth_request = packets.ClientAuthRequest.build({
				'username': self._username,
				'password': self._password
			})

			await self._stream.send_all(auth_request)

			data = await self._stream.receive_some(max_bytes=packets.ServerAuthResponse.sizeof())
			auth_response = packets.ServerAuthResponse.parse(data)

			if not auth_response.status:
				raise error.AuthError('Authentication denied')
		elif auth_choice == packets.auth_methods.no_auth:
			pass
		else:
			raise error.AuthError(f'Authentication method not supported: {auth_choice}')

	async def _negotiate_connection(self, command: packets.Socks5Command, address: Tuple[str, int]):
		"""
		Perform the command in association with the address through the established proxy server connection
		:param command: the Socks5 command to execute
		:param destination: the destination
		:return:
		"""
		auth_method = packets.auth_methods.username_password if self._username and self._password \
			else packets.auth_methods.no_auth

		log.debug(f'{auth_method=}')

		try:
			greeting = packets.ClientGreeting.build({
				'auth_methods': [auth_method]
			})

			await self._stream.send_all(greeting)

			data = await self._stream.receive_some(max_bytes=packets.ServerChoice.sizeof())
			auth_choice = packets.ServerChoice.parse(data).auth_choice
			await self._authenticate(auth_choice)

			log.debug('authenticated')
			address_type = packets.Socks5AddressType.domain_name
			try:
				version = ipaddress.ip_address(self._destination[0]).type
				if version == 6:
					address_type = packets.Socks5AddressType.ipv6_address
				elif version == 4:
					address_type = packets.Socks5AddressType.ipv4_address
				else:
					raise ValueError('Invalid address')
			except:
				pass

			connection_request = packets.ClientConnectionRequest.build({
				'command': command,
				'address': (
					{'type': address_type, 'address': self._destination[0]},
					self._destination[1]
				)
			})

			await self._stream.send_all(connection_request)
			log.debug(f'connection request sent: {packets.ClientConnectionRequest.parse(connection_request)}')

			data = await self._stream.receive_some()
			connection_response = packets.ServerConnectionResponse.parse(data)

			if connection_response.status != packets.ServerAuthStatus.request_granted:
				raise error.ProtocolError(f'Server denied connection request: {connection_response.status}')

			# (address, port) = connection_response.server_bind_address.address
			log.debug(connection_response.server_bind_address)
			self._negotiated.set()

		except (construct.StreamError, construct.ConstError) as e:
			raise error.ProtocolError(e)

	async def _ensure_negotiated(self):
		if self._stream is None:
			log.debug('connecting to proxy')
			self._stream = await trio.open_tcp_stream(*self._proxy)
			log.debug('connected to proxy')

		if not self._negotiated.is_set():
			log.debug(f'negotiating connection to: {self._destination}')
			await self._negotiate_connection(packets.Socks5Command.tcp_connect, self._destination)
			log.debug(f'negotiated connection to: {self._destination}')

	async def receive_some(self, max_bytes=None):
		await self._ensure_negotiated()
		return await self._stream.receive_some(max_bytes=max_bytes)

	async def send_all(self, data):
		await self._ensure_negotiated()
		return await self._stream.send_all(data)

	async def wait_send_all_might_not_block(self):
		await self._ensure_negotiated()
		return await self._stream.wait_send_all_might_not_block()

	async def send_eof(self):
		if not self._negotiated.is_set():
			raise error.ProtocolError('Negotiation not yet had')

		return await self._stream.send_eof()

	async def aclose(self):
		log.debug('aclose')
		self._negotiated = trio.Event()
		await self._stream.aclose()
		self._stream = None
