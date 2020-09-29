from search.forms import SearchHotelForm, SearchFlightForm
# mail
from django.shortcuts import render
from .forms import HotelBookingForm, FlightBookingForm
from django.db import connection
from collections import namedtuple
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


# Create your views here.
def hotelbookingpage(request):
    dest = request.GET.get('hoteldest', '')
    checkin = request.GET.get('checkin', '')
    checkout = request.GET.get('checkout', '')
    roomcount = request.GET.get('room', '')
    adultcount = request.GET.get('adult', '')
    hid = request.GET.get('hid', '')
    huid = request.GET.get('huid', '')
    hrid = request.GET.get('hrid', '')
    hrid = int(hrid)
    roomcount = int(roomcount)
    cursor = connection.cursor()
    cursor.execute("SELECT R.RoomType, R.SingleBedCount, R.DoubleBedCount,HR.Room_id as 'roomID',"
                   "HR.Price*%s as 'Price',R.AirConditioner,HR.Complimentary_Breakfast,HR.wifi FROM "
                   "database_hotel_room HR JOIN database_room R ON HR.Room_id=R.id "
                   "WHERE HR.id=%s",
                   [roomcount, hrid])
    room = namedtuplefetchall(cursor)
    cursor.execute("SELECT H.Hotel_Name, H.Hotel_Location, H.Hotel_Country,H.Address,H.CompanyAdmin_id as 'uid' FROM "
                   "database_hotel_room HR JOIN database_hotel H ON HR.Hotel_id=H.id WHERE HR.id=%s",
                   [hrid])
    hotel = namedtuplefetchall(cursor)
    form = HotelBookingForm()
    hotelform = SearchHotelForm()
    flightform = SearchFlightForm()
    return render(request, "booking/hotelbooking.html",
                  {'room': room[0], 'hotel': hotel[0], 'form': form, 'hotelform': hotelform, 'flightform': flightform})


# Create your views here.
def hotelbookingpaymet(request):
    roomcount = request.GET.get('room', '')
    hrid = request.GET.get('hrid', '')
    hrid = int(hrid)
    roomcount = int(roomcount)
    cursor = connection.cursor()
    cursor.execute("SELECT R.RoomType, R.SingleBedCount, R.DoubleBedCount,HR.Room_id as 'roomID',"
                   "HR.Price*%s as 'Price',R.AirConditioner,HR.Complimentary_Breakfast,HR.wifi FROM "
                   "database_hotel_room HR JOIN database_room R ON HR.Room_id=R.id "
                   "WHERE HR.id=%s",
                   [roomcount, hrid])
    room = namedtuplefetchall(cursor)
    cursor.execute("SELECT H.Hotel_Name, H.Hotel_Location, H.Hotel_Country,H.Address,H.CompanyAdmin_id as 'uid' FROM "
                   "database_hotel_room HR JOIN database_hotel H ON HR.Hotel_id=H.id WHERE HR.id=%s",
                   [hrid])
    hotel = namedtuplefetchall(cursor)
    form = HotelBookingForm()
    hotelform = SearchHotelForm()
    flightform = SearchFlightForm()
    return render(request, "booking/bookingpayment.html",
                  {'room': room[0], 'hotel': hotel[0], 'form': form, 'hotelform': hotelform, 'flightform': flightform})


