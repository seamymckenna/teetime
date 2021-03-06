#!/usr/bin/env python

import requests, datetime
from re import findall, search, DOTALL, IGNORECASE
from time import sleep
from os import environ

def lambda_handler(event, context):

    booking1_username = environ["USER1"]
    booking1_password = environ["PASSWORD1"]
    booking2_username = environ["USER2"]
    booking2_password = environ["PASSWORD2"]

    #Define Type
    lBookingType=['Confirm Competition Booking','Confirm Casual Booking']

    #Calculate Date
    bookingDate=datetime.date.today() + datetime.timedelta(days=12)

    #Specify fourball players
    fourballs={1:{'bookingPayload' : {'Player1_uid' : '1437',
                                      'Player2_uid' : '1572',
                                      'Player3_uid' : '1438',
                                      'Player4_uid' : '1578',
                                      'course_id' : '1',
                                      'unique_id' : None,
                                      'd_date' : bookingDate,
                                      'Booking_Operation' : None},
                 'loginPayload': {'_username':booking1_username,'_password':booking1_password, "_csrf_token": ''}},
              2:{'bookingPayload' : {'Player1_uid' : '1434',
                                     'Player2_uid' : '1436',
                                     'course_id' : '1',
                                     'unique_id' : None,
                                     'd_date' : bookingDate,
                                     'Booking_Operation' : None},
                 'loginPayload': {'_username':booking2_username,'_password':booking2_password, "_csrf_token": ''}}}

    #Define Uri's
    loginUri='https://www.brsgolf.com/killymoon/member/login_check'
    timeSlotsUri='https://www.brsgolf.com/killymoon/members_booking.php?operation=member_day&d_date={}&course_id1=1'.format(bookingDate)
    bookingUri='https://www.brsgolf.com/killymoon/members_booking.php?operation=member_process_booking'
    #Define polling interval
    pollInterval=30

    for group in fourballs.values():

        try:
          #1) Login
          headers = {'User-Agent': 'Mozilla/5.0'}
          session = requests.session()
          result = session.get(loginUri)
          #e.g _csrf_token" value="2360ba910dba76930ef8add5a07b84dbc15a820d">
          token = search('_csrf_token. value=.([a-f0-9]*)', result.text).group(1)
          group['loginPayload']['_csrf_token'] = token
          data=session.post(loginUri,group['loginPayload'])
          data = session.get(timeSlotsUri)

          #2) Get first available timeslot
          for i in range(2):
            data = session.get(timeSlotsUri)
            #if search('Not Live Yet',data.text):
            #  print '{}: sleeping...'.format(datetime.datetime.today())
            #  sleep(pollInterval)
            #else:
            if search('value=.Book Now',data.text,IGNORECASE):
              break
            else:
              print '{}: sleeping...'.format(datetime.datetime.today())
              sleep(pollInterval)

          #assuming now live, get all timeslot id's. Discard those pre sunrise. Remember to match those only with 4 free slots
          timeslotData = findall('(08:.*)',data.text,DOTALL)[0]
          timeslots = findall('<td></td>[\r\n]+<td></td>[\r\n]+<td></td>[\r\n]+<td></td>.*?unique_id.*?VALUE=.([0-9]*)',timeslotData,DOTALL)
          print timeslots

          #3) Book Timeslot, update payload
          group['bookingPayload']['unique_id'] = timeslots[0]
          for bookingType in lBookingType:
            group['bookingPayload']['Booking_Operation'] = bookingType
            print '{}: {}'.format(datetime.datetime.today(),group['bookingPayload'])
            data = session.post(bookingUri,data=group['bookingPayload'])
            print '{}: {}: {}'.format(datetime.datetime.today(),bookingType,data)
        except Exception as e:
          print e

if __name__ == "__main__":
    lambda_handler('x','y')


