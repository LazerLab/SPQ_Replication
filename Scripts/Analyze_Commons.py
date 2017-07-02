
import datetime as dt
import csv
import numpy as np
from scipy.stats import gaussian_kde,ttest_ind
from matplotlib import pyplot as pp
import scipy as sp
import scipy.stats

def importData(fname):
    '''import cleaned csv data file. '''
    data=[]
    f=open('Clean_Data/'+fname)
    dta=csv.reader(f)
    for i,line in enumerate(dta):
        data.append(line)
    return data

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    print n, m ,m-h, m+h
    return m, m-h, m+h

def testCows(res):
    '''
    header=['gameid','person','condition','avg_user_choices','avg_bot_choices','gender','age','device']
    '''
    commons=[float(a[3]) for a in res if a[2]=='commons'] #list of average_user_choice if condition=='commons'
    lcommons=[float(a[3]) for a in res if a[2]=='leanCommons'] 
    lbarn=[float(a[3]) for a in res if a[2]=='leanBarn']
    barn=[float(a[3]) for a in res if a[2]=='barn']

    print 'Commons conf-int'
    vci=mean_confidence_interval(commons, confidence=0.95)
    print 'Lean Commons conf-int'
    tci=mean_confidence_interval(lcommons, confidence=0.95)
    print 'Lean Barn conf-int'
    bci=mean_confidence_interval(lbarn, confidence=0.95)
    print 'Barn conf-int'
    ntci=mean_confidence_interval(barn, confidence=0.95)
    print np.mean(commons),np.mean(lcommons),np.mean(lbarn),np.mean(barn)
    t,p=ttest_ind(commons,lcommons)
    print 'T-test for Commons vs. Lean Commons shows t = %f at p=%f for means of %f and %f' % (t,p,np.mean(commons),np.mean(lcommons))
    t,p=ttest_ind(lcommons,lbarn)
    print 'T-test for Lean Barn vs. Lean Commons shows t = %f at p=%f for means of %f and %f' % (t,p,np.mean(lbarn),np.mean(lcommons))
    t,p=ttest_ind(lbarn,barn)
    print 'T-test for Lean Barn vs. Barn shows t = %f at p=%f for means of %f and %f' % (t,p,np.mean(lbarn),np.mean(barn))
    t,p=ttest_ind(lcommons,barn)
    print 'T-test for Lean Common vs. Barn shows t = %f at p=%f for means of %f and %f' % (t,p,np.mean(lcommons),np.mean(barn))
    return



fname='Commons_Dilemma.csv'
data=importData(fname)
testCows(data)


#results,header=Cows_Clean_First_Round(cdata)   #results are consistent if you just use participants' choice in the first round.
#testCows(results)

#results,header=Cows_Clean_First_Experiment(cdata)
#testCows(results)
#results=totals(results)

'''
we didn't add the commons condition "[[u'0', u'0', u'0', u'3'], [u'0.25', u'0.25', u'0.25', u'0.25']]"
until 12/09/2015
'''
#
#
#
#for i,r in enumerate(results):
#    results[i][6]='_'.join(map(str,r[6]))
#
#fn='Clean_Data/Three_Cows.txt'
#with open(fn,'wb') as f:
#    f.write(','.join(header)+'\n')
#    for r in results:
#        f.write(','.join(map(str,r))+'\n')

#t,p=ttest_ind(cdf.reactTime[(cdf.congruent==1)&(cdf.correct==1)],cdf.reactTime[(cdf.congruent==0)&(cdf.correct==1)])

#easyCounts(cdata)

'''possible params
http://www.volunteerscience.com/data/81/?format=json&amt=include&pi=include&variables=all&awards=all&scores=all&sections=all&export_lastnum=5&start=07%2F09%2F2014+16%3A05&end=07%2F11%2F2014+12%3A04
('format','json') - json, xml
('amt','include') - include, exclude, only
('pi','exclude') - include, exclude, only
('start','01/01/2014')
('end','07/10/2014')
('export_lastnum','5') - export N-previous games (any number)
('sections','all') - includes the Demonstrations data.
('awards','all')
('scores','all')
('variables','all')
'''



