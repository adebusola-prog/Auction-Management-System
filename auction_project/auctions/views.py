import csv
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Max, Q
from rest_framework.generics import(
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    GenericAPIView
)
from rest_framework.views import APIView, status
from .models import AuctionProduct, Bid
from .serializers import (
    AuctionProductSerializer,
    AuctionProductDetailSerializer,
    AuctionProductCreateUpdateSerializer,
    BidSerializer,
    ProductHighestBidSerializer,
    AuctionProductIdsSerializer
)
from channels.layers import get_channel_layer
from asgiref import async_to_sync
from .permissions import IsStaffuserOnlyPermission
from .utils import send_success_email
from .pagination import Paginator


class AuctionProductsListAPIView(ListAPIView):
    """
    API endpoint for listing auction products.

    Attributes:
        queryset (QuerySet): Set of active auction products.
        serializer_class (Serializer): Serializer class for auction products.
        permission_classes (list): List of permission classes.
        pagination_class (Paginator): Paginator class for pagination.

    Methods:
        get_queryset: Retrieves the queryset based on request parameters.
        list: List auction products with pagination.
    """
    queryset = AuctionProduct.active_objects.all()
    serializer_class = AuctionProductSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = Paginator

    def get_queryset(self):
        queryset = self.queryset
        search_param = self.request.query_params.get('search')
        status_param = self.request.query_params.get('status')
        if search_param:
            queryset = self.queryset.filter(name__icontains=search_param)
        if status_param:
            current_time = timezone.now()
            if status_param == 'Not Started':
                queryset = queryset.filter(bid_start_time__gt=current_time)
            elif status_param == 'Ongoing':
                queryset = queryset.filter(
                    Q(bid_start_time__lte=current_time) & Q(
                        bid_end_time__gt=current_time)
                    )
            elif status_param == 'Ended':
                queryset = queryset.filter(bid_end_time__lte=current_time)
        return queryset
    
    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(page, many=True)

        response_data = {
            'responseCode': 200,
            'data': serializer.data,
            'message': 'Auction Product list retrieved successfully'
        }

        return self.get_paginated_response(response_data)
    

class AuctionProductDetailAPIView(RetrieveAPIView):
    """Retreive aution product."""
    queryset = AuctionProduct.objects.all()
    serializer_class = AuctionProductDetailSerializer
    permission_classes =[IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        response_data = {
            'responseCode': 200,
            'data': serializer.data,
            'message': 'Auction Product retreived succesfully'
        }
        return Response(response_data)


class AuctionProductCreateAPIView(CreateAPIView):
    """
    API endpoint for retrieving details of a specific auction product.

    Attributes:
        queryset (QuerySet): Set of all auction products.
        serializer_class (Serializer): Serializer class for auction product details.
        permission_classes (list): List of permission classes.

    Methods:
        retrieve: Retrieves= details of a specific auction product.
    """
    queryset = AuctionProduct.objects.all()
    serializer_class = AuctionProductCreateUpdateSerializer
    permission_classes = [IsStaffuserOnlyPermission]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                'responseCode': 200,
                'data': serializer.data,
                'message': 'AuctionProduct created successfully'
            }
            return Response(response_data)
        
        response_data={
            'responseCode': 400,
            'data': serializer.errors,
            'message': 'Error creating Auction Product'
        }

        return Response(response_data, status=400)
    

class AuctionProductUpdateAPIView(UpdateAPIView):
    """Update an auction product."""
    queryset = AuctionProduct.objects.all()
    serializer_class = AuctionProductCreateUpdateSerializer
    permission_classes = [IsStaffuserOnlyPermission]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serilaizer=serializer)

            response_data = {
                'responseCode': 200,
                'data': serializer.data,
                'message': "Auction Product updated successfully"
            }
            return Response(response_data)
        
        response_data = {
            'responseCode': 400,
            'errors': serializer.errors,
            'message': 'Error updating Auction product' 
        }
        return Response(response_data)
    

class AuctionProductDeleteAPIView(GenericAPIView):
    """Delete an auction product."""
    queryset = AuctionProduct.objects.all()
    serializer_class = AuctionProductSerializer
    permission_classes = [IsStaffuserOnlyPermission]

    def delete(self, request, *args, **kwargs):
        instance = self.queryset.filter(pk=kwargs.get('pk'))
        if not instance.exists():
            response_data = {
                'responseCode': 401,
                'message': 'Invalid Product',
            }
            return Response(response_data)
        instance = instance.first()
        instance.is_active = False
        instance.save()
        response_data = {
            'responseCode': 200,
            'message': 'Auction product deactivated successfully',
        }
        return Response(response_data)
        
            
