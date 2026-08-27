from rest_framework import serializers


class PasswordField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs.setdefault("min_length", 6)
        super().__init__(**kwargs)
