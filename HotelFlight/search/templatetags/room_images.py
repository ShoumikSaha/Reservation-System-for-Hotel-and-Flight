from django import template
import os

register = template.Library()


@register.simple_tag
def room_images(userid, roomid):
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    userf = 'user_' + str(userid)
    roomf = 'room_' + str(roomid)
    root = os.path.join(root, 'HotelFlight/static/media/' + userf + '/' + roomf)
    imagelist = os.listdir(root)
    return imagelist
