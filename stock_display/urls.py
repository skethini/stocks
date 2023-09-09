from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name = "home"),
    path('autocomplete_ticker', views.autocomplete_ticker, name='autocomplete_ticker')
]

