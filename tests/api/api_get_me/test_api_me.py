import allure
import pytest
from api.api_list import APIs

@allure.title("Verify that /api/me​ returns exactly user information after login successfully")
@pytest.mark.asyncio
async def test_get_me(api_request, access_token):
    # Call /api/me and check returned user info
    with allure.step("Call GET /api/me"):
        res = await APIs(api_request, access_token).get_me()
        assert res.status == 200

    with allure.step("Verify response"):
        data = await res.json()
        assert data.get("id") is not None
        assert data.get("name") == "Khang Nguyen"
        assert data.get("email") == "mkhang0995.it@gmail.com"
        assert data.get("phone") == "0909111222"
        assert data.get("address") == "59 Lý Thái Tổ, Phường Vườn Lài, Thành phố Hồ Chí Minh"
