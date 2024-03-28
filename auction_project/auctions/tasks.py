from celery import Celery

from django.utils import timezone

from .models import AuctionProduct

from .utils import send_success_email

app = Celery('auctions')


@app.task
def notify_highest_bidders():
    try:
        auction_products = AuctionProduct.objects.filter(is_closed=False)

        for auction_product in auction_products:

            if (auction_product.bid_end_time >= timezone.now()):

                highest_bid = auction_product.get_highest_bid()

                if highest_bid:
                    send_success_email(highest_bid)

                    auction_product.is_closed = True

                    auction_product.save(updated_fields=['is_closed'])

        return "Task completed: Sent success emails and closed auctions."

    except Exception as e:

        return f"An error occurred: {str(e)}"