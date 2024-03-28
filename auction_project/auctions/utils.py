import time
import random
import string
from django.core.mail import send_mail
from django.conf import settings


def send_success_email(highest_bid):
    subject = 'Auction Success'
    message = f'Congratulations! You have won the auction for {highest_bid.auction_product.name} \
    with a bid of {highest_bid.price}. Kindly pay within the next 24 hours to validate your win'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [highest_bid.bidder.email]
    
    send_mail(subject, message, from_email, recipient_list)

def generate_sku(product_name):
    timestamp = int(time.time())
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    
    sku = f"{product_name[:2].upper()}-{timestamp}-{random_suffix}"
    return sku