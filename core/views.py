from django.db.models import Q
from django.db.models import Prefetch

from rest_framework.response import Response
from rest_framework.views import APIView

from store.models import Category, Mobile, Variety
from store.serializers import CategoriesSerializer, MobileSerializer


class GlobalSearchView(APIView):
    """
    A calss to search between selected models.
    """
    def get(self, request, *args, **kwargs):
        # Get the query from the request parameters
        query = request.query_params.get('query', '')

        result = {}

        if query:
            # Search for selected models matching the query in defined fields
            mobiles = Mobile.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            ).distinct().prefetch_related(
                'discount',
                Prefetch(
                    'mobile_vars',
                    queryset=Variety.objects.select_related('color')
                )
            )

            categories = Category.objects.filter(
                Q(title__icontains=query)
            ).distinct().select_related('sub_category')

            # Serialize models
            mobile_serializer = MobileSerializer(mobiles, many=True)
            category_serializer = CategoriesSerializer(categories, many=True)

            # Adds serialized models to the result if exist
            if mobile_serializer.data:
                result['mobiles'] = mobile_serializer.data

            if category_serializer.data:
                result['categories'] = category_serializer.data

        return Response(result)

