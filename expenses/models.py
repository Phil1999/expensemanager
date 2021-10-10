from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
# Create your models here.



class Expense(models.Model):
    # We could also use django-money here
    amount_spent = models.DecimalField(max_digits=19, decimal_places=4)
    date = models.DateField(default=now)
    description = models.TextField()
    category = models.CharField(max_length=255)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.category

    class Meta:
        ordering = ['-date', '-category'] # Note that ordering is not a free operation

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta: # Meta is used to define specific characteristics
        verbose_name_plural = 'Categories'