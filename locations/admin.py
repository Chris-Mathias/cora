from django.contrib import admin

from .models import Country, State, City


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'iso_code2', 'iso_code3', 'phone_code')
    search_fields = ('name', 'iso_code2', 'iso_code3')
    ordering = ('name',)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'uf', 'country')
    search_fields = ('name', 'uf', 'country__name')
    ordering = ('name',)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')
    search_fields = ('name', 'state__name', 'state__country__name')
    ordering = ('name',)
