from django.db import models

# Create your models here.


class FuelStationModel(models.Model):
    truckstop_id = models.IntegerField(null=True, blank=True)
    truckstop_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    rack_id = models.IntegerField(null=True, blank=True)
    retail_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    full_address = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )

    def __str__(self):
        return f"{self.truckstop_name} ({self.city}, {self.state})"
