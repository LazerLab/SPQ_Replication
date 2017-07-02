import os, csv, json
import datetime as dt
import cPickle
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde,ttest_ind
from matplotlib import pyplot as pp
import urllib
from httplib2 import Http


def importData(fname):
    with open(fname,'rb') as f:
        a=f.read()
    data=json.loads(a)
    return data

def writeCleanData(output,outfile=''):
    '''
    This takes the clean data file and writes it to the Clean_Data folder
    Input:
        output = [[observation 1],[observation 2]...[observation n]]
        outfile = "name to save file to" (e.g. "BigFive")
    Output:
        None
    '''
    newfile='Clean_Data/'+outfile+'.csv'
    with open(newfile,'wb') as f:
        writeit=csv.writer(f)
        for row in output:
            writeit.writerow(row)
    
    return


def cleanFlanker(data):
    '''Takes raw json data and generates a flat-file structure of person-id-submissions '''
    colorDict={'#FFFF00':'yellow','#FF0000':'red','#00CC00':'green','#0000FF':'blue'}
    cdata=[]
    badFaith={'inaccurate65%':0.0}
    incompletes=0.0
    repeats=0.0
    subjects=set()
    for line in data:
        #check for incompletes
        if line['submissions']==[]:
            continue
        
        #check for non-consents
        if line['subjects'][0]['consent']==False:
            continue
        
        #check for repeats
        uid=line['subjects'][0]['uid']
        if uid not in subjects:
            subjects.update([uid])
        else:
            repeats+=1
            continue
        
        #metadata
        gameid=line['id']
        uid=line['subjects'][0]['uid']
        round_data=[]
        bftest=0.0
        count=0.0
        for sub in line['submissions']:
            if sub['round']>99 and len(sub)>0:
                count+=1
                rnd=sub['round']
                reactTime=int(sub['val']['reaction']['reaction'])
                target= sub['val']['reaction']['word'][2].lower()
                stimulus=sub['val']['reaction']['word'].lower()
                guess=sub['val']['reaction']['answer'].lower()
                congruent= int(target==stimulus[0])
                near= int(target in guess)  #is there evidence the person input the right answer but mistyped some of it.
                correct=int(target==guess)  #is guess correct
                bftest+=correct
                round_data.append([gameid,uid,rnd,reactTime,target,guess,congruent,near,correct])
                
        
        #how many did subject get incorrect?  Exclude those who do worse than 65%
        if count==10:
            accuracy=bftest/count
            if accuracy<=.65:
                badFaith['inaccurate65%']+=1
            
            #add round data and accuracy to full data set
            else:
                for r in round_data:
                    cdata.append(r+[accuracy])
        else:
            incompletes+=1
        
        names=['gameid','uid','round','reactTime', 'color', 'guess', 'congruent', 'near', 'correct','accuracy']
                
    print 'Flanker - number of original games = ', len(data)
    print 'Flanker - number excluded for repeat = ', repeats, round(repeats/len(data),3)*100, 'percent'
    print 'Flanker - number excluded for inaccuracy = ', sum(badFaith.values()),round(sum(badFaith.values())/len(data),3)*100, 'percent'
    print 'Flanker - number excluded for incompleteness = ', incompletes, round(incompletes/len(data),3)*100, 'percent'
    print 'Flanker - number of final cases in the analysis = ', len(cdata),'rounds and ', len(set([c[0] for c in cdata])),' games'
    #cdata=totals(cdata)
    cdata=[names]+cdata
    writeCleanData(cdata,outfile='Flanker')
    return cdata

data=importData('Raw_Data/Flanker.json')
cdata=cleanFlanker(data)


'''
#post tests
scatter(cdf.age,cdf.reactTime)
cdf.age.corr(cdf.reactTime)
'''