class BidCreateAPIView(CreateAPIView):
    """Create a bid."""
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        auction_product = get_object_or_404(
            AuctionProduct, id=self.kwargs.get('pk'))

        context = {
            'bidder': request.user,
            'auction_product': auction_product,
            'request': request,
        }

        serializer = self.get_serializer(data=request.data, context=context)

        if serializer.is_valid():
            price = serializer.validated_data.get('price')
            auction_product.price = price
            serializer.save()
            response_data = {
                'responseCode': 200,
                'data': serializer.data,
                'message': 'Bid made successfully'
            }

            serialized_auction_product = AuctionProductDetailSerializer(
                auction_product).data
            auction_group_name = f'auction_{auction_product.id}'
            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                auction_group_name,
                {
                    'type': 'send.bid_update',
                    'bid_data': serialized_auction_product,
                }

            )
            return Response(response_data)

        response_data = {
            'responseCode': 400,
            'errors': serializer.errors,
            'message': 'Error while placing bid'
        }
        return Response(response_data)


class BidsListAPIView(ListAPIView):
    """List all bids."""
    serializer_class = BidSerializer
    pagination_class = Paginator
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Bid.objects.filter(auction_product_id=product_id)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        response_data = {
            'responseCode': 200,
            'data': serializer.data,
            'message': 'Bids list retrieved successfully'
        }
        return self.get_paginated_response(response_data)


class MyBidsListAPIView(ListAPIView):
    """List bids made by the authenticated user with pagination."""
    serializer_class = BidSerializer
    pagination_class = Paginator
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pks = []
        auction_products = Bid.objects.filter(
            bidder=self.request.user).order_by('auction_product_id').distinct('auction_product')

        for p in auction_products:
            bd = Bid.objects.filter(
                bidder=self.request.user, auction_product=p.auction_product).order_by('-price').first()
            pks.append(bd.pk)
        queryset = Bid.objects.filter(pk__in=pks)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        response_data = {
            'responseCode': 200,
            'data': serializer.data,
            'message': 'Your bids list retrieved successfully'
        }
        return self.get_paginated_response(response_data)


class SendSuccessEmailAPIView(APIView):
    """ Send a success email to the highest bidder of a closed auction product."""
    permission_classes = [IsStaffuserOnlyPermission]

    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get('pk')
        product = get_object_or_404(AuctionProduct, id=product_id)
        if product.bid_end_time <= timezone.now():
            highest_bid = product.get_highest_bid
            if highest_bid:
                send_success_email(highest_bid)
                product.is_closed = True
                product.save(updated_fields=['is_closed'])
                response_data = {
                    'responseCode': 200,
                    'message': 'Success email sent to highest bidder'
                }
                return Response(response_data)
        response_data = {
            'responseCode': 400,
            'message': 'Product bidding is still active'
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class AuctionProductHighestBidAPIView(ListAPIView):
    """Retrieves and lists the highest bids for active auction products"""
    queryset = AuctionProduct.active_objects.all()
    serializer_class = ProductHighestBidSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            'responseCode': 200,
            'data': serializer.data,
            'message': 'Product highest bids retrieved successfully'
        }
        return Response(response_data)


class BulkDeleteProductAPIView(GenericAPIView):
    """Delete multiple auction products."""
    queryset = AuctionProduct.active_objects.all()
    permission_classes = [IsStaffuserOnlyPermission]
    serializer_class = AuctionProductIdsSerializer

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            auction_product_ids = serializer.validated_data['expert_card_ids']
            auction_products = AuctionProduct.objects.filter(
                id__in=auction_product_ids)
            auction_products.is_active = False
            auction_products.save()
            response_data = {
                'responseCode': 200,
                'message': 'Auction products deleted successfully',
            }
            return Response(response_data)
        response_data = {
            'responseCode': 200,
            'message': 'Auction products deleted successfully',
        }
        return Response(response_data)


class ExportBidListAPIView(GenericAPIView):
    """Retrieve bid list data and exports it as a CSV file."""
    def get(self, request, *args, **kwargs):
        auction_product = AuctionProduct.active_objects.all().order_by('bid_start_time')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bidlist.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'product name',
            'product_sku',
            'bid_count',
            'highest_bidder',
            'highest bid price',
            'bid time stamp',
        ])
        for product in auction_product:
            highest_bids = product.get_highest_bid
            if highest_bids:
                bidder_email = highest_bids.bidder.email
                highest_bid_price = highest_bids.price
                time_stamp = highest_bids.time_stamp
            else:
                bidder_email = None
                highest_bid_price = None
                time_stamp = None

            writer.writerow([
                product.name,
                product.product_sku,
                product.get_product_bid_count,
                bidder_email,
                highest_bid_price,
                time_stamp,
            ])
        return response