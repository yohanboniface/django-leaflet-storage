from django.contrib.gis.db import models
from django.db.models import Q

class MapManager(models.GeoManager):
    def visible(self, request):
        filter = Q(share_status=self.model.PUBLIC)

        if request.user.is_authenticated():
            filter = filter | Q(owner=request.user)
            filter = filter | Q(editors=request.user)

        return self.filter(filter)
