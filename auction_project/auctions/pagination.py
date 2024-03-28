from rest_framework.pagination import PageNumberPagination
from django.conf import settings
import math
from collections import OrderedDict

from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class Paginator(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE', 10)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('total_page', math.ceil(self.page.paginator.count / int(self.request.GET.get('page_size', self.page_size)))),
            ('page', int(self.request.GET.get('page', 1))),
            ('page_size', int(self.request.GET.get('page_size', self.page_size))),
            ('results', data)
        ]))
