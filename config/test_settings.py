from config.settings import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "TEST": {"NAME": ":memory:"},
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Keep tests deterministic and independent of public mapping services. Runtime
# defaults remain OpenStreetMap in config.settings.
GEOCODING_PROVIDER = "stub"
ROUTING_PROVIDER = "stub"
