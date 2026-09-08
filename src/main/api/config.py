import os


BASE_URL = os.getenv("BANK_API_URL", "http://localhost:4111")
ADMIN_USERNAME = os.getenv("BANK_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("BANK_ADMIN_PASSWORD", "123456")

USER_PASSWORD = "Pas!sw0rd"
REQUEST_TIMEOUT = 10