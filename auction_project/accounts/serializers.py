from rest_framework import serializers
from .models import User


class AccessSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not value.endswith("afexafrica.com"):
            raise serializers.ValidationError("Invalid email format")
        return value


class LoginSerializer(AccessSerializer):
    otp = serializers.IntegerField()


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email',)