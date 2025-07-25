from django.db import models

class TransportVendor(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    eta = models.CharField(max_length=50)  # e.g. "2 hours"
    capabilities = models.CharField(max_length=100)  # ALS, BLS, etc.

    def __str__(self):
        return self.name
class AuditLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    pickup_location = models.CharField(max_length=100)
    dropoff_location = models.CharField(max_length=100)
    insurance_provider = models.CharField(max_length=100)
    medical_necessity = models.CharField(max_length=100)
    vendor_selected = models.ForeignKey(TransportVendor, on_delete=models.SET_NULL, null=True)
    justification = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} – {self.vendor_selected}"
