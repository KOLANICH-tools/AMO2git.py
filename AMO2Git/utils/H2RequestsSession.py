import requests

try:
	from hyper.contrib import HTTP20Adapter

	hyperHttp2Adapter = HTTP20Adapter()
except:
	hyperHttp2Adapter = None


class H2RequestsSession(requests.Session):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if hyperHttp2Adapter:
			self.mount("https://", hyperHttp2Adapter)
			self.mount("http://", hyperHttp2Adapter)
