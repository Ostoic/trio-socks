import trio

class Socks5Stream(trio.SocketStream):
	def __int__(self, destination, proxy=None, username=None, password=None):
		self._proxy = proxy
		self._username = username
		self._password = password
		self._destination = destination
		# self._handshook

	async def _negotiate_

	async def _connect_to_proxy(self, address, port) -> trio.SocketStream:
		"""
		Establish a connection to the desired proxy server
		:param address:
		:param port:
		:return: trio.SocketStream stream object
		"""
		return await trio.open_tcp_stream(address, port)

async def _SOCKS5_request(self, cmd, dst):
	"""
	Send SOCKS5 request with given command (CMD field) and
	address (DST field). Returns resolved DST address that was used.
	"""
	proxy_type, addr, port, rdns, username, password = self.proxy

	try:
		# First we'll send the authentication packages we support.
		if username and password:
			# The username/password details were supplied to the
			# set_proxy method so we support the USERNAME/PASSWORD
			# authentication (in addition to the standard none).
			writer.write(b"\x05\x02\x00\x02")
		else:
			# No username/password were entered, therefore we
			# only support connections with no authentication.
			writer.write(b"\x05\x01\x00")

		# We'll receive the server's response to determine which
		# method was selected
		auth_data = await proxy.receive_some(2)
		if auth_data[0:1]
		writer.flush()
		chosen_auth = self._readall(reader, 2)

		if chosen_auth[0:1] != b"\x05":
			# Note: string[i:i+1] is used because indexing of a bytestring
			# via bytestring[i] yields an integer in Python 3
			raise ProxyProtocolError('SOCKS5 proxy server sent invalid data')

		# Check the chosen authentication method

		if chosen_auth[1:2] == b"\x02":
			# Okay, we need to perform a basic username/password
			# authentication.
			if not (username and password):
				# Although we said we don't support authentication, the
				# server may still request basic username/password
				# authentication
				raise SOCKS5AuthError("No username/password supplied. "
				                      "Server requested username/password"
				                      " authentication")

			writer.write(b"\x01" + chr(len(username)).encode()
			             + username
			             + chr(len(password)).encode()
			             + password)
			writer.flush()
			auth_status = self._readall(reader, 2)
			if auth_status[0:1] != b"\x01":
				# Bad response
				raise GeneralProxyError(
					"SOCKS5 proxy server sent invalid data")
			if auth_status[1:2] != b"\x00":
				# Authentication failed
				raise SOCKS5AuthError("SOCKS5 authentication failed")

		# Otherwise, authentication succeeded

		# No authentication is required if 0x00
		elif chosen_auth[1:2] != b"\x00":
			# Reaching here is always bad
			if chosen_auth[1:2] == b"\xFF":
				raise SOCKS5AuthError(
					"All offered SOCKS5 authentication methods were"
					" rejected")
			else:
				raise GeneralProxyError(
					"SOCKS5 proxy server sent invalid data")

		# Now we can request the actual connection
		writer.write(b"\x05" + cmd + b"\x00")
		resolved = self._write_SOCKS5_address(dst, writer)
		writer.flush()

		# Get the response
		resp = self._readall(reader, 3)
		if resp[0:1] != b"\x05":
			raise GeneralProxyError(
				"SOCKS5 proxy server sent invalid data")

		status = ord(resp[1:2])
		if status != 0x00:
			# Connection failed: server returned an error
			error = SOCKS5_ERRORS.get(status, "Unknown error")
			raise SOCKS5Error("{:#04x}: {}".format(status, error))

		# Get the bound address/port
		bnd = self._read_SOCKS5_address(reader)

		super(socksocket, self).settimeout(self._timeout)
		return (resolved, bnd)
	finally:
		reader.close()
		writer.close()
