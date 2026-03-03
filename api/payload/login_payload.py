def build_login_payload(email: str, password: str) -> dict:
    return {
        "email": email,
        "password": password,
    }