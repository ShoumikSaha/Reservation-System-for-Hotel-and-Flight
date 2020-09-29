from django.shortcuts import render
from .forms import ProfileForm, UserCreateForm
from django.http import HttpResponseRedirect
from django.contrib import auth, messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from database import models
from django.db import connection
from collections import namedtuple
from database.models import Booking, Cancellation_Log
from database.models import *


# Create your views here.
def isHotel(user):
    return user.groups.filter(name='Hotel').exists()


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def login(request):
    redirect_to = request.GET.get('next', '')
    if request.method == 'POST':
        Username = request.POST.get("username", "")
        Password = request.POST.get("pass", "")
        user = auth.authenticate(request, username=Username, password=Password)
        if user is not None:
            auth.login(request, user)
            if isHotel(user):
                return HttpResponseRedirect('/adminHotelDash')
            return HttpResponseRedirect(redirect_to)
        else:
            messages.error(request, 'Username or password not correct')
    return render(request, "login/login.html")


def reg(request):
    submitted = False
    if request.method == 'POST':
        userform = UserCreateForm(request.POST)
        profileform = ProfileForm(request.POST)
        if userform.is_valid() and profileform.is_valid():
            user = userform.save()
            profile = profileform.save(commit=False)
            profile.user = user
            profile.save()
            return HttpResponseRedirect('/login?next=/')
        else:
            print(userform.errors)
    else:
        userform = UserCreateForm()
        profileform = ProfileForm()
    return render(request, "login/reg.html", {'userform': userform, 'profileform': profileform, 'submitted': submitted})


def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/')


def userbookings(request):
    cursor = connection.cursor()
    cursor.execute(
        "select distinct HB.Checkin_Date,HB.Checkout_Date,H.Hotel_Name,B.User_id,HR.Price*HB.TotalRooms as 'Price',"
        "(B.PaidMoney) as 'Paid',B.MoneyToPay as 'Pending',B.MoneyToRefund as 'RefundedMoneyUponCancellation',"
        "HR.Room_id,HB.TotalRooms as 'TotalRooms', R.RoomType,R.SingleBedCount,R.DoubleBedCount,B.id as 'BookingID',"
        "H.CompanyAdmin_id as 'AdminID', H.Address,H.Hotel_Location,H.Hotel_Country,'+'||CP.DaysCount||' day' "
        "as 'datestr', date('now') as 'Today',B.Status from database_hotel_booking HB join database_hotel_room HR "
        "on(HR.id=HB.Hotel_Room_id) join database_booking B on(HB.Booking_id=B.id) join database_room R on "
        "(R.id=HR.Room_id) join database_hotel H on(H.id=HR.Hotel_id) join database_cancellation_policy CP on "
        "(HR.Cancellation_Policy_id=CP.id) where HB.Checkin_Date>=CURRENT_DATE and B.User_id=%s"
        " and DATETIME(B.DateOfBooking,datestr)>=date('now') order by HB.Checkin_Date,"
        "HB.Checkout_Date,B.MoneyToPay", [request.user.id])
    data = namedtuplefetchall(cursor)
    # notifications count
    count = BookingLog.objects.filter(Actor=0, notified=0, Booking__User=request.user).count()
    return render(request, "login/userBookings.html", {'data': data, 'count': count})


def usernotifications(request):
    cursor = connection.cursor()
    cursor.execute(
        "select H.Hotel_Name,H.Hotel_Location,R.RoomType,HB.Checkin_Date,HB.Checkout_Date,HB.TotalRooms,B.PaidMoney,"
        "B.MoneyToPay,B.MoneyToRefund,BL.Message,BL.notified,B.Status from database_hotel_booking HB join "
        "database_hotel_room HR on(HR.id=HB.Hotel_Room_id) join database_booking B on(HB.Booking_id=B.id) "
        "join database_room R on (R.id=HR.Room_id) join database_hotel H on(H.id=HR.Hotel_id) join database_bookinglog"
        " BL on (B.id=BL.Booking_id) join auth_user U on(U.id=B.User_id) where BL.Actor=0 and  B.User_id=%s order by "
        "BL.notified,HB.Checkin_Date,HB.Checkout_Date,B.MoneyToPay", [request.user.id])
    data = namedtuplefetchall(cursor)
    BookingLog.objects.filter(Booking__User=request.user).update(notified=True)
    return render(request, "login/userNotifications.html", {'data': data})


def bookingcancel(request):
    bookingID = request.GET.get('bid', '1')
    bookingID = int(bookingID)
    cursor = connection.cursor()
    HotelBooking = Hotel_Booking.objects.get(Booking=Booking.objects.get(pk=bookingID))
    HotelRoom = Hotel_Room.objects.get(pk=HotelBooking.Hotel_Room_id)
    CancellationPolicy = Cancellation_Policy.objects.get(pk=HotelRoom.Cancellation_Policy_id)
    datestr = '+' + str(CancellationPolicy.DaysCount) + ' day'
    cursor.execute(
        "select distinct HB.Checkin_Date,HB.Checkout_Date,H.Hotel_Name,B.User_id,HR.Price*HB.TotalRooms as 'Price',"
        "(B.PaidMoney) as 'Paid',B.MoneyToPay as 'Pending',B.MoneyToRefund as 'RefundedMoneyUponCancellation', "
        "HR.Room_id,HB.TotalRooms as 'TotalRooms',R.RoomType,R.SingleBedCount,R.DoubleBedCount,B.id as 'BookingID',"
        "H.CompanyAdmin_id as 'AdminID',H.Address,H.Hotel_Location,H.Hotel_Country from database_hotel_booking HB "
        "join database_hotel_room HR on(HR.id=HB.Hotel_Room_id) join database_booking B on(HB.Booking_id=B.id) join "
        "database_room R on (R.id=HR.Room_id) join database_hotel H on(H.id=HR.Hotel_id) where "
        "HB.Checkin_Date>=CURRENT_DATE and B.id=%s and DATETIME(B.DateOfBooking,%s)>=date('now')"
        " order by HB.Checkin_Date,HB.Checkout_Date,B.MoneyToPay", [bookingID, datestr])
    data = namedtuplefetchall(cursor)
    return render(request, "login/bookingCancelConfirm.html", {'data': data[0]})


