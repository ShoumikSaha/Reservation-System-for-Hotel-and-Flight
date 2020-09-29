from django.shortcuts import render

from django.contrib import messages
from database.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
import os
from django.http import HttpResponseRedirect

from collections import namedtuple
from django.db import connection


# Create your views here.
def admindash(request):
    return render(request, "siteadmin/AdminDash.html")


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def viewHotels(request):
    cursor = connection.cursor()
    cursor.execute(
        "select Hotel_Name,Hotel_Location,Hotel_Country,Address,Phone,TotalSentMoney,Percentage from database_hotel")
    data = namedtuplefetchall(cursor)
    return render(request, "siteadmin/AdminHotels.html", {'data': data})


def viewAirlines(request):
    cursor = connection.cursor()
    cursor.execute(
        "select AirCompany_Name,TotalSentMoney,Percentage from database_air_company")
    data = namedtuplefetchall(cursor)
    return render(request, "siteadmin/AdminAirlines.html", {'data': data})


def viewPaymentLog(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT H.Hotel_Name as Hotel_Name,R.RoomType as RoomType,HR.Price as UnitPrice,B.MoneyToPay as MoneyToPay,B.MoneyToRefund as MoneyToRefund,B.PaidMoney as PaidMoney,"
        "B.DateOfBooking as DOB,HB.Checkin_Date as CheckinDate,HB.Checkout_Date as CheckoutDate,HB.TotalRooms as TotalRooms FROM database_payment_log PL JOIN database_booking B ON (PL.booking_id = B.id) "
        "JOIN database_hotel_booking HB ON(HB.Booking_id = B.id) JOIN database_hotel_room HR ON (HB.Hotel_Room_id = HR.id) "
        "JOIN database_hotel H ON (H.id = HR.Hotel_id) JOIN database_room R ON (R.id = HR.Room_id) WHERE PL.Admin_id=%s",
        [request.user.id])
    data = namedtuplefetchall(cursor)
    return render(request, "siteadmin/AdminPaymentLog.html", {'data': data})


def viewAirlinesPaymentLog(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT DISTINCT B.User_id,FR.Price*FB.TotalSeats as 'Price', FB.TotalSeats as 'TotalSeats', A.AirCompany_Name as 'AirCompany_Name', "
        "F.Airplane_Number as 'Plane', F.Aircraft as 'Model', FR.Time as 'Time', FR.Date as 'DOF', B.DateOfBooking as 'DOB', "
        "(B.PaidMoney) as 'Paid',B.MoneyToPay as 'Pending',B.MoneyToRefund as 'RefundedMoneyUponCancellation', "
        "FR.Source_Airport||','||R.Source as 'SRC' , FR.Destination_Airport||','||R.Destination as 'DEST', FR.Duration as 'Duration' "
        "FROM database_booking B JOIN database_payment_log PL ON (PL.Booking_id=B.id) JOIN database_flight_booking FB ON (FB.Booking_id=B.id) "
        "JOIN database_flight_route FR ON (FB.Flight_id = FR.id) "
        "JOIN database_flight F ON (FR.Flight_id = F.id) "
        "JOIN database_air_company A ON (F.AirCompany_id = A.id) JOIN database_route R ON (R.id=FR.Route_id) WHERE PL.Admin_id=%s",
        [request.user.id])
    data = namedtuplefetchall(cursor)
    return render(request, "siteadmin/AdminAirlinesPaymentLog.html", {'data': data})


def approveHotelBookings(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT B.id as 'bookingID', H.Hotel_Name as Hotel_Name,R.RoomType as 'RoomType',HR.Price as 'Price',B.MoneyToPay as 'MoneyToPay',B.MoneyToRefund as MoneyToRefund,B.PaidMoney as PaidMoney,"
        "B.DateOfBooking as DOB,HB.Checkin_Date as CheckinDate,HB.Checkout_Date as CheckoutDate,HB.TotalRooms as TotalRooms FROM database_booking B "
        "JOIN database_hotel_booking HB ON(HB.Booking_id = B.id) JOIN database_hotel_room HR ON (HB.Hotel_Room_id = HR.id) "
        "JOIN database_hotel H ON (H.id = HR.Hotel_id) JOIN database_room R ON (R.id = HR.Room_id) where HB.isApproved=0")
    data = namedtuplefetchall(cursor)
    return render(request, "siteadmin/AdminApproveHotelBooking.html", {'data': data})