def BookingConfirmationPage(request):
    # mine
    roomcount = request.GET.get('room', '')
    hrid = request.GET.get('hrid', '')
    hrid = int(hrid)
    roomcount = int(roomcount)
    print('HRID')
    print(hrid)
    print('Room ID')
    print(roomcount)
    cursor = connection.cursor()
    cursor.execute("SELECT R.RoomType, R.SingleBedCount, R.DoubleBedCount,HR.Room_id as 'roomID',"
                   "HR.Price*%s as 'Price',R.AirConditioner,HR.Complimentary_Breakfast,HR.wifi FROM "
                   "database_hotel_room HR JOIN database_room R ON HR.Room_id=R.id "
                   "WHERE HR.id=%s",
                   [roomcount, hrid])
    room = namedtuplefetchall(cursor)
    print(room[0])
    cursor.execute("SELECT H.Hotel_Name, H.Hotel_Location, H.Hotel_Country,H.Address,H.CompanyAdmin_id as 'uid' FROM "
                   "database_hotel_room HR JOIN database_hotel H ON HR.Hotel_id=H.id WHERE HR.id=%s",
                   [hrid])
    hotel = namedtuplefetchall(cursor)
    form = HotelBookingForm()
    hotelform = SearchHotelForm()
    flightform = SearchFlightForm()
    # mine

    FirstName = request.GET.get('first_name', '')
    LastName = request.GET.get('last_name', '')
    Email = request.GET.get('email', '')
    Phone = request.GET.get('phone', '')
    dest = request.GET.get('hoteldest', '')
    checkin = request.GET.get('checkin', '')
    checkout = request.GET.get('checkout', '')
    roomcount = request.GET.get('room', '')
    adultcount = request.GET.get('adult', '')
    hid = request.GET.get('hid', '')
    huid = request.GET.get('huid', '')
    hrid = request.GET.get('hrid', '')
    uid = request.GET.get('uid', '')

    hrid = int(hrid)
    uid = int(uid)
    cursor = connection.cursor()

    cursor.execute("SELECT MAX(id) from database_booking")
    results = cursor.fetchone()
    id = 1
    if results[0] is None:
        id = 1
    else:
        id = results[0] + 1
    cursor.execute("SELECT Price FROM database_hotel_room where id=%s", [hrid])
    results = cursor.fetchone()
    Price = results[0]
    cursor.execute("SELECT Percentage FROM database_hotel where id=%s", [hid])
    results = cursor.fetchone()
    rooms = int(roomcount)
    date_format = "%Y-%m-%d"
    a = datetime.strptime(checkout, date_format)
    b = datetime.strptime(checkin, date_format)
    delta = a - b
    Percentage = results[0] / 100
    TotalAmount = Price * rooms * delta.days
    PaidMoney = Percentage * Price * rooms * delta.days
    MoneyToPay = Price * (1 - Percentage) * rooms * delta.days
    # ei percentage should come from cancellation policy\
    cursor.execute(
        "SELECT Percentage_refunding FROM database_cancellation_policy WHERE id =(SELECT Cancellation_Policy_id FROM database_hotel_room where id=%s)",
        [hrid])
    results = cursor.fetchone()
    Percentage_refunding = results[0] / 100
    MoneyToRefund = PaidMoney * Percentage_refunding
    cursor.execute(
        "INSERT INTO database_booking (id, MoneyToPay, MoneyToRefund, DateOfBooking, DateOfCancellation, User_id,PaidMoney,isCancelled,Status) "
        "VALUES (%s, %s, %s, CURRENT_DATE, CURRENT_DATE, %s, %s,0,0)", [id, MoneyToPay, MoneyToRefund, uid, PaidMoney])
    cursor.execute("SELECT MAX(id) from database_hotel_booking")
    results = cursor.fetchone()
    new_id = 1
    if results[0] is None:
        new_id = 1
    else:
        new_id = results[0] + 1
    cursor.execute(
        "INSERT INTO database_hotel_booking (id, Booking_id, Hotel_Room_id, Checkin_Date, Checkout_Date,TotalRooms,isApproved) "
        "VALUES (%s,%s,%s,%s,%s,%s,0)", [new_id, id, hrid, checkin, checkout, roomcount])
    cursor.execute("UPDATE database_hotel_room "
                   "SET FreeRoomCount = FreeRoomCount - %s "
                   "WHERE id=%s", [roomcount, hrid])

    # generate confirmation mail
    # create message object instance
    print(FirstName)
    print(LastName)

    p = canvas.Canvas('./booking/pdfs/ex.pdf')
    p.drawString(250, 700, "Itinerary")
    Fname = "First Name: " + FirstName
    Lname = "Last Name: " + LastName
    Contact = "Contact No.: " + Phone
    HotelName = "Hotel Name: " + hotel[0].Hotel_Name
    InDate = "Check In: " + checkin
    OutDate = "Check Out: " + checkout
    TotalNights = "Total Night(s): " + str(delta.days)
    RoomType = "Room Type: " + room[0].RoomType
    RoomPrice = "Price per Room: " + str(Price)
    TotalRoom = "Total Room(s): " + str(rooms)
    TotalPrice = "Total Amount: " + str(Price) + "x" + str(delta.days) + "x" + str(rooms) + "= " + str(TotalAmount)
    BookAmount = "Booking Amount: " + str(PaidMoney)
    RestAmount = "More to Pay: " + str(MoneyToPay)

    p.drawString(100, 620, "Personal Information")
    p.drawString(100, 600, Fname)
    p.drawString(100, 580, Lname)
    p.drawString(100, 560, Contact)

    p.drawString(100, 510, "Booking Information")
    p.drawString(100, 480, HotelName)
    p.drawString(100, 460, InDate)
    p.drawString(100, 440, OutDate)
    p.drawString(100, 420, TotalNights)
    p.drawString(100, 400, RoomType)
    p.drawString(100, 380, RoomPrice)
    p.drawString(100, 360, TotalRoom)
    p.drawString(100, 340, TotalPrice)
    p.drawString(100, 320, BookAmount)
    p.drawString(100, 300, RestAmount)

    p.drawString(100, 280, "This booking has been confirmed.")

    p.drawImage('./HotelFlight/static/booking/barcode.jpg', 400, 750, 6 * cm, 2 * cm)
    p.drawImage('./HotelFlight/static/booking/logo.jpg', 100, 750, 2 * cm, 2 * cm)
    p.showPage()
    p.save()

    # create message object instance
    '''msg = MIMEMultipart()

    message = "Your booking has been confirmed! Thanks for staying with us!!"

    # setup the parameters of the message
    password = "proxierOSP"
    msg['From'] = "onlineserviceprovider131625@gmail.com"
    msg['To'] = Email
    msg['Subject'] = "Response to Hotel/Flight Booking"

    # add in the message body
    msg.attach(MIMEText(message, 'plain'))

    filename = "ex.pdf"
    attachment = open("./booking/pdfs/ex.pdf", "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    # create server
    server = smtplib.SMTP('smtp.gmail.com: 587')

    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    server.quit()
    
    print("email sent")'''


    return render(request, "booking/bookingconfirmation.html",
                  {'room': room[0], 'hotel': hotel[0], 'form': form, 'hotelform': hotelform, 'flightform': flightform})


