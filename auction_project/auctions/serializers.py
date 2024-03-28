from django.db.models import Max
from django.utils import timezone
from rest_framework import serializers
from .models import AuctionProduct, ProductPicture, Bid
from .utils import generate_sku
from accounts.serializers import AccountSerializer


class ProductPictureSerializer(serializers.Serializer):
    image = serializers.ImageField


class AuctionProductSerializer(serializers):
    get_product_image_urls = ProductPictureSerializer(many=True)
    highest_bid_price = serializers.CharField(source='get_highest_bid_price')
    highest_bidder = serializers.CharField(source='get_highest_bid')

    class Meta:
        model = AuctionProduct
        fields = (
            'id',
            'name',
            'price',
            'bid_start_time',
            'description',
            'bid_end_time',
            'get_product_bid_count',
            'highest_bidder',
            'highest_bid_price',
            'product_sku',
            'status',
            'get_product_image_urls'
        )

    extra_kwargs = {
        'get_product_image_urls': {'read_only': True},
    }

class AuctionProductCreateUpdateSerializer(serializers.ModelSerializer):
    product_picture = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True, required=False
    )

    class Meta:
        model = AuctionProduct
        fields = (
            'id',
            'name',
            'price',
            'description',
            'product_picture',
            'bid_start_time',
            'bid_end_time',
            'product_sku',
        )

    def validate(self, data):
        bid_start_time = data.get('bid_start_time')
        bid_end_time = data.get('bid_end_time')

        if data.get('product_sku'):
            check_sku = AuctionProduct.objects.filter(
                product_sku=data.get('product_sku'))
            if check_sku.exists():
                raise serializers.ValidationError(
                    'Product with serial number already exists')
        if bid_start_time == bid_end_time:
            raise serializers.ValidationError(
                'start and end time can not be the same')
        if bid_start_time and bid_start_time + timezone.timedelta(hours=1) < timezone.now():
            raise serializers.ValidationError(
                'bid start time cannot be before the current time'
            )
        if bid_start_time and bid_end_time and bid_start_time >= bid_end_time:
            raise serializers.ValidationError(
                'bid start time must be before bid end time')
        return data

    def create(self, validated_data):
        picture_data = None
        if validated_data.get('product_picture'):
            picture_data = validated_data.pop('product_picture')

        product = AuctionProduct.objects.create(**validated_data)
        product.save()

        if picture_data:
            product_images = [ProductPicture(
                product=product, image=image) for image in picture_data]
            ProductPicture.objects.bulk_create(product_images)
        return product

    def update(self, instance, validated_data):
        if instance.status == 'Ongoing':
            bid_end_time = validated_data.get(
                'bid_end_time', instance.bid_end_time)
            instance.bid_end_time = bid_end_time
            instance.save()
        else:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class BidSerializer(serializers.ModelSerializer):
    
    auction_product = AuctionProductSerializer(read_only=True)
    bidder = AccountSerializer(read_only=True)

    class Meta:
        model = Bid
        fields = (
            'auction_product',
            'bidder',
            'price',
            'time_stamp'
        )

        extra_kwargs = {
            'time_stamp': {'read_only': True},
        }

    def validate(self, data):
        bidder = self.context.get('bidder')
        auction_product = self.context.get('auction_product')

        if auction_product.bid_start_time >= timezone.now():
            raise serializers.ValidationError('Sorry, auction is yet to start')
        if timezone.now() > auction_product.bid_end_time:
            raise serializers.ValidationError('Sorry, the auction has ended')

        bid = Bid.objects.filter(
            auction_product=auction_product)

        highest_bid = bid.aggregate(Max('price'))
        if highest_bid['price__max'] is not None:
            highest_bidder = Bid.objects.filter(
                auction_product=auction_product, price=highest_bid['price__max']).first()
            if highest_bidder.bidder.id is bidder.id:
                raise serializers.ValidationError(
                    "You are currently the highest bidder, you can't place another bid")

        if data['price'] <= auction_product.price:
            raise serializers.ValidationError(
                "Your bid price must be higher than the product's initial price."
            )

        highest_price = bid.aggregate(Max('price'))['price__max']

        if highest_price is not None and data['price'] <= highest_price:
            raise serializers.ValidationError(
                "Your bid price must be higher than the current highest bid."
            )

        data['bidder'] = bidder
        data['auction_product'] = auction_product
        return data


class AuctionProductDetailSerializer(serializers.ModelSerializer):
    get_product_bidders = BidSerializer(many=True)
    highest_bid_price = serializers.CharField(source='get_highest_bid_price')
    get_product_image_urls = ProductPictureSerializer(many=True)

    class Meta:
        model = AuctionProduct
        fields = (
            'id',
            'name',
            'price',
            'bid_start_time',
            'bid_end_time',
            'description',
            'status',
            'product_sku',
            'highest_bid_price',
            'get_product_bidders',
            'get_product_image_urls',

        )

        extra_kwargs = {
            'get_product_image_urls': {'read_only': True},
        }


class ProductHighestBidSerializer(serializers.Serializer):
    name = serializers.CharField()
    current_highest_bid = serializers.CharField(source='get_highest_bid_price')

    class Meta:
        fields = ['name', 'current_highest_bid']


class AuctionProductIdsSerializer(serializers.Serializer):
    auction_product_ids = serializers.ListField(
        child=serializers.IntegerField())