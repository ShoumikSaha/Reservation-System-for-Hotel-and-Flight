import re
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    Phone = models.PositiveIntegerField()
    Address = models.CharField(max_length=1000)
    Passport_Number = models.CharField(max_length=100, null=True)
    Payment_Info = models.CharField(max_length=100, null=True)
    TotalSentMoney = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Hotel(models.Model):
    Hotel_Name = models.CharField(max_length=200)
    Hotel_Location = models.CharField(max_length=500)
    Hotel_Country = models.CharField(max_length=500, null=True)
    TotalSentMoney = models.FloatField()
    Percentage = models.FloatField()
    CompanyAdmin = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    Description = models.TextField(null=True)
    Address = models.CharField(max_length=200, null=True)
    Phone = models.PositiveIntegerField(null=True)
    Latitude = models.FloatField(null=True)
    Longitude = models.FloatField(null=True)

    def __str__(self):
        return self.Hotel_Name


class Room(models.Model):
    SingleBedCount = models.IntegerField()
    DoubleBedCount = models.IntegerField()
    RoomType = models.CharField(max_length=100)
    AirConditioner = models.BooleanField()

    def __str__(self):
        return 'Type:' + self.RoomType + '   Single Bed:' + str(self.SingleBedCount) + '   Double Bed:' + str(
            self.DoubleBedCount) + '   AC:' + str(self.AirConditioner)


class Cancellation_Policy(models.Model):
    DaysCount = models.IntegerField(default=10)
    Percentage_refunding = models.FloatField(default=80.0)


class Hotel_Room(models.Model):
    Hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    Room = models.ForeignKey(Room, on_delete=models.CASCADE)
    Price = models.FloatField()
    Complimentary_Breakfast = models.BooleanField()
    Wifi = models.BooleanField()
    TotalRoomCount = models.IntegerField(default=2)
    FreeRoomCount = models.IntegerField(default=2)
    Cancellation_Policy = models.ForeignKey(Cancellation_Policy, on_delete=models.CASCADE, default=1)


class Air_Company(models.Model):
    AirCompany_Name = models.CharField(max_length=200)
    TotalSentMoney = models.FloatField()
    Percentage = models.FloatField()
    CompanyAdmin = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.AirCompany_Name


class Flight(models.Model):
    AirCompany = models.ForeignKey(Air_Company, on_delete=models.CASCADE)
    Airplane_Number = models.CharField(max_length=200)
    Aircraft = models.CharField(max_length=200, null=True)
    TotalSeats = models.PositiveIntegerField(default=100, null=True)

    def __str__(self):
        return self.Airplane_Number


class Route(models.Model):
    Source = models.CharField(max_length=200)
    Destination = models.CharField(max_length=200)

    def __str__(self):
        return self.Source + " - " + self.Destination


class Flight_Route(models.Model):
    Route = models.ForeignKey(Route, on_delete=models.CASCADE)
    Flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    Time = models.TimeField(auto_now=False, auto_now_add=False, null=True)
    Date = models.DateField(auto_now=False, auto_now_add=False, null=True)
    Price = models.FloatField(null=True)
    Duration = models.IntegerField(default=30, null=True)
    Source_Airport = models.CharField(max_length=200, null=True)
    Destination_Airport = models.CharField(max_length=200, null=True)
    TotalSeatsBooked = models.PositiveIntegerField(default=0, null=True)
    Cancellation_Policy = models.ForeignKey(Cancellation_Policy, on_delete=models.CASCADE, default=1)


class Booking(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    MoneyToPay = models.FloatField()
    MoneyToRefund = models.FloatField()
    DateOfBooking = models.DateField(auto_now=False, auto_now_add=False)
    DateOfCancellation = models.DateField(auto_now=False, auto_now_add=False)
    isCancelled = models.BooleanField(default=False)
    # 0 Booked, 1 Confirmed, 2 Cancelled
    Status = models.IntegerField(default=0)
    PaidMoney = models.FloatField(default=0)


    def __str__(self):
        return self.User + ' ' + self.DateOfBooking


class Hotel_Booking(models.Model):
    Booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    Hotel_Room = models.ForeignKey(Hotel_Room, on_delete=models.CASCADE)
    Checkin_Date = models.DateField(auto_now=False, auto_now_add=False, null=True)
    Checkout_Date = models.DateField(auto_now=False, auto_now_add=False, null=True)
    TotalRooms = models.PositiveIntegerField(default=1, null=True)
    isApproved = models.BooleanField(null=True, default=False)


class Flight_Booking(models.Model):
    Booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    Flight = models.ForeignKey(Flight_Route, on_delete=models.CASCADE, null=True)
    TotalSeats = models.PositiveIntegerField(default=1, null=True)
    isApproved = models.BooleanField(null=True, default=False)


class Payment_Log(models.Model):
    Admin = models.ForeignKey(User, on_delete=models.CASCADE)
    Booking = models.ForeignKey(Booking, on_delete=models.CASCADE)


class Cancellation_Log(models.Model):
    Admin = models.ForeignKey(User, on_delete=models.CASCADE)
    Booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    notified = models.BooleanField(default=False)


class BookingLog(models.Model):
    Admin = models.ForeignKey(User, on_delete=models.CASCADE)
    Booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    # 0 admin, 1 user
    Actor = models.BooleanField(default=False)
    Message = models.CharField(max_length=100, null=True)
    notified = models.BooleanField(default=False)