def bookingcancelredirect(request):
    bookingID = request.GET.get('bid', '1')
    adminID = request.GET.get('aid', '3')
    # update status of booking
    bookingObject = Booking.objects.get(pk=int(bookingID))
    bookingObject.Status = 2
    bookingObject.save()
    # add notification for admin
    try:
        logObject = BookingLog.objects.get(Actor=1, Admin_id=adminID, Booking_id=int(bookingID))
        # todo
        logObject.Message = ''
        logObject.notified = 0
        logObject.save()
    except BookingLog.DoesNotExist:
        logObject = BookingLog(Actor=1, Message='', notified=0, Admin_id=adminID, Booking_id=int(bookingID))
        logObject.save()
    hotelObject = Hotel.objects.get(CompanyAdmin=adminID)
    hotelObject.TotalSentMoney -= bookingObject.MoneyToRefund
    hotelObject.save()
    return HttpResponseRedirect('userbookings')


def userflightbookings(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT DISTINCT B.id as 'bookingid',B.User_id,FR.Price*FB.TotalSeats as 'Price', FB.TotalSeats as 'TotalSeats'"
        ",A.AirCompany_Name as 'AirCompany_Name',F.Airplane_Number as 'Plane', F.Aircraft as 'Model', FR.Time as 'Time'"
        ",FR.Date as 'DOF', B.DateOfBooking as 'DOB',(B.PaidMoney) as 'Paid',B.MoneyToPay as 'Pending',B.MoneyToRefund "
        "as 'RefundedMoneyUponCancellation','+'||CP.DaysCount||' day' as 'datestr', FR.Source_Airport ||','||R.Source "
        "as 'SRC' , FR.Destination_Airport||','||R.Destination as 'DEST', FR.Duration as 'Duration' FROM "
        "database_flight_booking FB JOIN database_booking B ON (FB.Booking_id=B.id) JOIN database_flight_route FR ON "
        "(FB.Flight_id = FR.id) JOIN database_flight F ON (FR.Flight_id = F.id) JOIN database_air_company A ON "
        "(F.AirCompany_id = A.id) JOIN database_cancellation_policy CP ON (CP.id = FR.Cancellation_Policy_id) JOIN "
        "database_route R ON (R.id = FR.Route_id) WHERE B.User_id = %s and B.isCancelled=0 and "
        "DATETIME(B.DateOfBooking,datestr)>=date('now') order by B.DateOfBooking,FR.Date", [request.user.id])
    data = namedtuplefetchall(cursor)
    return render(request, "login/userBookings.html", {'data': data})


def flightbookingcancel(request):
    bookingID = request.GET.get('bid', '1')
    bookingID = int(bookingID)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT DISTINCT A.CompanyAdmin_id as 'AdminID',B.id as 'bookingid',B.User_id,FR.Price*FB.TotalSeats as 'Price'"
        ", FB.TotalSeats as 'TotalSeats', A.AirCompany_Name as 'AirCompany_Name',F.Airplane_Number as 'Plane', "
        "F.Aircraft as 'Model', FR.Time as 'Time', FR.Date as 'DOF', B.DateOfBooking as 'DOB',(B.PaidMoney) as "
        "'Paid',B.MoneyToPay as 'Pending',B.MoneyToRefund as 'RefundedMoneyUponCancellation', '+'||CP.DaysCount||' day'"
        " as 'datestr', FR.Source_Airport ||','||R.Source as 'SRC' , FR.Destination_Airport||','||R.Destination as "
        "'DEST', FR.Duration as 'Duration' FROM database_flight_booking FB JOIN database_booking B ON "
        "(FB.Booking_id=B.id) JOIN database_flight_route FR ON (FB.Flight_id = FR.id) JOIN database_flight F ON "
        "(FR.Flight_id = F.id) JOIN database_air_company A ON (F.AirCompany_id = A.id) JOIN "
        "database_cancellation_policy CP ON (CP.id = FR.Cancellation_Policy_id) JOIN database_route R ON "
        "(R.id = FR.Route_id) WHERE B.User_id = %s and B.id = %s and B.isCancelled=0 and "
        "DATETIME(B.DateOfBooking,datestr)>=date('now') order by B.DateOfBooking,FR.Date", [request.user.id, bookingID])
    data = namedtuplefetchall(cursor)
    return render(request, "login/flightBookingCancelConfirm.html", {'datum': data[0]})


def flightbookingcancelredirect(request):
    bookingid = request.GET.get('bid', '1')
    adminid = request.GET.get('aid', '3')
    bookingobject = Booking.objects.get(pk=int(bookingid))
    bookingobject.isCancelled = True
    bookingobject.save()
    cancelobject = Cancellation_Log(Admin=User.objects.get(id=adminid), Booking=Booking.objects.get(id=bookingid),
                                    notified=False)
    cancelobject.save()
    cursor = connection.cursor()
    cursor.execute("SELECT MoneyToRefund FROM database_booking where id=%s", [bookingid])
    results = cursor.fetchone()
    MoneyToDeduct = results[0]
    cursor.execute("UPDATE database_air_company "
                   "SET TotalSentMoney = TotalSentMoney - %s "
                   "WHERE CompanyAdmin_id=%s", [MoneyToDeduct, adminid])
    return HttpResponseRedirect('userflightbookings')
