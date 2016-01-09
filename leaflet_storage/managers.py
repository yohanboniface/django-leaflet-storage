from django.contrib.gis.db import models
from django.db.models import Q

class MapManager(models.GeoManager):
    def visible(self, request):
        filter = Q(share_status=self.model.PUBLIC)

        return self.filter(filter)
