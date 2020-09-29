from django.urls import path
from . import views

urlpatterns = [
    path('adminDash', views.admindash, name='SiteAdminDash'),
    path('viewHotels', views.viewHotels, name='HotelList'),
    path('viewAirlines', views.viewAirlines, name='AirlinesList'),
    path('viewPaymentLog', views.viewPaymentLog, name='HotelPaymentLog'),
    path('viewAirlinesPaymentLog', views.viewAirlinesPaymentLog, name='AirlinesPaymentLog'),
    path('approveHotelBookings', views.approveHotelBookings, name='ApproveHotelBooking'),
    path('approveFlightBookings', views.approveFlightBookings, name='ApproveFlightBooking'),
    path('approvedhotelbooking', views.approveHotelBookingRedirect, name='ApproveHotelBookingRedirect'),
    path('approvedflightbooking', views.approveFlightBookingRedirect, name='ApproveFlightBookingRedirect'),
    path('viewStats', views.viewStats, name='Statistics'),
]
