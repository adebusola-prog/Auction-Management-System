from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import AccessSerializer, LoginSerializer
from .models import User
from .utils import send_otp_email, generate_otp



class AccessAPIView(APIView):
    serializer_class = AccessSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user, created = User.objects.get_or_create(email=email)
            otp = generate_otp()
            user.otp = otp
            user.save(update_fields=["otp"])
            send_otp_email(email=email, otp=otp)

            response_data = {
                'responseCode': 200,
                'message': f'OTP sent to {email} successfully'
            }
            return Response(response_data)

        response_data = {
            'responseCode': 400,
            'errors': serializer.errors,
            'message': 'Error sending OTP'
            }
        return Response(response_data, status=400)
    

class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            otp = serializer.validated_data['otp']
            user = User.objects.filter(otp=otp).first()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            user.otp = ''
            user.save()

            response_data = {
                'responseCode': 100,
                'message': 'Login successful',
                'data': {'access_token': access_token, 'refresh_token': refresh_token,
                'email': user.email}
            }
            return Response(response_data)
        
        response_data = {
            'responseCode': 400,
            'errors': serializer.errors,
            'message': 'Error during login',
        }
        return Response(response_data)
    

class AdminLoginAPIView(APIView):

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response_data = {
                "responseCode": 100,
                "message": "Login successful",
                'data': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'email': user.email,
                }
            }

            return Response(response_data)
        else:
            response_data = {
                'responseCode': 401,
                'message': 'Invalid email or password',
            }
            return Response(response_data)