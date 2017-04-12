#!/usr/bin/env python

#30 8  * * 2 
import requests, datetime, yaml, os
from sys import exit
from re import findall, search, DOTALL, IGNORECASE
from time import sleep

#Player Ids
#</option><option value="1437">McKenna,  Seamus (N)
#</option><option value="1436">O'Kane,  Diarmuid
#</option><option value="1438">O'Kane,  James (N)
#</option><option value="1434">McDaid,  Barry (N) M
#</option><option value="1435">Devlin,  Paul (N)
#</option><option value="1439">Kidd,  Martin (N)
#</option><option value="1257">McKenna, Conor
#<option value="1578">O Neill,  Mark</option>

#Load Passwords
with open(os.path.dirname(os.path.realpath(__file__)) + "/.config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
booking1_username = cfg['user1']['username']
booking1_password = cfg['user1']['password']
booking2_username = cfg['user2']['username']
booking2_password = cfg['user2']['password']

#Sleep to account for minor drift
sleep(5)

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
             'loginPayload': {'GUILDNUMBER_VALIDATE':booking1_username,'PASSWORD_VALIDATE':booking1_password}},
          2:{'bookingPayload' : {'Player1_uid' : '1434',
                                 'Player2_uid' : '1436',
                                 'course_id' : '1',
                                 'unique_id' : None,
                                 'd_date' : bookingDate,
                                 'Booking_Operation' : None},
              'loginPayload': {'GUILDNUMBER_VALIDATE':booking2_username,'PASSWORD_VALIDATE':booking2_password}}}

#Define Uri's
loginUri='https://www.brsgolf.com/killymoon/user_admin.php?stage=login'
timeSlotsUri='https://www.brsgolf.com/killymoon/members_booking.php?operation=member_day&d_date={}&course_id1=1'.format(bookingDate)
bookingUri='https://www.brsgolf.com/killymoon/members_booking.php?operation=member_process_booking'

#Define polling interval
pollInterval=30

for group in fourballs.values():

    try:
      #1) Login
      headers = {'User-Agent': 'Mozilla/5.0'}
      session = requests.Session()
      data=session.post(loginUri,data=group['loginPayload'])
      #2) Get first available timeslot
      for i in range(2):
        session = requests.Session()
        session.post(loginUri,data=group['loginPayload'])
        data = session.get(timeSlotsUri)
        #if search('Not Live Yet',data.text):
        #  print '{}: sleeping...'.format(datetime.datetime.today())
        #  sleep(pollInterval)
        #else:
        #  break
        print data.text
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
    except:
      pass
