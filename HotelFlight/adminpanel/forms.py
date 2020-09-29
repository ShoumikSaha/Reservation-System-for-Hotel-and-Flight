from database.models import *
from .models import Photos
from django import forms
from django.forms import ClearableFileInput
from collections import namedtuple
from django.db import connection


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


CHOICES = (
    ('True', 'Yes'),
    ('False', 'No'),
)

ROOMTYPES = (
    ('1', 'Deluxe  SingleBed:0  DoubleBed:1 AC'),
    ('2', 'Casual  SingleBed:2  DoubleBed:0 AC'),
    ('3', 'Casual  SingleBed:1  DoubleBed:0 Non-AC'),
    ('4', 'Suite   SingleBed:0  DoubleBed:2 AC'),
    ('5', 'Suite   SingleBed:1  DoubleBed:2 AC')

)


class hotelupdateform(forms.Form):
    name = forms.CharField(max_length=200)
    location = forms.CharField(max_length=500)
    country = forms.CharField(max_length=500)
    description = forms.Textarea()
    address = forms.CharField(max_length=200)
    phone = forms.IntegerField()


class photoupload(forms.ModelForm):
    class Meta:
        model = Photos
        fields = ('file', 'roomid', 'userid')
        widgets = {
            'file': ClearableFileInput(attrs={'multiple': True}),
        }


class HotelUpdateRoom(forms.Form):
    wifi = forms.ChoiceField(choices=CHOICES)
    breakfast = forms.ChoiceField(choices=CHOICES)
    price = forms.IntegerField()
    roomCount = forms.IntegerField()


class HotelAddRoomForm(forms.Form):
    room = forms.ChoiceField(choices=ROOMTYPES)
    wifi = forms.ChoiceField(choices=CHOICES)
    breakfast = forms.ChoiceField(choices=CHOICES)
    price = forms.DecimalField()
    roomCount = forms.IntegerField()


class FlightAddRouteForm(forms.Form):
    Source = forms.CharField(max_length=200)
    Destination = forms.CharField(max_length=200)


class airlinesupdateform(forms.Form):
    name = forms.CharField(max_length=200)
    # address = forms.CharField(max_length=200)
    # phone = forms.IntegerField()


class FlightUpdateForm(forms.Form):
    TotalSeats = forms.IntegerField()


class FlightAddFlight(forms.Form):
    AirplaneNumber = forms.CharField(max_length=200)
    Aircraft = forms.CharField(max_length=200)
    TotalSeats = forms.IntegerField()


class FlightAddFlightRoute(forms.Form):
    my_arg = 0

    def __init__(self, *args, **kwargs):
        my_arg = kwargs.pop('my_arg')
        super(FlightAddFlightRoute, self).__init__(*args, **kwargs)
        self.my_arg = my_arg
        print("my_Arg")
        print(my_arg)
        cursor = connection.cursor()
        cursor.execute("SELECT F.id,F.Airplane_Number, F.Aircraft,F.TotalSeats "
                       "FROM database_flight F JOIN database_air_company A on (A.id = F.AirCompany_id) "
                       "WHERE A.CompanyAdmin_id = %s", [my_arg])
        my_tuple2 = []
        results = cursor.fetchall()
        for row in results:
            str = row[1]
            my_tuple2.append((row[0], str))

        FLIGHTS = tuple(my_tuple2)
        self.fields['Flight'] = forms.ChoiceField(choices=FLIGHTS)

    # my_field = forms.CharField(initial=my_arg)
    results = Route.objects.all()
    my_tuple = []
    i = 1
    for row in results:
        var = row.Source + "-" + row.Destination
        my_tuple.append((i, var))
        i = i + 1
    ROUTES = tuple(my_tuple)

    results = Cancellation_Policy.objects.all()
    my_tuple = []
    i = 1
    for row in results:
        var = []
        var.append('Booking can be cancelled upto ')
        var.append(str(row.DaysCount))
        var.append(' days of booking and ')
        var.append(str(row.Percentage_refunding))
        var.append('% of advanced payment is returned to the customer')
        var = ''.join(var)

        # var =  "Booking can be cancelled upto " #+ ' days of booking and ' + str(row.Percentage_refunding) + '% of advanced payment is returned to the customer'
        my_tuple.append((i, var))
        i = i + 1
    CANCELLATIONPOLICIES = tuple(my_tuple)

    Route = forms.ChoiceField(choices=ROUTES)
    Cancellation_Policy = forms.ChoiceField(choices=CANCELLATIONPOLICIES)
    Source_Airport = forms.CharField(max_length=200)
    Destination_Airport = forms.CharField(max_length=200)
    Date = forms.DateField()
    Time = forms.TimeField()
    Duration = forms.IntegerField()
    Price = forms.IntegerField()
