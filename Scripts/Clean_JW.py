#justicia Analysis

import urllib
import httplib2
import os, csv, json
import datetime as dt
import cPickle
import pandas as pd
import numpy as np


def importJSONData(fname):
    with open(fname,'rb') as f:
        a=f.read()
    data=json.loads(a)
    return data

def importCSVData(fname):
    data=[]
    f=open(fname,'rb')
    dta=csv.reader(f)
    for line in dta:
        data.append(line)
    return data


def easyCounts(data,badFaith={}):
    '''
    badFaith is calculated in cleanFlanker as the dict
    '''
    idx=[i for i,line in enumerate(data) if line['subjects'][0]['consent']!=False]
    players=[line['subjects'][0]['uid'] for i,line in enumerate(data) if str(line['subjects'][0]['uid'])!='0']
    nonConsents=len(data)-len(idx)
    consents=len(idx)
    total=len(data)
    #NumValidRounds=sum([len(data[i]['submissions'])-2 for i in idx])
    print 'Total Games = ', total
    print 'Total Unique Participants =', len(set(players))
    print "Number of Consented Games", consents, " by percent: ", consents/float(total)
    print "Number of Non-Consented",nonConsents, " by percent: ", nonConsents/float(total)
    #print "Total Number of rounds in %s = %d" % (game,NumValidRounds)

    ids=[]
    completions=0.0
    for i,line in enumerate(data):
        if i in idx:
            if sum([d['round']>100 for d in line['submissions']])==10:
                completions+=1
            
            for s in line['subjects']:
                if 'uid' in s.keys():
                    ids.append(s['uid'])
    
    updateData=[total,consents,nonConsents,0,completions,sum(badFaith.values()),str(badFaith)]
    updateQualityData(updateData,game='flanker')
    
    NumParticipants=len(set(ids))
    print "Number of Unique Participants",NumParticipants
    #results=[NumNonConsentGames,numValidGames,NumValidRounds,NumParticipants]
    return #results
    
    
def cleanRT(data):
    '''Takes raw data and generates a flat-file structure of person-id-submissions '''
    cdata=[]
    subTranslate={'desktop':1,'smart_phone':2,'tablet':3,'male':1,'female':0}
    badFaith={'inaccurate65%':0.0}
    mobile=0.0
    cdata.append(['gameid','uid','age','gender','device','round','reactTime','nonword','justiceWord','correct','NumChars','accuracy','rounds'])
    for line in data:
        if line['submissions']==[]:
            continue
        gameid=line['id']
        person=line['subjects'][0]['uid']
	
        try:
            gender=subTranslate[line['subjects'][0]['gender']]
        except:
            gender=''
        try:
            age=int(line['subjects'][0]['age-bin'])
        except:
            age=''
        try:
            device=subTranslate[line['subjects'][0]['device']]
        except:
            device=''
	
	if device == 2 or device==3:
	    mobile+=1
	    continue
	    
	
	gdata=[]
        bftest=0.0
        count=0.0
	for sub in line['submissions']:
	    if sub['round']>99 and len(sub)>0:
		word=sub['val']['reaction']['word'].lower()
		
		#PRACTICE ROUND
                if word in ['pencil','penicl','lesson','pattern','graet','python','zpiper','comes','hosue','tarits']:
                    continue
                
		count+=1
                rnd=sub['round']
		letters=len(word)
                if word in ["fair", "legitimate", "just", "valid", "justified"]:
                    justiceWord=1
                else:
                    justiceWord=0
                if word in ["fair", "legitimate", "just", "valid", "justified","ladder","school","hostile","close","emperor"]:
                    nonword=0
                
                elif word in ["hugner", "divroce", "grbabing", "kcik", "ahce", "drnoe", 
				 "divnie", "horziontal", "dowcnast", "buoncy", "shkae", "dzoen",
				 "dynatsy", "pinwehel", "femrent", "natsy", "dveout", "cranbrery", 
				 "anaylze", "trhust", "dynaimc", "spriit", "robebr", "heartbaet",
				 "mtoh", "glmimer", "alolw", "dmeolish", "furoius", "amtaeur",
				 "exrteme", "cirlce", "decdaence", "lsuter", "tcatical", "caeml"]:
                    nonword=1
		else:
		    print 'word not found ', word
                reactTime=int(sub['val']['reaction']['reaction'])
                correct=sub['val']['reaction']['correct']
                if correct=='true':
                    correct=1
                else:
                    correct=0
            
                bftest+=correct
                gdata.append([gameid,person,age,gender,device,rnd,reactTime,nonword,justiceWord,correct, letters])#+['' for i in userdict.values()[0]]+['',''])
                names=['gameid','person','age','gender','device','round','reactTime','nonword','justiceWord','correct','NumChars','accuracy','rounds']
        
	#calculate accuracy and exclude cases where accuracy is below 65%
	if count==15:
            if bftest/count<=.65:
                badFaith['inaccurate65%']+=1
		continue
	
	#add accuracy and number of rounds variable variable
	for i,row in enumerate(gdata):
	    gdata[i]+=[bftest/count,count]
	cdata=cdata+gdata    
        
    print 'Just World number mobile exclusions = ', mobile, round(mobile/len(data),3)*100, 'percent'
    cdf=pd.DataFrame(cdata,columns=names)
    cdf.replace('',np.nan,inplace=True)
    return cdf,cdata


