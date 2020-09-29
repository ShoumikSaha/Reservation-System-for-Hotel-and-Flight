from django.urls import path
from . import views

urlpatterns = [
    path('hotelbooknow', views.hotelbookingpage, name='hotelbookingpage'),
    path('bookingpayment', views.hotelbookingpaymet, name='hotelbookingpaynment'),
    path('bookingok', views.BookingConfirmationPage, name='BookingConfirmationPage'),
    path('check', views.FlightBookingPage, name='FlightBookingPage'),
    path('flightbookingpayment', views.flightbookingpayment, name='flightbookingpayment'),
    path('flightbookingok', views.FlightBookingConfirmationPage, name='FlightBookingConfirmationPage')
]
