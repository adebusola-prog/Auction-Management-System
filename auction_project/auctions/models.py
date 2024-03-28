from django.db import models
from django.db.models import Max
from django.utils import timezone
from django.utils.functional import cached_property
from accounts.models import User
from base.models import BaseModel


class AuctionProduct(BaseModel):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=9, decimal_places=3)
    description = models.TextField(null=True, blank=True)
    bid_start_time = models.DateTimeField()
    bid_end_time = models.DateTimeField()
    is_closed = models.BooleanField(default=False)

    @cached_property
    def status(self):
        current_time = timezone.now()

        if current_time < self.bid_start_time:
            return "Not started"
        elif self.bid_start_time <= current_time < self.bid_end_time:
            return "Ongoing"
        else:
            return "Closed"
    
    @cached_property
    def get_product_bidders(self):
        return self.bids.all()
    
    @cached_property
    def get_product_image_urls(self):
        return self.product_pictures.all()
    
    @cached_property
    def get_highest_bid_price(self):
        highest_bid_price = Bid.objects.filter(auction_product=self).aggregate(Max('price'))['price_max']
        return highest_bid_price if highest_bid_price else self.price
    
    @cached_property
    def get_highest_bid(self):
        highest_price =  Bid.objects.filter(auction_product=self).aggregate(Max('price'))['price__max']
        if highest_price:
            highest_bidders = Bid.objects.filter(auction_product=self, price=highest_price).order_by('time_stamp')
        if highest_bidders.exists():
            return highest_bidders.first()
        
    def __str__(self):
        return self.name
    

class ProductPicture(BaseModel):
    product = models.ForeignKey(AuctionProduct, on_delete=models.SET_NULL, null=True, related_name='product_pictures')
    image = models.ImageField(upload_to='images')

    def __str__(self):
        return f"{self.product.name} picture"
    

class Bid(BaseModel):
    bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bidders')
    auction_product = models.ForeignKey(AuctionProduct, on_delete=models.CASCADE, related_name='bids')
    price = models.PositiveIntegerField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('bidder', 'auction_product')
        ordering = ['-time_stamp']
    
    def __str__(self):
        return f"{self.bidder.email} bid for {self.auction_product.name}__{self.price}"