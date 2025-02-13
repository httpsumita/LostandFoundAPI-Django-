from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    ITEM_STATUS = (
        ('lost', 'Lost'),
        ('found', 'Found'),
        ('claimed', 'Claimed')
    )

    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='items/', null=True, blank=True)
    location = models.CharField(max_length=200)
    contact_info = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=ITEM_STATUS)
    date = models.DateTimeField(auto_now_add=True) # found or lost on
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    brand = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.status}"
