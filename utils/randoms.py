import random
import string

try:
    from api.data.street_address import STREET_ADDRESS
except ModuleNotFoundError:
    STREET_ADDRESS = [{"street_name": "Le Loi", "ward_name": "Ward 1"}]

def random_suffix(length: int = 5) -> str:
    chars = string.ascii_lowercase + "123456789"
    return "".join(random.choice(chars) for _ in range(length))

def random_phone() -> str:
    return f"+84{random.randint(300000000, 999999999)}"

def random_address() -> str:
    house_number = random.randint(10, 500)
    item = random.choice(STREET_ADDRESS)
    return f"{house_number} {item['street_name']}, {item['ward_name']}, Ho Chi Minh City"

def random_email() -> str:
    return f"khangnguyen0995_{random_suffix(5)}@testing.com"


def random_string_alnum(length: int = 5) -> str:
    if length < 2:
        raise ValueError("random_string_alnum length must be at least 2.")

    chars = string.ascii_letters + string.digits
    while True:
        value = "".join(random.choice(chars) for _ in range(length))
        if any(ch.isalpha() for ch in value) and any(ch.isdigit() for ch in value):
            return value


def random_password(suffix_length: int = 5) -> str:
    return f"Khang_qa_{random_string_alnum(suffix_length)}"
