from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    iso_code2 = models.CharField(max_length=2, unique=True)
    iso_code3 = models.CharField(max_length=3, unique=True)
    phone_code = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        ordering = ['name']

    def __str__(self):
        return self.name


class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')
    name = models.CharField(max_length=100)
    uf = models.CharField(max_length=2, unique=True)

    class Meta:
        verbose_name = 'State'
        verbose_name_plural = 'States'
        unique_together = ('country', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.uf}) - {self.country.name}"


class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        unique_together = ('state', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.state.name}, {self.state.country.name}"
