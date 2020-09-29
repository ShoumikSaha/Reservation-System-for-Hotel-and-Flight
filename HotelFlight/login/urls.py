from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('reg/', views.reg, name='reg'),
    path('logout/', views.logoutUser, name='logout'),
    path('userbookings', views.userbookings, name='userBookings'),
    path('userflightbookings', views.userflightbookings, name='userFlightBookings'),
    path('usernotifications', views.usernotifications, name='userNotifications'),
    path('userbookingcancel', views.bookingcancel, name='userBookingCancel'),
    path('userflightbookingcancel', views.flightbookingcancel, name='userFlightBookingCancel'),
    path('bookingcancelredirect', views.bookingcancelredirect, name='bookingCancelRedirect'),
    path('flightbookingcancelredirect', views.flightbookingcancelredirect, name='flightBookingCancelRedirect'),
]