def approveFlightBookings(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT DISTINCT FB.id as 'fid',B.id as 'bookingID',FR.Price*FB.TotalSeats as 'Price', FB.TotalSeats as 'TotalSeats', A.AirCompany_Name as 'AirCompany_Name', "
        "F.Airplane_Number as 'Plane', F.Aircraft as 'Model', FR.Time as 'Time', FR.Date as 'DOF', B.DateOfBooking as 'DOB', "
        "(B.PaidMoney) as 'Paid',B.MoneyToPay as 'Pending',B.MoneyToRefund as 'RefundedMoneyUponCancellation', "
        "FR.Source_Airport||','||R.Source as 'SRC' , FR.Destination_Airport||','||R.Destination as 'DEST', FR.Duration as 'Duration' "
        "FROM database_flight_booking FB JOIN database_booking B ON (FB.Booking_id=B.id) "
        "JOIN database_flight_route FR ON (FB.Flight_id = FR.id) "
        "JOIN database_flight F ON (FR.Flight_id = F.id) "
        "JOIN database_air_company A ON (F.AirCompany_id = A.id) JOIN database_route R ON (R.id=FR.Route_id)")
    data = namedtuplefetchall(cursor)
    return render(request, "siteadmin/AdminApproveFlightBooking.html", {'data': data})


def approveHotelBookingRedirect(request):
    id = request.GET.get('bookingID', '')
    print("bookingid")
    print(id)
    hotelbookingobject = Hotel_Booking.objects.get(Booking=Booking.objects.get(pk=int(id)))

    hotelbookingobject.isApproved = True
    hotelbookingobject.save()
    hotelroom = Hotel_Room.objects.get(pk=hotelbookingobject.Hotel_Room_id)
    cursor = connection.cursor()
    cursor.execute("SELECT PaidMoney FROM database_booking where id=%s", [id])
    results = cursor.fetchone()
    MoneyToSend = results[0]
    print(MoneyToSend)
    cursor.execute("SELECT Hotel_id FROM database_hotel_room where id=%s", [hotelroom.id])
    results = cursor.fetchone()
    HotelToSend = results[0]
    print(HotelToSend)
    cursor.execute("UPDATE database_Hotel "
                   "SET TotalSentMoney = TotalSentMoney + %s "
                   "WHERE id=%s", [MoneyToSend, HotelToSend])
    payment = Payment_Log(Booking_id=id, Admin_id=request.user.id)
    payment.save()
    return HttpResponseRedirect('approveHotelBookings')


def approveFlightBookingRedirect(request):
    id = request.GET.get('bookingID', '')
    print("bookingid")
    print(id)
    fid = request.GET.get('fid', '')
    flightbookingobject = Flight_Booking.objects.get(pk=int(fid))
    print('flight booking id')
    print(fid)
    flightbookingobject.isApproved = True
    flightbookingobject.save()
    flightroute = Flight_Route.objects.get(pk=flightbookingobject.Flight_id)
    cursor = connection.cursor()
    cursor.execute("SELECT PaidMoney FROM database_booking where id=%s", [id])
    results = cursor.fetchone()
    MoneyToSend = results[0]
    print(MoneyToSend)
    cursor.execute("SELECT Flight_id FROM database_flight_route where id=%s", [flightroute.id])
    results = cursor.fetchone()
    Flight = results[0]
    print("flight ID")
    print(Flight)
    cursor.execute("SELECT AirCompany_id FROM database_flight where id=%s", [Flight])
    results = cursor.fetchone()
    AirCompany = results[0]
    print("Air company ID: ")
    print(AirCompany)
    cursor.execute("UPDATE database_air_company "
                   "SET TotalSentMoney = TotalSentMoney + %s "
                   "WHERE id=%s", [MoneyToSend, AirCompany])
    payment = Payment_Log(Booking_id=id, Admin_id=request.user.id)
    payment.save()
    print("Approved")
    return HttpResponseRedirect('approveFlightBookings')


