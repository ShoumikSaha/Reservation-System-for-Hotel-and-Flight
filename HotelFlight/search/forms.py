from django import forms
import datetime

CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
)


class SearchHotelForm(forms.Form):
    hoteldest = forms.CharField(label='Hotel or destination place', max_length=100)
    checkin = forms.DateField()
    checkout = forms.DateField()
    room = forms.CharField(widget=forms.Select(choices=CHOICES))
    adult = forms.CharField(widget=forms.Select(choices=CHOICES))
    children = forms.CharField(widget=forms.Select(choices=CHOICES))


class SearchFlightForm(forms.Form):
    source = forms.CharField(label='City or airport', max_length=100)
    dest = forms.CharField(label='City or airport', max_length=100)
    depart = forms.DateField()
    checkout = forms.DateField()
    adult = forms.CharField(widget=forms.Select(choices=CHOICES))
    children = forms.CharField(widget=forms.Select(choices=CHOICES))
