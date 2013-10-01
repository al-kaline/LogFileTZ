##############################################################
#
#        d8888                                             888
#       d88888                                             888 
#      d88P888                                             888
#     d88P 888 888d888 .d8888b   .d88b.  88888b.   8888b.  888
#    d88P  888 888P    88K      d8P  Y8b 888  88b      88b 888
#   d88P   888 888      Y8888b. 88888888 888  888 .d888888 888 
#  d8888888888 888          X88 Y8b.     888  888 888  888 888
# d88P     888 888      88888P    Y8888  888  888  Y888888 888
#
#  8888888b.
#  888   Y88b                                   
#  888    888
#  888   d88P .d88b.   .d8888b .d88b.  88888b.
#  8888888P  d8P  Y8b d88P    d88  88b 888  88b 
#  888 T88b  88888888 888     888  888 888  888 
#  888  T88b Y8b.     Y88b.   Y88..88P 888  888 
#  888   T88b  Y8888    Y8888P  Y88P   888  888 
#
# bgerdon@arsenalexperts.com
#
# Take the output from LogFileParser 
# (https://code.google.com/p/mft2csv/wiki/LogFileParser)
# and convert to specified timezone
#
##############################################################

import sys
import re
from datetime import date, datetime
from pytz import timezone
from optparse import OptionParser

###
# tz list from http://stackoverflow.com/questions/13866926/python-pytz-list-of-timezones
###

###
# initialize
###
OFFSET = 0
MFTReference = 1

###
# what our header row ofthen looks like
##
# Offset,MFTReference,MFTBaseRecRef,LSN,LSNPrevious,RedoOperation,UndoOperation,OffsetInMft,FileName,CurrentAttribute,UsnJrnlFileName,FileNameModified,UsnJrnlMFTReference,UsnJrnlMFTParentReference,UsnJrnlTimestamp,UsnJrnlReason,SI_CTime,SI_ATime,SI_MTime,SI_RTime,SI_FilePermission,SI_MaxVersions,SI_VersionNumber,SI_ClassID,SI_SecurityID,SI_QuotaCharged,SI_USN,SI_PartialValue,FN_CTime,FN_ATime,FN_MTime,FN_RTime,FN_AllocSize,FN_RealSize,FN_Flags,DT_StartVCN,DT_LastVCN,DT_ComprUnitSize,DT_AllocSize,DT_RealSize,DT_InitStreamSize,DT_DataRuns,DT_Name
####
Offset = 0
SI_CTime = 16
SI_ATime = 17
SI_MTime = 18
SI_RTime = 19
FN_CTime = 28
FN_ATime = 29
FN_MTime = 30
FN_RTime = 31



def convertTimezone(dateString, timez):

###
# 'try' to parse out the date and time so
# that we can remove the ":"s between the
# milliseconds and microsecond and replace
# it with a period
###
    try:
        [date, time] = re.split(' ', dateString)
        [h, m, s, ms, us] = re.split(':', time)
        time = h+":"+m+":"+s+"."+ms
        dateString = date+" "+time
    except:
        return dateString

###
# 'try' to identify the date
# format to see if we can then
# change the TZ
###
    try:
        tmpTime = datetime.strptime(dateString, "%Y-%m-%d %H:%M:%S.%f")
    except:
        try:
            tmpTime = datetime.strptime(dateString, "%Y-%m-%d %H:%M:%S")
        except:
             return 0
            
###
# default to UTC
###
    tmpTime_utc = tmpTime.replace(tzinfo=timezone('UTC'))

###
# 'try' to convert to timezone 'timez'
###
    try:
        tmpTime = tmpTime_utc.astimezone(timezone(timez))
    except:
        tmpTime = tmpTime_utc.astimezone(timezone('UTC'))


    return tmpTime



def parseLine(line, timezone, o):

    a = []
    a = line.split(',')

###
# if the line starts with 'Offset'
# then its the header row and we
# should just print
###
    if ('Offset' in a[Offset]):
        o.write(",".join(a))


###
# let's convert some time!
###
    if ('0x' in a[Offset]):
        a[SI_CTime] = str(convertTimezone(a[SI_CTime], timezone))
        a[SI_ATime] = str(convertTimezone(a[SI_ATime], timezone))
        a[SI_MTime] = str(convertTimezone(a[SI_MTime], timezone))
        a[SI_RTime] = str(convertTimezone(a[SI_RTime], timezone))
        a[FN_CTime] = str(convertTimezone(a[FN_CTime], timezone))
        a[FN_ATime] = str(convertTimezone(a[FN_ATime], timezone))
        a[FN_MTime] = str(convertTimezone(a[FN_MTime], timezone))
        a[FN_RTime] = str(convertTimezone(a[FN_RTime], timezone))
        o.write(",".join(a))


def main():

    usage = "usage: %prog -f filename [-z timezone] [-o outputFile]\n or .. usage: %prog -l (to list timezones)"
    parser = OptionParser(usage) 
    parser.add_option("-f", dest="inputFile", help="Input File")
    parser.add_option("-o", dest="outputFile", help="Output File")
    parser.add_option("-z", dest="timezone", action="store", help="TZ")
    parser.add_option("-l", dest="printTZList", action="store_true") 
    (options, args) = parser.parse_args()

    if not (options.inputFile or options.printTZList):
        print usage
        exit(0)

    if (options.printTZList):
        import pytz
        for tz in pytz.all_timezones:
            print tz
        exit(0)

    try:
        
        f = open(options.inputFile,'r')
        if (options.outputFile):
            o = open(options.outputFile, 'w')
        else:
            o = sys.stdout

        for line in f:

            line.rstrip('\r\n')
            parseLine(line, options.timezone, o)
        
        if (o):
            o.close
        f.close

    except Exception, e:
        print e

if __name__ == "__main__":
    main()