def viewStats(request):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT count(B.id) as 'TotalBooking', sum(HR.Price)*.05 as 'TotalRevenue' , B.DateOfBooking as 'Date' "
        "FROM database_booking B JOIN database_hotel_booking HB ON B.id=HB.Booking_id "
        "JOIN database_hotel_room HR ON HB.Hotel_Room_id=HR.id "
        "GROUP BY B.DateOfBooking")
    results1 = cursor.fetchall()
    totalHotelBooking = []
    totalHotelRevenue = []
    dates = []
    for row in results1:
        print(row)
        totalHotelBooking.append(row[0])
        totalHotelRevenue.append(row[1])
        dates.append(row[2])
    data = namedtuplefetchall(cursor)
    print("Data1")
    print(data)
    print(results1)
    print(results1[0][2])

    cursor.execute(
        "SELECT count(B.id) as 'TotalBooking', sum(HR.Price)*.05 as 'TotalRevenue' , H.Hotel_Name as 'HotelName' "
        "FROM database_booking B JOIN database_hotel_booking HB ON B.id=HB.Booking_id "
        "JOIN database_hotel_room HR ON HB.Hotel_Room_id=HR.id "
        "JOIN database_hotel H ON HR.Hotel_id=H.id "
        "GROUP BY H.id ORDER BY sum(HR.Price) ")
    results2=cursor.fetchall();
    print(results2)

    '''y_pos = np.arange(len(totalHotelBooking))
    plt.bar(y_pos, totalHotelBooking, align='center', color="skyblue")
    plt.xticks(y_pos, dates)
    plt.xlabel('Date')
    plt.ylabel('Hotel Bookings')
    plt.title('Hotel Booking per day')
    plt.savefig('./HotelFlight/static/siteadmin/barPlotHotelBooking.png')

    y_pos = np.arange(len(totalHotelRevenue))
    plt.bar(y_pos, totalHotelRevenue, align='center', color="lightgreen")
    plt.xticks(y_pos, dates)
    plt.xlabel('Date')
    plt.ylabel('Revenue from Hotels')
    plt.title('Revenue from hotels per day')
    plt.savefig('./HotelFlight/static/siteadmin/barPlotHotelRevenue.png')
    #plt.show()'''

    cursor.execute(
        "SELECT count(B.id) as 'TotalBooking', sum(FR.Price)*.05 as 'TotalRevenue' , B.DateOfBooking as 'Date' "
        "FROM database_booking B JOIN database_flight_booking FB ON B.id=FB.Booking_id "
        "JOIN database_flight_route FR ON FB.Flight_id=FR.id "
        "GROUP BY B.DateOfBooking")
    results3 = cursor.fetchall()

    data = namedtuplefetchall(cursor)
    print("Data3")
    print(data)
    print(results3)
    # print(totalHotelBooking)

    cursor.execute(
        "SELECT count(B.id) as 'TotalBooking', sum(FR.Price)*.05 as 'TotalRevenue' , AC.AirCompany_Name as 'CompanyName' "
        "FROM database_booking B JOIN database_flight_booking FB ON B.id=FB.Booking_id "
        "JOIN database_flight_route FR ON FB.Flight_id=FR.id "
        "JOIN database_flight F ON FR.Flight_id=F.id "
        "JOIN database_air_company AC ON F.AirCompany_id=AC.id "
        "GROUP BY AC.id "
        "ORDER BY sum(FR.Price)")
    results4 = cursor.fetchall()

    data = namedtuplefetchall(cursor)
    print("Data3")
    print(data)
    print(results4)

    return render(request, "siteadmin/AdminStats.html", {'data1': results1, 'data2': results2, 'data3': results3, 'data4': results4})
