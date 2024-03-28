from django.urls import path
from . import views


urlpatterns = [
    path('', views.AuctionProductsListAPIView.as_view(), name='products'),
    path('<int:pk>', views.AuctionProductDetailAPIView.as_view(), name='product'),
    path('<int:pk>/bid', views.BidCreateAPIView.as_view(), name='bid_product'),
    path('my_bids', views.MyBidsListAPIView.as_view(), name='my_bids'),
    path('<int:product_id>/bids', views.BidsListAPIView.as_view(), name='bids'),
    path('product_highest_bids', views.AuctionProductHighestBidAPIView.as_view(
    ), name='product_highest_bid'),
]

urlpatterns += [
    path('<int:pk>/send_success_mail',
         views.SendSuccessEmailAPIView.as_view(), name='send_mail'),
    path('create-product', views.AuctionProductCreateAPIView.as_view(),
         name='create_product'),
    path('<int:pk>/delete', views.AuctionProductDeleteAPIView.as_view(),
         name='delete_product'),
    path('<int:pk>/update', views.AuctionProductUpdateAPIView.as_view(),
         name='update_product'),
    path('bulk-product-delete', views.BulkDeleteProductAPIView.as_view(),
         name='bulk-delete-auction-product'),
    path('bids/export', views.ExportBidListAPIView.as_view(),
         name='export_bid_list',)
]