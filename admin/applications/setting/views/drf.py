from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from applications.setting.models import City
from applications.setting.serializers import CitySerializer


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    @action(detail=False, methods=['post'], url_path='by-province')
    def by_province(self, request):
     province_id = request.data.get('id')
     if not province_id:
          return Response({'data': []}, status=status.HTTP_200_OK)

     cities = self.get_queryset().filter(province_id=province_id)
     serializer = self.get_serializer(cities, many=True)
     # label رو هم اضافه می‌کنیم تا با رندر اولیه‌ی قالب یکسان باشد
     data = [
          {'id': item['id'], 'name': item['name'], 'label': item['name']}
          for item in serializer.data
     ]
     return Response({'data': data}, status=status.HTTP_200_OK)