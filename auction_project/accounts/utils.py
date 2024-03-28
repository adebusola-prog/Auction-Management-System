import random
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


def generate_otp(length=4):
    otp_number = [str(random.randint(1, 9)) for i in range(length)]
    otp = ''.join(otp_number)
    return otp

def send_otp_email(email, otp):
    subject = 'YOUR OTP CODE',
    login_url = reverse('login')
    message = f'Your OTP code is: {otp} \nPlease use this code to login at {login_url}'
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, [email], fail_silently=False)