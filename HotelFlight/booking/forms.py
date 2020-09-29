from django import forms


class HotelBookingForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=100)
    last_name = forms.CharField(label='Last Name', max_length=100)
    email = forms.CharField(label='Email', max_length=100)
    phone = forms.CharField(label='Phone Number', max_length=100)


class FlightBookingForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=100)
    last_name = forms.CharField(label='Last Name', max_length=100)
    email = forms.CharField(label='Email', max_length=100)
    phone = forms.CharField(label='Phone Number', max_length=100)
    passport = forms.CharField(label='Passport', max_length=100)