def FlightBookingPage(request):
    print("flight booking page")
    Source = request.GET.get('source', '')
    Dest = request.GET.get('dest', '')
    Departure_Date = request.GET.get('depart', '')
    frid = request.GET.get('FRID', '')
    id1 = request.GET.get('ID1', '')
    id2 = request.GET.get('ID2', '')
    adultCount = request.GET.get('adult', '')
    fids = request.GET.get('FIDS', '')
    fidm1 = request.GET.get('FIDM1', '')
    fidm2 = request.GET.get('FIDM2', '')
    print("Source: " + Source)
    print("Destination: " + Dest)
    print("Departure date: " + Departure_Date)
    print("Multiple hop flight route 1: " + id1)
    print("Multiple hop flight route 2: " + id2)
    print("Single hop 1: " + frid)
    print("Adult count: " + adultCount)
    print(adultCount)
    print("FIDS ->")
    print(fids)
    print("FIDM1 ->")
    print(fidm1)
    print("FIDM2 ->")
    print(fidm2)

    if id1 == "" and id2 == "":
        cursor = connection.cursor()

        cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                       "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                       "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                       "WHERE FR.id = %s", [frid])
        aircompany = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
            "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
            "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
            [adultCount, frid])

        flight = namedtuplefetchall(cursor)
        form = FlightBookingForm()
        hotelform = SearchHotelForm()
        flightform = SearchFlightForm()
        return render(request, "booking/flightbooking.html",
                      {'flight': flight[0], 'aircompany': aircompany[0], 'form': form, 'hotelform': hotelform,
                       'flightform': flightform, 'multi': 'False'})
    else:
        cursor = connection.cursor()

        cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                       "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                       "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                       "WHERE FR.id = %s", [id1])
        aircompany = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
            "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
            "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
            [adultCount, id1])

        flight = namedtuplefetchall(cursor)

        cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                       "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                       "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                       "WHERE FR.id = %s", [id2])
        aircompany2 = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
            "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
            "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
            [adultCount, id2])

        flight2 = namedtuplefetchall(cursor)
        form = FlightBookingForm()
        hotelform = SearchHotelForm()
        flightform = SearchFlightForm()
        return render(request, "booking/flightbooking.html",
                      {'flight': flight[0], 'aircompany': aircompany[0], 'flight2': flight2[0],
                       'aircompany2': aircompany2[0], 'form': form, 'hotelform': hotelform,
                       'flightform': flightform, 'multi': 'True'})


