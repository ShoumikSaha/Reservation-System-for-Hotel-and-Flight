from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('hotelRooms', views.hotelrooms, name='hotelRoomsPage'),
    path('searchHotel', views.searchHotelPage, name='searchHotelPage'),
    path('searchFlight', views.searchFlightPage, name='searchFlightPage'),
]
