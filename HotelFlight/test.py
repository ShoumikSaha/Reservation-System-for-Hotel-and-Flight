from collections import namedtuple
from django.db import connection


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


cursor = connection.cursor()
cursor.execute("select distinct HB.Checkin_Date,HB.Checkout_Date,B.User_id,U.first_name,U.last_name,U.email,P.Phone,"
               "P.Address,B.MoneyToPay,(B.MoneyToPay-B.MoneyToRefund) as 'Paid',B.MoneyToRefund as 'Pending',"
               "HR.Room_id,HB.TotalRooms from database_hotel_booking HB join database_hotel_room HR "
               "on(HR.id=HB.Hotel_Room_id) join database_booking B on(HB.Booking_id=B.id) join auth_user U "
               "on(U.id=B.User_id) join database_profile P on(P.user_id=U.id)where HB.Checkin_Date>=2019-07-23 and "
               "HR.Hotel_id=1 order by HB.Checkin_Date,HB.Checkout_Date,B.MoneyToPay")
result = namedtuplefetchall(cursor)
print(result)

print('commit from pc')
