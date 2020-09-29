from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import SearchHotelForm, SearchFlightForm
from django.db import connection
from collections import namedtuple
from datetime import datetime
import os
from django.utils.encoding import smart_str
from geopy import geocoders
from geopy.exc import GeocoderServiceError

EASY_MAPS_GOOGLE_KEY = "AIzaSyATg_isuGSCHIlJamrxAXfkFDTYhIz7ytM"


class Error(Exception):
    pass


def google_v3(address):
    try:
        g = geocoders.GoogleV3(EASY_MAPS_GOOGLE_KEY)
        results = g.geocode(smart_str(address), exactly_one=False)
        if results is not None:
            return results[0]
        else:
            return "notfound"
    except (UnboundLocalError, ValueError, GeocoderServiceError) as e:
        return "notfound"


def daysBetween(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def homepage(request):
    hotelForm = SearchHotelForm()
    flightForm = SearchFlightForm()
    return render(request, "search/homepage.html", {'hotelForm': hotelForm, 'flightForm': flightForm})


def searchHotelPage(request):
    hotelForm = SearchHotelForm()
    flightFrom = SearchFlightForm()
    dest = request.GET.get('hoteldest', '')
    checkin = request.GET.get('checkin', '')
    checkout = request.GET.get('checkout', '')
    roomCount = request.GET.get('room', '')
    adultCount = request.GET.get('adult', '')
    dest = '%' + dest + '%'
    latitudeR = 0
    longitudeR = 0
    rr = google_v3(dest)
    if rr != "notfound":
        r = rr[1]
        latitudeR = r[0] * 0.0174533
        longitudeR = r[1] * 0.0174533
    cursor = connection.cursor()
    cursor.execute("SELECT H.Hotel_Name,H.Address,H.Hotel_Location,H.Hotel_Country,H.Description,HR.FreeRoomCount"
                   " as 'Num', min(HR.Price)*%s as 'Price', H.CompanyAdmin_id as ID , H.id as HID  FROM "
                   "database_hotel_room HR  join database_hotel H on(HR.Hotel_id=H.id) where (lower(H.Hotel_Name) "
                   "Like %s OR lower(H.Hotel_Location) Like %s OR lower(H.Hotel_Country) Like %s OR "
                   "lower(H.Address) Like %s OR (acos(sin(%s) * sin(radians(H.Latitude)) + "
                   "cos(%s) * cos(radians(H.Latitude)) * cos(radians(H.Longitude) - (%s))) * 6371 <= 5)) "
                   "and Num >= %s GROUP BY H.Hotel_Name",
                   [int(roomCount), dest, dest, dest, dest, latitudeR, latitudeR, longitudeR, int(roomCount)])
    hotels = namedtuplefetchall(cursor)
    # setting initial values for room and adult
    hotelForm.fields['room'].initial = int(roomCount)
    hotelForm.fields['adult'].initial = int(adultCount)
    return render(request, "search/searchHotel.html",
                  {'hotelForm': hotelForm, 'flightForm': flightFrom, 'hotels': hotels})


# @login_required(login_url='/login/')
def hotelrooms(request):
    hotelForm = SearchHotelForm()
    flightForm = SearchFlightForm()
    checkIn = request.GET.get('checkin', '')
    checkOut = request.GET.get('checkout', '')
    roomCount = request.GET.get('room', '')
    adultCount = request.GET.get('adult', '')
    hotelID = request.GET.get('hid', '')
    dateCount = daysBetween(checkIn, checkOut)
    cursor = connection.cursor()
    cursor.execute("select H.Hotel_Name,H.Address,H.Hotel_Location,H.Hotel_Country,H.Description,H.CompanyAdmin_id "
                   "as 'uid',H.id as 'hid' from database_hotel H WHERE H.id=%s",
                   [int(hotelID)])
    hotel = namedtuplefetchall(cursor)
    hotelRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    userf = 'user_' + str(hotel[0].uid)
    hotelRoot = os.path.join(hotelRoot, 'HotelFlight/static/media/' + userf + '/main')
    imageList = os.listdir(hotelRoot)
    cursor.execute("select R.SingleBedCount,R.DoubleBedCount,R.RoomType,R.AirConditioner,HR.Price*%s as 'Price',"
                   "HR.Complimentary_Breakfast,HR.wifi,HR.FreeRoomCount as 'cnt',HR.Hotel_id as 'hotelID',"
                   " HR.Room_id as 'roomID',hr.ID as 'hrID' from database_room R join database_hotel_room HR "
                   "on (R.id=HR.Room_id) where HR.Hotel_id=%s and cnt>=%s group by HR.Hotel_id,R.id ",
                   [int(roomCount), int(hotelID), int(roomCount)])
    rooms = namedtuplefetchall(cursor)
    # setting initial values for room and adult
    hotelForm.fields['room'].initial = int(roomCount)
    hotelForm.fields['adult'].initial = int(adultCount)
    return render(request, "search/hotelRooms.html",
                  {'hotelForm': hotelForm, 'flightForm': flightForm, 'hotel': hotel[0], 'rooms': rooms,
                   'imageList': imageList, 'daysCount': dateCount})


def searchFlightPage(request):
    hotelform = SearchHotelForm()
    flightform = SearchFlightForm()
    source = request.GET.get('source', '')
    dest = request.GET.get('dest', '')
    depart = request.GET.get('depart', '')
    adultcount = request.GET.get('adult', '')
    childrenCount = request.GET.get('children', '')
    cursor = connection.cursor()
    print("searching for: ")
    print("Source " + source + "Dest: " + dest + "Departure: " + depart)
    dest = '%' + dest + '%'
    source = '%' + source + '%'
    # single stop
    # single stop
    cursor.execute("SELECT R.Source, R.Destination, FR.Source_Airport, FR.Destination_Airport, FR.Date, FR.Time, "
                   "FR.Duration, FR.Price, A.AirCompany_Name, F.Aircraft, F.Airplane_Number,FR.id as 'FRID',FR.id as 'FIDS' FROM database_route R "
                   "JOIN database_flight_route FR ON R.id = FR.Route_id "
                   "JOIN database_flight F ON F.id = FR.Flight_id "
                   "JOIN database_air_company A ON F.AirCompany_id=A.id "
                   "WHERE (R.Source Like %s OR FR.Source_Airport Like %s ) AND (R.Destination Like %s OR FR.Destination_Airport Like %s) AND FR.Date=%s",
                   [source, source, dest, dest, depart])
    ssflights = namedtuplefetchall(cursor)
    # multi stop
    cursor.execute("SELECT T.Source as 'Src', T.Source_Airport as 'SrcAirport' , T.Destination as 'Intermediate', "
                   "T.Destination_Airport as 'InterAirport', S.Destination as 'Dest', S.Destination_Airport as 'DestAirport',"
                   " T.Date as 'Departure', T.AirCompany_Name as 'SrcCompany', T.Aircraft as 'SrcAircraft', "
                   "T.Airplane_Number as 'SrcAirNo', T.Time as 'SrcTime', T.Duration as 'SrcDuration', "
                   "S.AirCompany_Name as 'DestCompany', S.Aircraft as 'DestAircraft', S.Airplane_Number as 'DestAirNo',"
                   " S.Time as 'DestTime', S.Duration as 'DestDuration',"
                   " ((strftime('%%H',S.Time)*60+strftime('%%M',S.Time))- "
                   "strftime('%%H',T.Time)*60-strftime('%%M',T.Time)-T.Duration) as 'TimeDiff',"
                   "T.Price as 'firstPrice',S.Price 'secondPrice',T.TID as 'ID1',S.SID as 'ID2',T.TFID as 'FIDM1',S.SFID as 'FIDM2' "
                   "FROM (SELECT *,FR.id as 'TID',FR.Flight_id as 'TFID' FROM database_route R JOIN database_flight_route FR ON R.id = FR.Route_id "
                   "JOIN database_flight F ON F.id = FR.Flight_id JOIN database_air_company A "
                   "ON F.AirCompany_id=A.id WHERE (R.Source Like %s OR FR.Source_Airport Like %s) AND FR.Date=%s ) T "
                   "JOIN (SELECT *,FR.id as 'SID',FR.Flight_id as 'SFID' FROM database_route R JOIN database_flight_route FR ON R.id = FR.Route_id "
                   "JOIN database_flight F ON F.id = FR.Flight_id JOIN database_air_company A ON F.AirCompany_id=A.id"
                   " where R.Destination Like %s OR FR.Destination_Airport Like %s) S ON S.Source = T.Destination "
                   "WHERE (T.SOURCE Like %s OR T.Source_Airport LIKE %s) AND (S.Destination Like %s OR S.Destination_Airport LIKE %s) AND T.Date=S.Date AND "
                   "(strftime('%%H', T.Time)*60 + strftime('%%M', T.Time) + 30 + T.Duration) < "
                   "(strftime('%%H', S.Time)*60 + strftime('%%M', S.Time))",
                   [source, source, depart, dest, dest, source, source, dest, dest])
    msflights = namedtuplefetchall(cursor)
    flightform.fields['children'].initial = int(childrenCount)
    flightform.fields['adult'].initial = int(adultcount)

    return render(request, "search/flighttest.html",
                  {'hotelform': hotelform, 'flightform': flightform, 'ssflights': ssflights, 'msflights': msflights})