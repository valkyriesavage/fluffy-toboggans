# testLogFile.py
# to test the creation of a new daily log file
import time, datetime, sys


##############################################################
def checkdailylog(lofilename):

    if lofilename == None:
        return false

    TimeStamp = "%s" % (time.strftime( "%Y%m%d%M"))
    checkname = "/opt/www/testlog"+TimeStamp+".csv"

    if lofilename == checkname:
        return True
    else:
        return False


##############################################################
def getlogfile():
# open our datalogging file


    TimeStamp = "%s" % (time.strftime("%Y%m%d%M"))
    # print "TimeStamp", TimeStamp 
    filename = "/opt/www/testlog"+TimeStamp+".csv"   # where we will store our flatfile data

    lfile = None
    try:
        lfile = open(filename, 'r+')
    except IOError:
        # didn't exist yet
        lfile = open(filename, 'w+')
        lfile.write("#Date, time, sensornum, value\n");
        lfile.flush()

    return lfile



##############################################################

logfile = getlogfile()
print "Log file "+logfile.name+" opened..."

while True:

    if checkdailylog(logfile.name) == False:
        logfile = getlogfile()
        print "current log file=", logfile.name


    time.sleep(10)
    print "sleep log file=", logfile.name
