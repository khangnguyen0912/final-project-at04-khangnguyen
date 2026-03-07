def build_register_payload(email: str, password: str) -> dict:
    return {
        "name": "Khang Iris",
        "email": email,
        "password": password,
        "phone": "0990111222",
        "address": "59 Lý Thái Tổ, Phường Vườn Lài, Thành phố Hồ Chí Minh",
    }
