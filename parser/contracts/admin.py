from django.contrib import admin
from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("id", "original_filename", "status", "progress", "uploaded_at")
    list_filter = ("status", "uploaded_at")
    search_fields = ("original_filename",)



