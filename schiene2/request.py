import hashlib
import json
import requests

def md5(string, salt):
  m = hashlib.md5()
  m.update(string.encode('utf-8'))
  m.update(salt.encode('utf-8'))
  return m.hexdigest()

def request(payload):
  headers = {
    'Content-Type': 'application/json',
    'Accept-Encoding': 'gzip, deflate',
    'user-agent': 'schiene2'
  }
  body = {
    'lang': 'en',
    'svcReqL': [{
      'cfg': {
        'polyEnc': 'GPA'
      },
      'meth': 'TripSearch',
      'req': payload
    }],
    'client': {
      'id': 'DB',
      'v': '16040000',
      'type': 'IPH',
      'name': 'DB Navigator'
    },
    'ext': 'DB.R15.12.a',
    'ver': '1.15',
    'auth': {
      'type': 'AID',
      'aid': 'n91dB8Z77MLdoR0K'
    }
  }
  params = {
    'checksum': md5(json.dumps(body), 'bdI8UVj40K5fvxwf')
  }
  res = requests.post('https://reiseauskunft.bahn.de/bin/mgate.exe', headers=headers, data=json.dumps(body), params=params)
  return res.json()
