import requests
import xml.etree.ElementTree as ET
from datetime import datetime

class Schiene2():

  dbAccessToken = '3356e54605aa647bc8cb8c4eb70a1938'

  def eva(self, station):
    headers = {
      'Authorization': 'Bearer {0}'.format(self.dbAccessToken)
    }
    res = requests.get('https://api.deutschebahn.com/timetables/v1/station/{0}'.format(station), headers=headers)
    root = ET.fromstring(res.content)
    return root[0].attrib['eva']

  def connections(self, origin, destination, dt=datetime.now(), only_direct=False):
    return
