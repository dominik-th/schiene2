import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import request
import parse

def formatTimedelta(td):
  hours = str(int(td.total_seconds() / 60 / 60))
  minutes = str(int(td.total_seconds() / 60 % 60))
  return hours + ':' + ('0' if len(minutes) <= 1 else '') + minutes

# https://github.com/kennell/schiene/blob/3cccbbc940b85dd041cab49d8a85bf6265896cdf/schiene/schiene.py#L40
def parse_stations(html):
  """
      Strips JS code, loads JSON
  """
  html = html.replace('SLs.sls=', '').replace(';SLs.showSuggestion();', '')
  html = json.loads(html)
  return html['suggestions']

class Schiene2():

  dbAccessToken = '3356e54605aa647bc8cb8c4eb70a1938'

  def evaDBApi(self, station):
    headers = {
      'Authorization': 'Bearer {0}'.format(self.dbAccessToken)
    }
    res = requests.get('https://api.deutschebahn.com/timetables/v1/station/{0}'.format(station), headers=headers)
    root = ET.fromstring(res.content)
    return root[0].attrib['eva']

  def eva(self, station):
    query = {
      'start': 1,
      'S': station + '?',
      'REQ0JourneyStopsB': 1 # number of results
    }
    rsp = requests.get('https://reiseauskunft.bahn.de/bin/ajax-getstop.exe/dn', params=query)
    results = rsp.text.replace('SLs.sls=', '').replace(';SLs.showSuggestion();', '')
    results = json.loads(results)['suggestions']
    return int(results[0]['extId'])

  def connections(self, origin, destination, dt=datetime.now(), only_direct=False):
    try:
      originEva = self.eva(origin)
      destinationEva = self.eva(destination)
    except (NameError, IndexError, KeyError):
      raise ValueError('station not found')
    req = {
      'outDate': dt.strftime('%Y%m%d'), # departure date
      'outTime': dt.strftime('%H%M%S'), # departure time
      'ctxScr': None, # not sure
      'getPasslist': False, # get passed stations
      'maxChg': 0 if only_direct else 5, # transfers
      'minChgTime': 0, # transfer time
      'depLocL': [{ # departure location
        'lid': 'A=1@L={0}@'.format(originEva)
      }],
      'viaLocL': None, # via location
      'arrLocL': [{ # arrival location
        'lid': 'A=1@L={0}@'.format(destinationEva)
      }],
      'jnyFltrL': [{ # journey filters, products
        'type': 'PROD',
        'mode': 'INC',
        'value': '511'
      }, {
        'type': 'META',
        'mode': 'INC',
        'meta': 'notBarrierfree'
      }],
      'getTariff': False, # tickets
      'getPT': True, # not sure what this is
      'outFrwd': True, # not sure what this is
      'getIV': False, # walk and bike alternatives?
      'getPolyline': False, # shape for displaying on a map
      'numF': 5, # number of results
      'trfReq': {
        'jnyCl': 2, # first class options
        'tvlrProf': [{
          'type': 'E',
          'redtnCard': None # loyalty card
        }],
        'cType': 'PK' # not sure
      }
    }
    res = request.request(req)
    connections = res['svcResL'][0]['res']['outConL']
    journeys = []
    for connection in connections:
      journey = {
        'transfers': connection['chg']
      }
      arrival = parse.dt(dt, connection['arr']['aTimeS'])
      journey['arrival'] = arrival.strftime('%H:%M')

      departure = parse.dt(dt, connection['dep']['dTimeS'])
      journey['departure'] = departure.strftime('%H:%M')

      delay = {}
      try:
        departureR = parse.dt(dt, connection['dep']['dTimeR'])
        if (departureR - departure).total_seconds() >= 60:
          delay['delay_departure'] = int((departureR - departure).total_seconds()/60)
      except:
        pass

      try:
        arrivalR = parse.dt(dt, connection['arr']['aTimeR'])
        if (arrivalR - arrival).total_seconds() >= 60:
          delay['delay_arrival'] = int((arrivalR - arrival).total_seconds()/60)
      except:
        pass

      time = parse.td(connection['dur'])
      journey['time'] = formatTimedelta(time)

      price = connection['trfRes']['fareSetL'][0]['fareL'][0]['prc']
      journey['price'] = None if price <= 0 else price / 100

      if delay:
        journey['delay'] =  delay

      products = []
      canceled = False
      for leg in connection['secL']:
        if leg['type'] == 'JNY':
          product = res['svcResL'][0]['res']['common']['prodL'][leg['jny']['prodX']]['prodCtx']['catOut']
          if 'aCncl' in leg['arr'] and leg['arr']['aCncl']:
            canceled = True
          if 'dCncl' in leg['dep'] and leg['dep']['dCncl']:
            canceled = True
          if not product in products:
            products.append(product)

      journey['products'] =  products
      journey['ontime'] = False if delay or canceled else True
      journey['canceled'] = canceled

      journeys.append(journey)
    return journeys

  # https://github.com/kennell/schiene/blob/3cccbbc940b85dd041cab49d8a85bf6265896cdf/schiene/schiene.py#L99
  def stations(self, station, limit=10):
    """
    Find stations for given queries
    Args:
        station (str): search query
        limit (int): limit number of results
    """
    query = {
      'start': 1,
      'S': station + '?',
      'REQ0JourneyStopsB': limit
    }
    rsp = requests.get('http://reiseauskunft.bahn.de/bin/ajax-getstop.exe/dn', params=query)
    return parse_stations(rsp.text)
