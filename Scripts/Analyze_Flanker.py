import os, csv, json
import datetime as dt
import cPickle
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde,ttest_ind
from matplotlib import pyplot as pp
import urllib
from httplib2 import Http


def importCleanData(fname):
    cdf=pd.read_csv(fname)
    cdf.replace('',np.nan,inplace=True)
    #with open(fname,'rb') as f:
    #    data=csv.reader(f)
    #    for i,row in enumerate(data):
    #        cdata.append(data)
    #data=json.load(a)
    return cdf
#
#def writeCleanData(output,outfile=''):
#    '''
#    This takes the clean data file and writes it to the Clean_Data folder
#    Input:
#        output = [[observation 1],[observation 2]...[observation n]]
#        outfile = "name to save file to" (e.g. "BigFive")
#    Output:
#        None
#    '''
#    newfile='Clean_Data/'+outfile+'.csv'
#    with open(newfile,'wb') as f:
#        writeit=csv.writer(f)
#        for row in output:
#            writeit.writerow(row)
#    
#    return


def plotKDE(cdf):
    '''
    Generates Figure 2 for Flanker
    '''
    #get data
    mx=np.mean(cdf.reactTime)+np.std(cdf.reactTime)*3
    cons=map(float,cdf.reactTime[(cdf.congruent==1)&(cdf.correct==1)&(cdf.reactTime<mx)])
    incons=map(float,cdf.reactTime[(cdf.congruent==0)&(cdf.correct==1)&(cdf.reactTime<mx)])
    
    #Transform data by KDE
    consd = gaussian_kde(cons)
    #consd.covariance_factor = lambda : .25
    #consd._compute_covariance()
    
    inconsd = gaussian_kde(incons)
    #inconsd.covariance_factor = lambda : .25
    #inconsd._compute_covariance()
    
    #plotting parameters
    mn=min([min(cons),min(incons)])
    mx=max([max(cons),max(incons)])
    fakeX=np.arange(mn-mn*.1,mx+mx*.1,10)
    cony=consd(fakeX)
    
    incony=inconsd(fakeX)
    pp.figure()
    pp.xlim((mn,mx))
    pp.plot(fakeX,cony,'#7D7D7D')
    pp.plot(fakeX,incony,'#7D7D7D')
    pp.hist(list(cdf.reactTime[(cdf.congruent==1)&(cdf.correct==1)&(cdf.reactTime<mx)]),bins=30,normed=1,hatch='x',color='#7D7D7D',alpha=.2,label='congruent')
    pp.hist(list(cdf.reactTime[(cdf.congruent==0)&(cdf.correct==1)&(cdf.reactTime<mx)]),bins=30,normed=1,hatch='o',color='#7D7D7D',alpha=.2,label='incongruent')
    pp.xlabel('Reaction time (milliseconds)')
    pp.ylabel('Kernel Density')
    pp.title('Reaction Times for Flanker Test')
    pp.legend()
    pp.savefig('Images/Fig_2_Flanker.jpg')
    #pp.show()
    return

fname='Clean_Data/Flanker.csv'
cdf=importCleanData(fname)

outlier_cut=np.mean(cdf.reactTime)+np.std(cdf.reactTime)*3

print 'Pre-Exclusion Reaction Time for Correct Congruents was ',np.mean(cdf.reactTime[(cdf.congruent==1)&(cdf.correct==1)])
print 'Pre-Exclusion Reaction Time for Correct Incongruents was ', np.mean(cdf.reactTime[(cdf.congruent==0)&(cdf.correct==1)])
print 'Exclusion Reaction Time for Correct Congruents was ',np.mean(cdf.reactTime[(cdf.congruent==1)&(cdf.correct==1)&(cdf.reactTime<outlier_cut)])
print 'Exclusion Reaction Time for Correct Incongruents was ', np.mean(cdf.reactTime[(cdf.congruent==0)&(cdf.correct==1)&(cdf.reactTime<outlier_cut)])
print 'Exclusion Reaction Time Std for Correct Congruents was ',np.std(cdf.reactTime[(cdf.congruent==1)&(cdf.correct==1)&(cdf.reactTime<outlier_cut)])
print 'Exclusion Reaction Time Std for Correct Incongruents was ', np.std(cdf.reactTime[(cdf.congruent==0)&(cdf.correct==1)&(cdf.reactTime<outlier_cut)])
print 'Exclusion Mean Inaccuracy for Congruents was ',1-np.mean(cdf.correct[(cdf.congruent==1)&(cdf.reactTime<outlier_cut)])
print 'Exclusion Mean Inaccuracy for Incongruents was ', 1-np.mean(cdf.correct[(cdf.congruent==0)&(cdf.reactTime<outlier_cut)])
print 'Error Rate for Excluded Congruents was ', 1-(np.sum(cdf.correct[(cdf.congruent==1)&(cdf.reactTime<outlier_cut)])/float(len(cdf.correct[(cdf.congruent==1)&(cdf.reactTime<outlier_cut)])))
print 'Error Rate for Excluded Incongruents was ', 1-(np.sum(cdf.correct[(cdf.congruent==0)&(cdf.reactTime<outlier_cut)])/float(len(cdf.correct[(cdf.congruent==0)&(cdf.reactTime<outlier_cut)])))



plotKDE(cdf)
t,p=ttest_ind(cdf.reactTime[(cdf.congruent==1)&(cdf.correct==1)],cdf.reactTime[(cdf.congruent==0)&(cdf.correct==1)])
print 'Pre-Outlier-Exclusion T-test for Flanker shows t = %f at p=%f' % (t,p)
t,p=ttest_ind(cdf.reactTime[(cdf.congruent==1)&(cdf.correct==1)&(cdf.reactTime<outlier_cut)],cdf.reactTime[(cdf.congruent==0)&(cdf.correct==1)&(cdf.reactTime<outlier_cut)])
print 'Outliers Excluded T-test for Flanker shows t = %f at p=%f' % (t,p)





'''
#post tests
scatter(cdf.age,cdf.reactTime)
cdf.age.corr(cdf.reactTime)
'''