def flightbookingpayment(request):
    print("flight booking page")
    Source = request.GET.get('source', '')
    Dest = request.GET.get('dest', '')
    Departure_Date = request.GET.get('depart', '')
    frid = request.GET.get('FRID', '')
    id1 = request.GET.get('ID1', '')
    id2 = request.GET.get('ID2', '')
    adultCount = request.GET.get('adult', '')
    fids = request.GET.get('FIDS', '')
    fidm1 = request.GET.get('FIDM1', '')
    fidm2 = request.GET.get('FIDM2', '')
    print("Source: " + Source)
    print("Destination: " + Dest)
    print("Departure date: " + Departure_Date)
    print("Multiple hop flight route 1: " + id1)
    print("Multiple hop flight route 2: " + id2)
    print("Single hop 1: " + frid)
    print("Adult count: " + adultCount)
    print(adultCount)
    print("FIDS ->")
    print(fids)
    print("FIDM1 ->")
    print(fidm1)
    print("FIDM2 ->")
    print(fidm2)

    if id1 == "" and id2 == "":
        cursor = connection.cursor()

        cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                       "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                       "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                       "WHERE FR.id = %s", [frid])
        aircompany = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
            "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
            "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
            [adultCount, frid])

        flight = namedtuplefetchall(cursor)
        form = FlightBookingForm()
        hotelform = SearchHotelForm()
        flightform = SearchFlightForm()
        return render(request, "booking/flightbookingpayment.html",
                      {'flight': flight[0], 'aircompany': aircompany[0], 'form': form, 'hotelform': hotelform,
                       'flightform': flightform, 'multi': 'False'})
    else:
        cursor = connection.cursor()

        cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                       "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                       "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                       "WHERE FR.id = %s", [id1])
        aircompany = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
            "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
            "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
            [adultCount, id1])

        flight = namedtuplefetchall(cursor)

        cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                       "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                       "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                       "WHERE FR.id = %s", [id2])
        aircompany2 = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
            "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
            "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
            [adultCount, id2])

        flight2 = namedtuplefetchall(cursor)
        form = FlightBookingForm()
        hotelform = SearchHotelForm()
        flightform = SearchFlightForm()
        return render(request, "booking/flightbookingpayment.html",
                      {'flight': flight[0], 'aircompany': aircompany[0], 'flight2': flight2[0],
                       'aircompany2': aircompany2[0], 'form': form, 'hotelform': hotelform,
                       'flightform': flightform, 'multi': 'True'})


