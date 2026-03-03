import requests

class APIClient:
    def __init__(self, base_url: str, token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def post(self, path: str, json: dict | None = None):
        return self.session.post(self.base_url + path, json=json, timeout=30)

    def get(self, path: str):
        return self.session.get(self.base_url + path, timeout=30)

    def patch(self, path: str, json: dict):
        return self.session.patch(self.base_url + path, json=json, timeout=30)