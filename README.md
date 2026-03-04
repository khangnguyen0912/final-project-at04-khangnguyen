# Final Project AT04 - API/UI Automation

This is an automation test project for `https://book.anhtester.com/`.
Tools:
- `pytest`
- `playwright`
- `allure-pytest`

## 1. Setup

```bash
pip install -r requirements.txt
playwright install
```

Create `.env`:

```env
API_BASE_URL=https://book.anhtester.com/
BASE_URL=https://book.anhtester.com/
EMAIL=mkhang0995.it@gmail.com
PASSWORD=Kh@ng_qa1234
UI_SLOW_MO=1000
```

## 2. Test folders

- `tests/ui`: UI tests
- `tests/api`: API tests
- `tests/api/api_patch_profile/single_field`: API tests for one field update

## 3. Run tests

Run all UI tests:

```bash
pta tests/ui
```

Run all API tests:

```bash
pta tests/api
```

Run one folder:

```bash
pta tests/api/api_patch_profile/single_field
```

Run one file:

```bash
pta tests/ui/test_update_profile.py
pta tests/api/api_patch_profile/single_field/test_update_email_field.py
```

## 4. Notes

- After each test case, the framework tries login with `EMAIL/PASSWORD` in `.env`.
- If login fails, the framework calls `POST /api/register` to make sure the default account is ready for the next case.
