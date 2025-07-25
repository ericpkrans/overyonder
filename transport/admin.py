from django.contrib import admin
from .models import TransportVendor, AuditLog

admin.site.register(TransportVendor)
admin.site.register(AuditLog)
