from django_filters.rest_framework import FilterSet, filters

from .models import Mobile


# class MobileFilter(FilterSet):
#     """
#     A class to filter mobiles based on its own fields.
#     """
#     # TODO similar query problem
#     unit_price = filters.RangeFilter(field_name = 'mobile_vars__unit_price', distinct=True)
#     available = filters.BooleanFilter(field_name='available')
#     picture_resolution = filters.AllValuesFilter(field_name = 'picture_resolution')
#     size = filters.AllValuesFilter(field_name='size')
#     os_type = filters.AllValuesFilter(field_name='os_type')
#     screen_technology = filters.AllValuesFilter(field_name='screen_technology')

#     class Meta:
#         model = Mobile
#         fields = {
#             'name': ['icontains'],
#         }

class MobileFilterSet(FilterSet):
    brand = filters.CharFilter(field_name='category__slug')

    class Meta:
        model = Mobile
        fields = ['brand']

    
    
     