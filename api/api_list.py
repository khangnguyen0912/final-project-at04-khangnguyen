import json
import allure
from playwright.async_api import Error as PlaywrightError
from api.core.endpoints import ME, PROFILE

class APIs:
    def __init__(self, api_request, token: str):
        self.api_request = api_request
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def _attach_request_payload(self, name: str, payload):
        attachment_type = allure.attachment_type.TEXT

        if payload is None:
            payload_text = "{}"
            attachment_type = allure.attachment_type.JSON
        elif isinstance(payload, (dict, list)):
            payload_text = json.dumps(payload, ensure_ascii=False, indent=2)
            attachment_type = allure.attachment_type.JSON
        else:
            payload_text = str(payload)
            try:
                parsed = json.loads(payload_text)
                payload_text = json.dumps(parsed, ensure_ascii=False, indent=2)
                attachment_type = allure.attachment_type.JSON
            except Exception:
                attachment_type = allure.attachment_type.TEXT

        allure.attach(payload_text, name, attachment_type)

    async def _attach_response_payload(self, name: str, res):
        try:
            text = await res.text()
        except Exception:
            text = "<cannot read response text>"
        allure.attach(f"{res.status}\n{text}", name, allure.attachment_type.TEXT)

    async def get_me(self, timeout: int = 15000):
        await self._attach_request_payload("GET /me request payload", {})
        try:
            res = await self.api_request.get(
                ME,
                headers=self.headers,
                timeout=timeout,
            )
        except PlaywrightError as e:
            allure.attach(str(e), "GET /me PlaywrightError", allure.attachment_type.TEXT)
            raise
        await self._attach_response_payload("GET /me response payload", res)
        return res

    async def update_profile(self, payload: str, timeout: int = 15000):
        await self._attach_request_payload("PATCH /profile request payload", payload)
        try:
            res = await self.api_request.patch(
                PROFILE,
                headers=self.headers,
                data=payload,
                timeout=timeout,
            )
        except PlaywrightError as e:
            allure.attach(str(e), "PATCH /profile PlaywrightError", allure.attachment_type.TEXT)
            raise
        await self._attach_response_payload("PATCH /profile response payload", res)
        return res