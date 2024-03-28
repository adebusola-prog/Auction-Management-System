from django.contrib import admin
from .models import AuctionProduct, ProductPicture, Bid


class ProductPictureInline(admin.TabularInline):
    model = ProductPicture
    extra = 0


class BidInline(admin.TabularInline):
    model = Bid
    extra = 0


@admin.register(AuctionProduct)
class AuctionProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'bid_start_time', 'bid_end_time', 'status')
    inlines = [ProductPictureInline, BidInline]


@admin.register(ProductPicture)
class ProductPictureAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('bidder', 'auction_product', 'price', 'time_stamp')