def FlightBookingConfirmationPage(request):
    FirstName = request.GET.get('first_name', '')
    LastName = request.GET.get('last_name', '')
    Email = request.GET.get('email', '')
    Phone = request.GET.get('phone', '')
    Passport = request.GET.get('passport', '')
    print(FirstName)
    print(LastName)
    print(Email)
    print(Phone)
    print("confirmation page")
    Source = request.GET.get('source', '')
    Dest = request.GET.get('dest', '')
    Departure_Date = request.GET.get('depart', '')
    frid = request.GET.get('FRID', '')
    id1 = request.GET.get('ID1', '')
    id2 = request.GET.get('ID2', '')
    uid = request.GET.get('uid', '')
    adultCount = request.GET.get('adult', '')
    fids = request.GET.get('FIDS', '')
    fidm1 = request.GET.get('FIDM1', '')
    fidm2 = request.GET.get('FIDM2', '')
    print(Source)
    print(Dest)
    print(Departure_Date)
    print(id1)
    print(id2)
    print(frid)
    print(uid)
    print(adultCount)
    print("FIDS ->")
    print(fids)
    print("FIDM1 ->")
    print(fidm1)
    print("FIDM2 ->")
    print(fidm2)
    form = FlightBookingForm()
    hotelform = SearchHotelForm()
    flightform = SearchFlightForm()
    if frid == "":
        print("Single hop  empty")
    else:
        print("Single hop not empty")
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(id) from database_booking")
        results = cursor.fetchone()
        print(results)
        id = 1
        if results[0] is None:
            id = 1
        else:
            id = results[0] + 1
        cursor.execute("SELECT Price FROM database_flight_route where id=%s", [frid])
        results = cursor.fetchone()
        print("price is ")
        print(results[0])
        Price = results[0]
        cursor.execute("SELECT A.Percentage from database_air_company A JOIN database_flight F "
                       "ON (A.id = F.AirCompany_id) JOIN database_flight_route FR "
                       "ON (FR.Flight_id = F.id) where FR.id=%s", [frid])
        results = cursor.fetchone()
        Percentage = results[0] / 100
        PaidMoney = Percentage * Price * float(adultCount)
        MoneyToPay = Price * float(adultCount) * (1 - Percentage)
        cursor.execute(
            "SELECT Percentage_refunding FROM database_cancellation_policy WHERE id =(SELECT Cancellation_Policy_id FROM database_flight_route where id=%s)",
            [frid])
        results = cursor.fetchone()
        Percentage_refunding = results[0] / 100

        MoneyToRefund = PaidMoney * Percentage_refunding
        MoneyToRefund = PaidMoney * .8
        cursor.execute(
            "INSERT INTO database_booking (id, MoneyToPay, MoneyToRefund, DateOfBooking, DateOfCancellation, User_id,PaidMoney,isCancelled,Status) "
            "VALUES (%s, %s, %s, CURRENT_DATE, CURRENT_DATE,  %s,%s,0,0)",
            [id, MoneyToPay, MoneyToRefund, uid, PaidMoney])
        cursor.execute("SELECT MAX(id) from database_flight_booking")
        results = cursor.fetchone()
        print(results)
        new_id = 1
        if results[0] is None:
            new_id = 1
        else:
            new_id = results[0] + 1
        cursor.execute("INSERT INTO database_flight_booking (id, Booking_id, Flight_id,TotalSeats,isApproved) "
                       "VALUES (%s,%s,%s,%s,0)", [new_id, id, frid, adultCount])
        cursor.execute("UPDATE database_flight_route "
                       "SET TotalSeatsBooked = TotalSeatsBooked + %s "
                       "WHERE id=%s", [adultCount, frid])
        cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                       "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                       "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                       "WHERE FR.id = %s", [frid])
        aircompany = namedtuplefetchall(cursor)

        cursor.execute(
            "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
            "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
            "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
            [adultCount, frid])

        flight = namedtuplefetchall(cursor)

        return render(request, "booking/flightbookingconfirmation.html",
                      {'flight': flight[0], 'aircompany': aircompany[0], 'form': form, 'hotelform': hotelform,
                       'flightform': flightform, 'multi': 'False'})

    if id1 == "" and id2 == "":
        print("Multi hop empty")
    else:
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(id) from database_booking")
        results = cursor.fetchone()
        print(results)
        id = 1
        if results[0] is None:
            id = 1
        else:
            id = results[0] + 1
            Price = 0
            cursor.execute("SELECT Price FROM database_flight_route where id=%s", [id1])
            results = cursor.fetchone()
            print("price is ")
            print(results[0])
            Price1 = results[0]
            cursor.execute("SELECT Price FROM database_flight_route where id=%s", [id2])

            results = cursor.fetchone()
            print("price is ")
            print(results[0])
            Price2 = results[0]
            cursor.execute("SELECT A.Percentage from database_air_company A JOIN database_flight F "
                           "ON (A.id = F.AirCompany_id) JOIN database_flight_route FR "
                           "ON (FR.Flight_id = F.id) where FR.id=%s", [id1])
            results = cursor.fetchone()
            Percentage = results[0] / 100
            PaidMoney = Percentage * Price1 * float(adultCount)
            MoneyToPay = Price1 * float(adultCount) * (1 - Percentage)
            cursor.execute(
                "SELECT Percentage_refunding FROM database_cancellation_policy WHERE id =(SELECT Cancellation_Policy_id FROM database_flight_route where id=%s)",
                [id1])
            results = cursor.fetchone()
            Percentage_refunding = results[0] / 100

            MoneyToRefund = PaidMoney * Percentage_refunding

            cursor.execute(
                "INSERT INTO database_booking (id, MoneyToPay, MoneyToRefund, DateOfBooking, DateOfCancellation,  User_id, PaidMoney,isCancelled,Status) "
                "VALUES (%s, %s, %s, CURRENT_DATE, CURRENT_DATE,  %s,%s,0,0)",
                [id, MoneyToPay, MoneyToRefund, uid, PaidMoney])

            cursor.execute("SELECT A.Percentage from database_air_company A JOIN database_flight F "
                           "ON (A.id = F.AirCompany_id) JOIN database_flight_route FR "
                           "ON (FR.Flight_id = F.id) where FR.id=%s", [id2])
            results = cursor.fetchone()
            Percentage = results[0] / 100
            PaidMoney = Percentage * Price2 * float(adultCount)
            MoneyToPay = Price2 * float(adultCount) * (1 - Percentage)
            cursor.execute(
                "SELECT Percentage_refunding FROM database_cancellation_policy WHERE id =(SELECT Cancellation_Policy_id FROM database_flight_route where id=%s)",
                [id2])
            results = cursor.fetchone()
            Percentage_refunding = results[0] / 100

            MoneyToRefund = PaidMoney * Percentage_refunding
            cursor.execute(
                "INSERT INTO database_booking (id, MoneyToPay, MoneyToRefund, DateOfBooking, DateOfCancellation, User_id,PaidMoney,isCancelled) "
                "VALUES (%s, %s, %s, CURRENT_DATE, CURRENT_DATE, %s, %s,0)",
                [id + 1, MoneyToPay, MoneyToRefund, uid, PaidMoney])

            cursor.execute("SELECT MAX(id) from database_flight_booking")
            results = cursor.fetchone()
            print(results)
            new_id = 1
            if results[0] is None:
                new_id = 1
            else:
                new_id = results[0] + 1
            cursor.execute("INSERT INTO database_flight_booking (id, Booking_id, Flight_id,TotalSeats,isApproved) "
                           "VALUES (%s,%s,%s,%s,0)", [new_id, id, id1, adultCount])
            new_id = new_id + 1
            cursor.execute("INSERT INTO database_flight_booking (id, Booking_id, Flight_id,TotalSeats,isApproved) "
                           "VALUES (%s,%s,%s,%s,0)", [new_id, id + 1, id2, adultCount])
            cursor.execute("UPDATE database_flight_route "
                           "SET TotalSeatsBooked = TotalSeatsBooked + %s "
                           "WHERE id=%s", [adultCount, id1])
            cursor.execute("UPDATE database_flight_route "
                           "SET TotalSeatsBooked = TotalSeatsBooked + %s "
                           "WHERE id=%s", [adultCount, id2])
            cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                           "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                           "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                           "WHERE FR.id = %s", [id1])
            aircompany = namedtuplefetchall(cursor)

            cursor.execute(
                "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
                "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
                "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
                [adultCount, id1])

            flight = namedtuplefetchall(cursor)

            cursor.execute("SELECT A.Aircompany_Name as 'Airlines' ,A.CompanyAdmin_id as 'uid' "
                           "FROM database_flight_route FR JOIN database_flight F ON (FR.Flight_id = F.id )  "
                           "JOIN database_air_company A ON (A.id = F.AirCompany_id) "
                           "WHERE FR.id = %s", [id2])
            aircompany2 = namedtuplefetchall(cursor)

            cursor.execute(
                "SELECT F.Airplane_Number as 'Plane' , FR.Source_Airport as 'Src_Airport', R.Source as 'Src' ,FR.Destination_Airport as 'Dest_Airport',R.Destination as 'Dest', "
                "FR.Time as 'Time', FR.Date as 'Date', FR.Price*%s as 'Price' , FR.Duration as 'Duration' "
                "FROM database_flight_route FR JOIN database_route R ON (FR.Route_id = R.id) JOIN database_flight F ON (FR.Flight_id = F.id) where FR.id = %s",
                [adultCount, id2])

            flight2 = namedtuplefetchall(cursor)

            print(FirstName)
            print(LastName)

            p = canvas.Canvas('./booking/pdfs/ex2.pdf')
            p.drawString(250, 700, "Itinerary")
            Fname = "First Name: " + FirstName
            Lname = "Last Name: " + LastName
            Contact = "Contact No.: " + Phone
            HotelName = "Hotel Name: " + hotel[0].Hotel_Name
            InDate = "Check In: " + checkin
            OutDate = "Check Out: " + checkout
            TotalNights = "Total Night(s): " + str(delta.days)
            RoomType = "Room Type: " + room[0].RoomType
            RoomPrice = "Price per Room: " + str(Price)
            TotalRoom = "Total Room(s): " + str(rooms)
            TotalPrice = "Total Amount: " + str(Price) + "x" + str(delta.days) + "x" + str(rooms) + "= " + str(
                TotalAmount)
            BookAmount = "Booking Amount: " + str(PaidMoney)
            RestAmount = "More to Pay: " + str(MoneyToPay)

            p.drawString(100, 620, "Personal Information")
            p.drawString(100, 600, Fname)
            p.drawString(100, 580, Lname)
            p.drawString(100, 560, Contact)

            p.drawString(100, 510, "Booking Information")
            p.drawString(100, 480, HotelName)
            p.drawString(100, 460, InDate)
            p.drawString(100, 440, OutDate)
            p.drawString(100, 420, TotalNights)
            p.drawString(100, 400, RoomType)
            p.drawString(100, 380, RoomPrice)
            p.drawString(100, 360, TotalRoom)
            p.drawString(100, 340, TotalPrice)
            p.drawString(100, 320, BookAmount)
            p.drawString(100, 300, RestAmount)

            p.drawString(100, 280, "This booking has been confirmed.")

            p.drawImage('./HotelFlight/static/booking/barcode.jpg', 400, 750, 6 * cm, 2 * cm)
            p.drawImage('./HotelFlight/static/booking/logo.jpg', 100, 750, 2 * cm, 2 * cm)
            p.showPage()
            p.save()

            return render(request, "booking/flightbookingconfirmation.html",
                          {'flight': flight[0], 'aircompany': aircompany[0], 'flight2': flight2[0],
                           'aircompany2': aircompany2[0], 'form': form, 'hotelform': hotelform,
                           'flightform': flightform, 'multi': 'True'})
