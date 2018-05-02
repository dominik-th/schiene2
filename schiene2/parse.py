import datetime

def td(string):
  hours = int(string[:2])
  minutes = int(string[2:4])
  seconds = int(string[4:6])
  return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

def dt(date, string):
  dateOffset = 0
  if len(string) == 8:
    dateOffset = int(string[:2])
    string = string[2:8]
  hour = int(string[:2])
  minute = int(string[2:4])
  second = int(string[4:6])
  return (datetime.datetime(date.year, date.month, date.day, hour, minute, second) + datetime.timedelta(days=dateOffset))
