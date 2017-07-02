import os
import csv  
import datetime as dt
import urllib
from httplib2 import Http
import json
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde,ttest_ind
from matplotlib import pyplot as pp
import cPickle



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


def cleanStroop(data):
    '''Takes raw data and generates a flat-file structure of person-id-submissions '''
    colorDict={'#FFFF00':'yellow','#FF0000':'red','#008000':'green','#00CC00':'green','#0000FF':'blue'}
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
        person=line['subjects'][0]['uid']
        round_data=[]
        bftest=0.0  #here we perform the bad faith test(s). In this case, those who perfrom super-poorly
        count=0.0
        for sub in line['submissions']:    
            if sub['round']>99 and len(sub)>0:
                count+=1
                rnd=sub['round']
                reactTime=int(sub['val']['reaction']['reaction'])
                word= sub['val']['reaction']['word'].lower()
                col= colorDict[sub['val']['reaction']['color']]
                guess=sub['val']['reaction']['answer'].lower()
                congruent= int(word==col)
                if len(guess)>0:
                    near= int(guess[0]==col[0])
                else:
                    near=0
                correct=int(col==guess)
                bftest+=correct
                cdata.append([gameid,person,rnd,reactTime,col,guess,congruent,near,correct])
                #cdata.append([gameid,person,age,gender,device,rnd,reactTime,target,guess,congruent,near,correct])#+['' for i in userdict.values()[0]]+['',''])
                #if person in userdict.keys():
                #    print 'found', person
                #    +userdict[person])
                #else:
                #    cdata.append([gameid,person,age,gender,device,rnd,reactTime,target,guess,congruent,near,correct]+['' for i in userdict.values()[0]])
                
        if count==10:
            accuracy=bftest/count
            if accuracy<=.65:
                badFaith['inaccurate65%']+=1
            #if accuracy not below 65% and completed all tne rounds add round data and accuracy to full data set
            else:
                for r in round_data:
                    cdata.append(r+[accuracy])
        else:
            incompletes+=1
                
        
        names=['gameid','person','round','reactTime', 'color', 'guess', 'congruent', 'near', 'correct','accuracy']
        
    print 'Stroop - number of original games = ', len(data)
    print 'Stroop - number excluded for repeat = ', repeats, round(repeats/len(data),3)*100, 'percent'
    print 'Stroop - number excluded for inaccuracy = ', sum(badFaith.values()),round(sum(badFaith.values())/len(data),3)*100, 'percent'
    print 'Stroop - number excluded for incompleteness = ', incompletes, round(incompletes/len(data),3)*100, 'percent'
    print 'Stroop - number of final cases in the analysis = ', len(cdata),'rounds and ', len(set([c[0] for c in cdata])),' games'
    #cdata=totals(cdata)
    cdata=[names]+cdata
    writeCleanData(cdata,outfile='Stroop')
    return cdata


data=importData('Raw_Data/Stroop.json')
cdata=cleanStroop(data)


'''
#post tests
scatter(cdf.age,cdf.reactTime)
cdf.age.corr(cdf.reactTime)
'''