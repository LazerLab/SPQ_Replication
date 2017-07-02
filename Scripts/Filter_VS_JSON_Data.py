'''
Filter_VS_Survey_Data.py
completeness = 99% (complete code, not yet tested)
This code calls the VS json data and filters out the nonconsents and multiplayer versions of games,
storing the resulting json data in the Raw_Data folder

'''

import os
import json


def getFiles(fname):
    fname='Dump_Data\\'+fname+'.json'
    print fname
    with open(fname,'rb') as f:
        a=f.read()
    data=json.loads(a)
    if type(data)==dict:
        return data['tests']
    else:
        return data

def writeFilteredData(data,name):
    with open('Raw_Data/'+name+'.json','wb') as f:
        json.dump(data,f)
    return
    

def FilterData(data,name):
    cdata=[]
    nonconsents=0.0
    subjects=set()
    for line in data:
        flag=0 
        for s in line['subjects']:
            subjects.update([s['uid']])
            if s['consent']==False: #if subject doesn't consent.
                nonconsents+=1
                flag=1
            else:
                if 'age-bin' in s.keys(): #if no age-bin, then person is not logged in with an account.
                    if s['age-bin']<3:      #if age<3, they are under 18 and cannot consent.
                        flag=1
                        nonconsents+=1
        if flag==0:
            cdata.append(line)

    print name, '- number of original cases = ',len(data)
    print name, '- number of original unique individuals = ',len(subjects)
    print name,'-  number excluded for nonconsents = ',  nonconsents, round(nonconsents/len(data),3), 'percent'
    print name, '- number of remaining cases = ',len(cdata)
    return cdata

experiments=['TSP']#,'Commons_Dilemma','Flanker','JW_Reaction_Time','Prisoners_Dilemma','Stroop']
for exp in experiments:
    print 'doing ',exp
    data=getFiles(exp)
    cdata=FilterData(data,exp)
    writeFilteredData(cdata,exp)