fname='Raw_Data/JW_Reaction_Time.json'
data=importJSONData(fname)

#the first three cases are test cases
cdf,cdata=cleanRT(data[3:])

#Import Survey Data
PWC=importCSVData('Raw_Data/JW_PWE.csv')
VIG=importCSVData('Raw_Data/JW_Vignette.csv')
SJ=importCSVData('Raw_Data/JW_System_Justification.csv')


#Collate Respondents across individual tasks
Users=set([v[4] for i,v in enumerate(VIG) if i>0])
Users=dict([(u,{'vig':set(),'sj':set(),'pwc':set(),'timed':set()}) for u in Users])

for i,row in enumerate(VIG):
    if i>0:
        Users[row[4]]['vig'].update([row[0]])
    
for i,row in enumerate(cdata):
    if i>0:
        if row[1] in Users.keys():
            Users[row[1]]['timed'].update([row[0]])
        else:
            continue#print 'found new user in Timing ', row[1]

for i,row in enumerate(PWC):
    if i>0:
        if row[18] in Users.keys():
            Users[row[18]]['pwc'].update([row[0]])
        else:
            print 'found new user in PWC ', row[18]


for i,row in enumerate(SJ):
    if i>0:
        if row[10] in Users.keys():
            Users[row[10]]['sj'].update([row[0]])
        else:
            print  'found new user in SJ ', row[10]

#Find users who did not complete all four tasks
incompletes=0
topop=[]
for u,k in Users.iteritems():
    if 0 in map(len,k.values()):
        incompletes+=1
        topop.append(u)
for u in topop:
    Users.pop(u)

print 'number of unique users who completed all four tasks = ', len(Users)


UserChains={}
count=0
for uid,val in Users.iteritems():
    maxgames=len(val['vig'])
    init=sorted(list(val['vig']))
    first=init[0]
    if len(init)>1:
	other=init[1]
    else:
	other=100000
    chain={}
    timeid=''
    pwcid=''
    sjid=''
    #vigid=init[i]
    for gid in sorted(val['timed']):
	if timeid=='' and int(gid)>int(first) and int(other)>int(gid):    #take the first ID unless that ID is larger than the users' second Vignette ID (i.e. multiple participation)
	    timeid=gid
    if timeid=='':
	#person didn't take timed lexical task. Skip them. 
	continue
    for gid in sorted(val['sj']):
	if sjid=='' and int(gid)>int(first) and int(gid)>int(timeid) and int(other)>int(gid):    #take the first larger ID
	    sjid=gid
    if sjid=='':
	#person didn't complete System Justification survey task. Skip them.
	continue
    for gid in sorted(val['pwc']):
	if pwcid=='' and int(gid)>int(first) and int(gid)>int(timeid) and int(other)>int(gid):    #take the first larger ID
	    pwcid=gid
    if pwcid=='':
	#person didn't complete Protestant Work Ethic survey. Skip them.
	continue
    chain[count]=[first,timeid,sjid,pwcid]
    UserChains[uid]=chain
    count+=1

print 'number of unique users who completed all four tasks on their first try = ', len(UserChains)

    
#Now to put the chainID back into the data
for i,row in enumerate(VIG):
    if i==0:
        VIG[i].append('chain')
    if i>0:
        VIG[i].append('')   #makes this default to missing
        if row[4] not in UserChains.keys():
            continue
        for num,chain in UserChains[row[4]].iteritems():
            if row[0] in chain:
                VIG[i][len(row)-1]=str(num)

fn='Clean_Data/JW_Vignette.txt'
with open(fn,'wb') as f:
    for r in VIG:
        f.write(','.join(map(str,r))+'\n')

for i,row in enumerate(SJ):
    if i==0:
        SJ[i].append('chain')
    if i>0:
        SJ[i].append('')   #makes this default to missing
        if row[10] not in UserChains.keys():
            continue
        for num,chain in UserChains[row[10]].iteritems():
            if row[0] in chain:
                SJ[i][len(row)-1]=str(num)


fn='Clean_Data/JW_System_Justification.txt'
with open(fn,'wb') as f:
    for r in SJ:
        f.write(','.join(map(str,r))+'\n')


for i,row in enumerate(PWC):
    if i==0:
        PWC[i].append('chain')
    if i>0:
        PWC[i].append('')   #makes this default to missing
        if row[18] not in UserChains.keys():
            continue
        for num,chain in UserChains[row[18]].iteritems():
            if row[0] in chain:
                PWC[i][len(row)-1]=str(num)


fn='Clean_Data/JW_PWE.txt'
with open(fn,'wb') as f:
    for r in PWC:
        f.write(','.join(map(str,r))+'\n')


for i,row in enumerate(cdata):
    if i==0:
        cdata[i].append('chain')
    if i>0:
        cdata[i].append('')   #makes this default to missing
        if row[1] not in UserChains.keys():
            continue
        for num,chain in UserChains[row[1]].iteritems():
            if row[0] in chain:
                cdata[i][len(row)-1]=str(num)


fn='Clean_Data/JW_Reaction_Time.txt'
with open(fn,'wb') as f:
    for r in cdata:
        f.write(','.join(map(str,r))+'\n')



   
    

