'''
Code created to analyze the TSP data for the replication paper.  It is based on earlier, reporting code called TSPclean.py.

Date Created: January 14, 2015

'''
import csv
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde,ttest_ind,ttest_1samp
from matplotlib import pyplot as pp
import urllib
from httplib2 import Http
import datetime as dt
import json, ast, re
import random as rn
from collections import Counter
from scipy.stats.stats import pearsonr


def importData(fname):
    '''import cleaned csv data file. '''
    data=[]
    f=open('Clean_Data/'+fname)
    dta=csv.reader(f)
    for i,line in enumerate(dta):
        data.append(line)
    return data


def bootstrapTestTSP(data):
    scores=[float(line[2]) for i,line in enumerate(data[1:]) if line[2]!='' and line[3] not in ['']]# and line[7]!='0']
    hulls=[float(line[3]) for i,line in enumerate(data[1:]) if line[2]!='' and line[3] not in ['']]# and line[7]!='0']
    correct=[float(line[4]) for i,line in enumerate(data[1:]) if line[2]!='' and line[3] not in ['']]# and line[7]!='0']
    
        #set the sampling proportion to the smallest value    
    balance=Counter(hulls)
    mn=float(min(balance.values()))
    for k,v in balance.iteritems():
        balance[k]=mn/v
        
    #set the seed for replication purposes.
    rn.seed(1000)
    cors=[]
    for x in xrange(100):
        fcorrect=[]
        fhulls=[]
        for i,h in enumerate(hulls):    
            if rn.random()<balance[h]:
                fhulls.append(h)
                fcorrect.append(correct[i])
        #print pearsonr(fhulls,fcorrect)
        r,p=pearsonr(fhulls,fcorrect)
        cors.append(r)
    
    #run the one-sample t-test to determine if average estimated effect is not zero
    print np.mean(cors),ttest_1samp(cors,0.0)


    return cors

fname='TSP.csv'
data=importData(fname)
cors=bootstrapTestTSP(data)
