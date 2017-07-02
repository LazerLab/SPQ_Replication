
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde,ttest_ind
from matplotlib import pyplot as pp

def importCleanData(fname):
    cdf=pd.read_csv(fname)
    cdf.replace('',np.nan,inplace=True)

    return cdf



def plotKDE(cdf):
    '''
    takes the panda data and creates a plot of the distributions.
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
    pp.hist(list(cdf.reactTime[(cdf.congruent==1)&(cdf.correct==1)&(cdf.reactTime<mx)]),normed=1,hatch='x',color='#7D7D7D',alpha=.2,label='congruent')
    pp.hist(list(cdf.reactTime[(cdf.congruent==0)&(cdf.correct==1)&(cdf.reactTime<mx)]),normed=1,hatch='o',color='#7D7D7D',alpha=.2,label='incongruent')
    pp.xlabel('Reaction time (milliseconds)')
    pp.ylabel('Kernel Density')
    pp.title('Reaction Times for Stroop Test')
    pp.legend()
    pp.savefig('Images/Fig_2_Stroop.jpg')
    return


fname='Clean_Data/Stroop.csv'
cdf=importCleanData(fname)
#cdf,cdata=cleanFlanker(data)
#easyCounts(data)


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
print 'Pre-Exclusion T-test for Stroop shows t = %f at p=%f' % (t,p)
t,p=ttest_ind(cdf.reactTime[(cdf.congruent==1)&(cdf.correct==1)&(cdf.reactTime<outlier_cut)],cdf.reactTime[(cdf.congruent==0)&(cdf.correct==1)&(cdf.reactTime<outlier_cut)])
print 'T-test for Stroop shows t = %f at p=%f' % (t,p)
