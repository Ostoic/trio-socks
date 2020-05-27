import construct
import trio
import ipaddress

from typing import Tuple, Optional
from . import packets
from . import error

class Socks5Stream:
	def __int__(self, destination: Tuple[str, int], proxy: Tuple[str, int]=None, username=None, password=None):
		self._stream: Optional[trio.SocketStream] = None
		self._proxy = proxy
		self._username = username
		self._password = password
		self._destination = destination
		self._negotiated = trio.Event()

	async def _connect_to_proxy(self, address, port):
		"""
		Establish a connection to the desired proxy server
		:param address:
		:param port:
		:return: Socks5Stream stream object
		"""
		self._stream: trio.SocketStream = await trio.open_tcp_stream(address, port)

	async def _negotiate_connection(self, command: packets.Socks5Command, destination: Tuple[str, int]):
		"""
		Negotiate a connection to dst through the established proxy server connection
		:param command: the Socks5 command to execute
		:param destination: the destination
		:return:
		"""
		auth_method = packets.auth_methods.username_password if self._username and self._password \
			else packets.auth_methods.no_auth

		try:
			greeting = packets.ClientGreeting(version=5, auth_methods=[auth_method])
			await self._stream.send_all(greeting.build())

			data = await self._stream.receive_some()
			server_choice = packets.ServerChoice.parse(data)

			if server_choice == packets.auth_methods.no_auth:
				data = await self._stream.receive_some()
				auth_response = packets.ServerAuthResponse.parse(data)
				if not auth_response.status:
					raise error.AuthError('Authentication denied')

			elif server_choice == packets.auth_methods.username_password:
				auth_request = packets.ClientAuthRequest.build({
					'username': self._username,
					'password': self._password
				})

				await self._stream.send_all(auth_request)

				data = await self._stream.receive_some()
				auth_response = packets.ServerAuthResponse.parse(data)

				if not auth_response.status:
					raise error.AuthError('Authentication denied')

			else:
				raise error.ProtocolError('Auth method not supported')

			connection_request = packets.ClientConnectionRequest.build({
				'command': command,
				'destination': destination,
			})

			await self._stream.send_all(connection_request)

			data = await self._stream.receive_some(max_bytes=2048)
			connection_response = packets.ServerConnectionResponse.parse(data)

			if connection_response.status != packets.ServerAuthStatus.request_granted:
				raise error.ProtocolError(f'Server denied connection request: {connection_response.status}')

			self._negotiated.set()

		except (construct.StreamError, construct.ConstError) as e:
			raise error.ProtocolError(e)

		except Exception as e:
			print(e)

	async def _ensure_negotiated(self):
		if not self._negotiated.is_set():
			await self._negotiate_connection(packets.Socks5Command.tcp_connect, self._destination)
			await self._negotiated.wait()

		await trio.lowlevel.checkpoint()

	async def receive_some(self, max_bytes=None):
		return await self._stream.receive_some(max_bytes=max_bytes)

	async def send_all(self, data):

		return await self._stream.send_all(data)

	async def wait_send_all_might_not_block(self):
		return await self._stream.wait_send_all_might_not_block()

	async def send_eof(self):
		return await self._stream.send_eof()

	async def aclose(self):
		self._negotiated = trio.Event()
		await self._stream.aclose()
		self._stream = None



