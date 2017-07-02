
'''
Completeness: 99% (complete, but not run)

Summary: This code takes the raw JSON and qualtrics csv data from the survey-based studies and merges them into
a raw csv file.  Note, the nonconsented users were excluded during the json dump script and so the
number of non-consents is not reported in this code.
'''


import json
import numpy as np
import datetime as dt
from matplotlib import pyplot as pp
import operator
import matplotlib.dates as ds
import os
import csv
import re

def getFiles(fname):
    fname='Dump_Data\\'+fname+'.json'
    print fname
    with open(fname,'rb') as f:
        a=f.read()
    data=json.loads(a)
    return data


def FilterData(data,name):
    ids=[]
    f=open('Survey Consents/'+name+'.csv')
    dta=csv.reader(f)
    for i,line in enumerate(dta):
        ids.append(line[0])
    
    
    cdata=[]
    nonconsents=0.0
    subjects=set()
    old=1
    out=[]
    fail=1.0
    count=1.0
    for line in data:
        if line['date'][0:7]==old:
            if s['consent']==False and uid not in ids:
                fail+=1
        else:
            old=line['date'][0:7]
            out.append([fail/count,count])
            fail=0.0
            count=0.0
        count+=1
        flag=0 
        for s in line['subjects']:
            uid=s['uid']
            subjects.update([uid])
            if s['consent']==False and uid not in ids: #if subject doesn't consent.
                nonconsents+=1
                flag=1
            else:
                if 'age-bin' in s.keys(): #if no age-bin, then person is not logged in with an account.
                    if s['age-bin']<3:      #if age<3, they are under 18 and cannot consent.
                        flag=1
                        nonconsents+=1
        if flag==0:
            cdata.append(line)
    out.append([fail/count,count])
    #print out
    return cdata

def getids(data):
    '''
    Gets the list of gameids and userids from consented experiments in order filter out the non-consented data in
    the extractData() and cleanBigFive() functions.
    '''
    userdict={}
    for line in data:
        for s in line['subjects']:
            userdict[str(line['id'])]=s['uid']
    return userdict


def writeCleanData(results,outfile=''):
    newfile='Raw_Data/'+outfile+'.csv'
    with open(newfile,'wb') as f:
        writeit=csv.writer(f)
        for row in results:
            writeit.writerow(row)
    return


def extractData(dfile,idDict,qids,outfile):
    '''
    applies to all but the Big Five where the qids are handled differently.
    '''
    count=dict(zip(idDict.values(),[0 for z in xrange(len(idDict))]))
    
    questions={}
    results=[]
    varids={}
    header=[]
    nonConsent=0.0
    with open(dfile,'rb') as f:
        data=csv.reader(f)
        for i,row in enumerate(data):
            if i==0:
                for j,item in enumerate(row):
                    if item in qids:  
                        nitem=''.join(re.findall(r"[\d']+",item))
                        varids[j]=nitem
                        header.append(nitem)
                    if item=='testId':
                        varids[j]=item
                        header.append(item)
                    if item=='V8': #StartDate
                        start=j
                    if item=='V9': #EndDate
                        end=j
                header.append('timeSpent')
                header.append('uid')
                results.append(header)
            elif i==1:
                for j,item in enumerate(row):
                    if j in varids.keys():
                        questions[varids[j]]=item #text
            else:
                result=[r.replace(',','') for j,r in enumerate(row) if j in varids.keys()]
                st=dt.datetime.strptime(row[start],"%Y-%m-%d %H:%M:%S")
                ed=dt.datetime.strptime(row[end],"%Y-%m-%d %H:%M:%S")
                tot=ed-st
                result.append(tot.seconds)  #append total time spent on survey in seconds
                if result[0] != '' and result[0] in idDict.keys():
                    result.append(idDict[result[0]])
                    results.append(result)
                elif result[0] !='':
                    nonConsent+=1
    print outfile, '- number of original cases = ',i-1
    #print outfile, '- number of original unique individuals = ',len(subjects)
    print outfile,' - number excluded for nonconsents = ',  nonConsent, round(nonConsent/(i-1),3), 'percent'
    print outfile, '- number of remaining cases = ',len(results)-1, round((len(results)-1)/float(i-1),3), 'percent'
   
    writeCleanData(results,outfile)
    
    return questions, results


