



from botocore.vendored import requests
from botocore.vendored.requests import adapters

class CustomPynamoSession(requests.Session):
    def __init__(self):
        super(CustomPynamoSession, self).__init__()
        self.mount('http://', adapters.HTTPAdapter(pool_maxsize=100))

session_cls = CustomPynamoSession
