
# -*- coding: utf-8 -*-
'''
Created on Fri May 06 2016

@author: Jason Radford

Data collection was conducted from 11/21/2014 (or so) to 12/31/2015 (or so). The experimental conditions were changed in December 2015,
and the analysis should reflect this.

Steps:
Import Test data
Import Prior data
Do counts of subjects in test data (without including those in the not testify condition)
    - Individuals participating and Number of sessions.
    - Number of sessions consented to.
    - Number that are complete and subjects' first session
Analyze subjects first session.

'''

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
    '''
    Used for generating Figure 4
    '''
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    print n, m, m-h, m+h
    return m, m-h, m+h


def testPD(res):
    '''
    header=['gameid','person','condition','avg_user_choices','avg_bot_choices','gender','age','device']   
        
    '''
    testify=[float(a[3]) for a in res if a[2]=='testify']
    lnot=[float(a[3]) for a in res if a[2]=='leanNot']
    print 'Testify conf-int'
    vci=mean_confidence_interval(testify, confidence=0.95)
    print 'Lean Not Testify conf-int'
    bci=mean_confidence_interval(lnot, confidence=0.95)
    t,p=ttest_ind(testify,lnot)
    print 'T-test for Testify vs. Lean Not Testify shows t = %f at p=%f for means of %f and %f' % (t,p,np.mean(testify),np.mean(lnot))
    return



fname='Prisoners_Dilemma.csv'
data=importData(fname)
testPD(data)

#data=importTestData('Raw_Data/Prisoners_Dilemma.json')

#results,header=PD_Clean_First_Round(data)
#results=totals(results)
#testPD(results)

