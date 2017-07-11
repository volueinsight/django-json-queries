from django.db import models


class Manufacturer(models.Model):
    name = models.CharField()


class Product(models.Model):
    name = models.CharField()
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
