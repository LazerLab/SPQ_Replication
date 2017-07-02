'''
Completeness: 10%

This code goes through the studies reported in Radford et al. and dumps the raw json data for all experimental sessions.
'''

import os, csv, json
import datetime as dt
import cPickle
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde,ttest_ind
from matplotlib import pyplot as pp
import urllib
from httplib2 import Http

#url='http://www.volunteerscience.com/data/89/?format=json&amt=include&start=04%2F15%2F2014+11%3A47&end=04%2F15%2F2014+11%3A59'
#page=urllib2.urlopen(url)
#data=json.loads(page.read())

#urllib2.urlopen('http://www.timeanddate.com/worldclock/astronomy.html?n=78').read())

#resFile='C:\Data\Lazer Data\VS\FlankerData\\06-06-2014TestDtaNoAdmins.json'
#
#f=open(resFile,'rb')
#l=f.read()
#f.close()
#
#data = json.loads(l)['tests']


def urlConstruct(params,game):
    tok='9eb10bd50a56c89825ab6bcccffb76ebd81b0d62'
    url='http://volunteerscience.com/data/'+game+'/?format=json&'+urllib.urlencode(params)+'&token='+tok
    client=Http()
    content = client.request(url,method='GET',body='')
    data = json.loads(content[1])['tests']
    return data



params=[('format','json'),('variables','all'),('amt','exclude'),('pi','exclude'),('start','01/01/2014'),('end','12/31/2015')]#('end',dt.date.strftime(dt.date.today(),"%m/%d/%Y"))]
studies={'TSP':'3','Flanker':'90','Stroop':'89','JW_Reaction_Time':'173'}

for name,game in studies.iteritems():
    data=urlConstruct(params,game)
    print 'saving ', name
    with open('Dump_Data/'+name+'.json','wb') as f:
        json.dump(data,f)


studies={'Prisoners_Dilemma':'81','Commons_Dilemma':'80'}
params=[('format','json'),('variables','all'),('amt','exclude'),('pi','exclude'),('start','12/09/2015'),('end','12/31/2015')]#('end',dt.date.strftime(dt.date.today(),"%m/%d/%Y"))]
for name,game in studies.iteritems():
    data=urlConstruct(params,game)
    print 'saving ', name
    with open('Raw_Data/'+name+'.json','wb') as f:
        json.dump(data,f)




