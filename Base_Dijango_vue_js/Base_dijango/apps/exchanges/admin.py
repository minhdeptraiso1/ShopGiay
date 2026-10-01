from django.contrib import admin

from .models import ExchangeItem, ExchangeRequest, ExchangeReservation, ExchangeStatusHistory

admin.site.register((ExchangeRequest, ExchangeItem, ExchangeReservation, ExchangeStatusHistory))