def cleanBigFive(dfile,idDict):
    '''
    Input:
        dfile is the location of the big five csv file.
        idDict is the dictionary of VS-based data for what data is eligible for publication
    
    Output:
        csv file of clean data.
    '''
    questions={}
    results=[]
    varids={}
    header=[]
    nonConsent=0.0
    with open(dfile,'rb') as f:
        data=csv.reader(f)
        for i,row in enumerate(data):
            #identifies the header information
            if i==0:
                for j,item in enumerate(row):
                    if item.startswith('BFI'):  
                        nitem=re.findall(r"[\d']+",item)[0]
                        varids[j]=nitem
                        header.append(nitem)
                    if item=='testId':
                        varids[j]=item
                        header.append(item)
                    if item=='V8': #StartDate
                        start=j
                    if item=='V9': #EndDate
                        end=j
                
                header.append('timeSpent')
                header.append('uid')
                results.append(header)
            elif i==1:
                #get question phrasing
                for j,item in enumerate(row):
                    if j in varids.keys():
                        text=item.split('-')[len(item.split('-'))-1]
                        questions[varids[j]]=text.lstrip().rstrip().lower()
            else:
                result=[r for j,r in enumerate(row) if j in varids.keys()]
                start_time=dt.datetime.strptime(row[start],"%Y-%m-%d %H:%M:%S")
                end_time=dt.datetime.strptime(row[end],"%Y-%m-%d %H:%M:%S")
                time_spent=end_time-start_time
                result.append(time_spent.seconds)  #append total time spent on survey in seconds
                if result[0] != '' and result[0] in idDict.keys(): #result[0] only works if testid is the first variable picked out in enumerate(row)
                    result.append(idDict[result[0]])        #adding the uid.
                    results.append(result)                  #appending data to final data.
                elif result[0] !='':
                    nonConsent+=1
    
    outfile='BigFive'
    writeCleanData(results,outfile)
    print outfile, '- number of original cases = ',i-1
    #print outfile, '- number of original unique individuals = ',len(non)
    print outfile,' - number excluded for nonconsents = ',  nonConsent, round(nonConsent/(i-1),3), 'percent'
    print outfile, '- number of remaining cases = ',len(results)-1, round((len(results)-1)/float(i-1),3), 'percent'
   
    return questions,results#,nonConsent#newquestions,valids


def handler(path,dfile,ids):
    '''This code uses the file names of the csv to detect the survey being analyzed and exracts the cleaned data '''
    if "big" in dfile.lower() and 'five' in dfile.lower():
        return(cleanBigFive(path+'\\'+dfile,ids))
    
    if "africa" in dfile.lower():
        qids=['Q1','Q2','Q3']
        return(extractData(path+'\\'+dfile,ids,qids,'Anchoring_Africa'))
    
    if "trees" in dfile.lower():
        qids=['Q1','Q2','Q3']
        return(extractData(path+'\\'+dfile,ids,qids,'Anchoring_Trees'))
    
    if "disease" in dfile.lower():
        qids=['Q1','Q2']
        return(extractData(path+'\\'+dfile,ids,qids,'Disease_Problem'))
    
    if 'timed' in dfile.lower()and 'risk' in dfile.lower():
        qids=['Q4_1','Q6_1','Q8_1','Q10_1','Q14_1','Q16_1','Q18_1','Q20_1']
        return(extractData(path+'\\'+dfile,ids,qids,'Timed_Risk_Reward'))
    
    if 'vignette' in dfile.lower():
        qids=['Q12','Q4']
        return(extractData(path+'\\'+dfile,ids,qids,'JW_Vignette'))
    
    if 'protestant' in dfile.lower():
        qids=['Q1_1','Q1_2','Q1_3','Q1_4','Q1_5','Q1_6','Q1_7','Q1_8','Q1_9','Q1_10','Q1_11','Q1_12','Q1_13','Q1_14','Q1_15','Q1_16']
        return(extractData(path+'\\'+dfile,ids,qids,'JW_PWE'))
    
    if 'system' in dfile.lower() and 'just' in dfile.lower():
        qids=['Q1_1','Q1_2','Q1_3','Q1_4','Q1_5','Q1_6','Q1_7','Q1_8']
        return(extractData(path+'\\'+dfile,ids,qids,'JW_System_Justification'))
    
    if 'six' in dfile.lower() and 'figures' in dfile.lower():
        qids=['Q2_1','Q2_2','Q2_3','Q2_4','Q2_5','Q2_6','Q5','Q6','Q7','Q8','Q9_1','Q9_2','Q9_3','Q9_4','Q9_5','Q9_6']
        return(extractData(path+'\\'+dfile,ids,qids,'Six_Figures'))



experiments=['TSP','All_TSP','Commons_Dilemma','Flanker','JW_Reaction_Time','Prisoners_Dilemma','Stroop']

path='Dump_Data'
ids={}
#iterate through dumped data and get ids for everyone.
for f in os.listdir(path):
    #if 'random' not in f.lower():
    #    continue
    if '.json' in f:
        name=f.split('.')[0]
        if name in experiments:
            continue
        data=getFiles(name)
        data=FilterData(data,name)
        ids.update(getids(data))
                
for dfile in os.listdir(path):
    if '.csv' not in dfile:
        continue
    print dfile
    questions, results=handler(path,dfile,ids)
    
