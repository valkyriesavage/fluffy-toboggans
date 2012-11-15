# sensorhistory.py

import time, datetime
import sys
import traceback
def formatExceptionInfo(maxTBlevel=5):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.__dict__["args"]
    except KeyError:
        excArgs = "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    return (excName, excArgs, excTb)


class SensorHistories:
    # array of sensor data
    sensorhistories = []

    def __init__(self):
        self.sensorhistories = []

    def __init__(self, f):
        if f:
            self.readfromfile(f)

    def find(self, sensornum):
        for history in self.sensorhistories:
            if history.sensornum == sensornum:
                return history
        # none found, create it!
        history = SensorHistory(sensornum)
        self.sensorhistories.append(history)
        return history

    def readfromfile(self, f):
        curryear = 0
        currmonth = 0
        currdate = 0

        currdailypowerusage = None

        for line in f:
            try:
                line = line.strip()
                #print line
                if (line[0] == '#'):
                    continue

                # divide up into [0] date, [1] time, [2] sensornum, [3] Watts used
                # this parsing isnt very flexible...it would be nice if it was rugged :(
                foo = line.split(', ')
                timestamp = foo[1]
                sensornum = int(foo[2])
                powerused = float(foo[3])
                dateset = foo[0].split(' ')
                year = int(dateset[0])
                month = int(dateset[1])
                date = int(dateset[2])

                # debug print out that parsed line
                # print "#", year, month, date, timestamp, sensornum,  powerused

                if not ( datetime.date.today().year == year and datetime.date.today().month == month and datetime.date.today().day == date) :
                    pass            # older data, skip it

                # get the 'seconds since epoch' time for the datapoint
                datapointtime = time.mktime( time.strptime(foo[0]+", "+foo[1], "%Y %m %d, %H:%M") )
                history = self.find(sensornum)
                if history.lasttime > datapointtime:
                    # this is the first datapoint for this sensor
                    history.lasttime = datapointtime
                    # the next time we go through, we'll have a delta of time
                    continue

                # figure out how much time has elapsed since last datapoint
                #print (datapointtime - history.lasttime), " seconds elapsed since last datapoint"

                # calculate how many Watthrs since last datapoint
                #print powerused * (datapointtime - history.lasttime) / (60.0 * 60.0)
                # add that to the current sensorhistory dayswatthr
                history.dayswatthr += powerused * (datapointtime - history.lasttime) / (60.0 * 60.0)

                history.lasttime = datapointtime
            except:
                print formatExceptionInfo()

        for history in self.sensorhistories:
            history.lasttime = time.time()

    def __str__(self):
        s = ""
        for history in self.sensorhistories:
            s += history.__str__()
        return s

####### store sensor data and array of histories per sensor
class SensorHistory:
  sensornum = 0                # the ID for this set of data
  cumulative5mwatthr =  0      # data for power collected over last 5 minutes
  dayswatthr = 0               # power collected over last full day
  fiveminutetimer = 0
  lasttime = 0
  dataPointCount = 0            #  02.18.2011 tps Count number of data points
                                #  accumulated in 5 minute period.

  def __init__(self, sensornum):
      self.sensornum = sensornum
      self.fiveminutetimer = time.time()  # track data over 5 minutes
      self.lasttime = time.time()
      self.cumulative5mwatthr = 0
      self.dayswatthr = 0
      self.dataPointCount = 0   # 02.18.2011 tps

  def addwatthr(self, deltawatthr):
      self.cumulative5mwatthr +=  float(deltawatthr)
      self.dayswatthr += float(deltawatthr)

  # chrisjx, 08.27.2010, added this to genericise sensorhistory for any value type
  def addvalue(self, deltawatthr):
      self.cumulative5mwatthr +=  float(deltawatthr)
      self.dayswatthr += float(deltawatthr)
      self.dataPointCount += 1 # 02.18.2011 tps
      # print time.strftime("%H:%M:%S", time.localtime()), self.dataPointCount, deltawatthr, self.cumulative5mwatthr  # 02.21.2011 tps

  def reset5mintimer(self):
      self.cumulative5mwatthr = 0
      self.fiveminutetimer = time.time()
      self.dataPointCount = 0   # 02.18.2011 tps

  def avgwattover5min(self):
      return self.cumulative5mwatthr * (60.0*60.0 / (time.time() - self.fiveminutetimer))

  # chrisjx, 08.27.2010, added this to genericise sensorhistory for any value type
  def avgunitsover5min(self):
      # 02.18.2011 tps Average of data points accumulated over past 5 minutes
      return self.cumulative5mwatthr / self.dataPointCount
      #return self.cumulative5mwatthr * (60.0*60.0 / (time.time() - self.fiveminutetimer))

  def __str__(self):
      return "[ id#: %d, 5mintimer: %f, lasttime; %f, 5minwatthr: %f, daywatthr = %f]" % (self.sensornum, self.fiveminutetimer, self.lasttime, self.cumulative5mwatthr, self.dayswatthr)
