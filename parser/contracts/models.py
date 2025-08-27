from django.db import models


class Contract(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    file = models.FileField(upload_to="contracts/")
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    progress = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    # Simplified extracted data fields
    parties = models.JSONField(default=dict, blank=True)
    account_info = models.JSONField(default=dict, blank=True)
    financial_details = models.JSONField(default=dict, blank=True)
    payment_structure = models.JSONField(default=dict, blank=True)
    revenue_classification = models.JSONField(default=dict, blank=True)
    sla = models.JSONField(default=dict, blank=True)
    score = models.PositiveIntegerField(default=0)
    gaps = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return f"Contract #{self.pk} - {self.original_filename}"



