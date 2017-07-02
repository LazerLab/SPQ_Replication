
# -*- coding: utf-8 -*-
'''
Created on Fri May 06 2016

@author: Jason Radford

'''


#The goal of this script is to produce this file:
#userid, demo1,demo2,GAME1,GAME2,game3,game4,survey1,survey2...
#af234i3, male,age5,yes,no,yes,no,no,no
import datetime as dt
import urllib
import httplib2
import json
import pandas as pd
import numpy as np
import operator
import cPickle
import csv

def urlConstruct(params,gameNum):
    tok='9eb10bd50a56c89825ab6bcccffb76ebd81b0d62'
    url='http://volunteerscience.com/data/'+gameNum+'/?format=json&'+urllib.urlencode(params)+'&token='+tok
    client=httplib2.Http(disable_ssl_certificate_validation=True)
    content = client.request(url,method='GET',body='')
    data = json.loads(content[1])['tests']
    return data


def users(experiment,Users,name='Title'):
    players=[]
    for game in experiment:
        for subject in game['subjects']:
            if 'uid' in subject.keys() and subject['uid']!=0:
                uid=subject['uid'].strip()
                players.append(uid)
                subject.update({'game':name})
                if uid not in Users.keys():
                    Users[uid]={}
                    Users[uid]['demography']=[subject]
                else:
                    Users[uid]['demography'].append(subject)
                    #except: Users[uid]['demography']=[subject['device'],subject['locale']]
    return players, Users

def MakeUserFile(Users,Players):
    for name, players in Players.iteritems():
        for uid in players:
            Users[uid][name]=sum([uid==p for p in players])
    #for uid,dataDict in Users.iteritems():
    #    Users[uid].update(dict([(game,sum([uid==p for p in ps])) for game,ps in Players.iteritems()]))
    return Users

def ParticipationReport(Users):
    '''creates demographic summary and multi-game player counts
    challenge is handling changes to subject info - e.g. device , locale
    '''
    uniques={}
    totals={}
    demographics={'count':0}
    for uid,dataDict in Users.iteritems():
        demographics['count']+=1
        demographics[uid]={}
        uniques[uid]=0
        totals[uid]=0
        for ks,vs in dataDict.iteritems():
            if ks=='demography':
                for game in vs:
                    for k,v in game.iteritems():
                        if k not in demographics[uid].keys():
                            demographics[uid][k]={}
                            demographics[uid][k][v]=1
                        else:
                            if v in demographics[uid][k].keys():
                                demographics[uid][k][v]+=1
                            else:
                                demographics[uid][k][v]=1
            else:
                totals[uid]+=vs
                if vs>0:
                    uniques[uid]+=1
    return demographics,uniques,totals

def flatten(demographics,uniques, totals):
    '''This code takes the demographics data and restructures it into a dictionary used to call participant-level data.
    '''
    row={}
    row['header']=['uid','gender','age','locale','desktop','phone','tablet','consents','totgames','uniquegames','consentedGames','unconsentedGames']
    for idx, dat in demographics.iteritems():
        if idx!='count' and idx!=0:
            if 'gender' in dat.keys():
                gender=sorted(dat['gender'].items(), key=operator.itemgetter(1),reverse=True)[0][0]
            else:
                gender=''
            if 'age-bin' in dat.keys():
                age=sorted(dat['age-bin'].items(), key=operator.itemgetter(1),reverse=True)[0][0]
            else:
                age=''
            if 'locale' in dat.keys():
                loc=sorted(dat['locale'].items(), key=operator.itemgetter(1),reverse=True)[0][0]
            else:
                loc=''
            if 'device' not in dat.keys():
                desk=''
                phone=''
                tablet=''
            else:
                if 'desktop' in dat['device'].keys():
                    desk=dat['device']['desktop']
                else:
                    desk=0
                if 'smart_phone' in dat['device'].keys():
                    phone=dat['device']['smart_phone']
                else:
                    phone=0
                if 'tablet' in dat['device'].keys():
                    tablet=dat['device']['tablet']
                else:
                    tablet=0
            
            if False in dat['consent'].keys():
                unconsentedGames=dat['consent'][False]
                consents=len(dat['consent'].keys())-1
            else:
                unconsentedGames=0
                consents=len(dat['consent'].keys())
            totgames=totals[idx]
            uniquegames=uniques[idx]
            consentedGames=totgames-unconsentedGames
            row[idx]=[idx,gender,age,loc,desk,phone,tablet,consents,totgames,uniquegames,consentedGames,unconsentedGames]
    with open('C:\Data\Lazer Data\VS\userDemoDict.pkl','w') as f:
        cPickle.dump(row,f)
    with open('C:\Data\Lazer Data\VS\userDemos.csv','w') as f:
        writeit=csv.writer(f)
        writeit.writerow(row['header'])
        for idx,line in row.iteritems():
            if idx!='header':
                writeit.writerow(line)
            
#{u'age-bin': {4: 2},
# u'consent': {False: 1, 7788: 1},
# u'device': {u'desktop': 2},
# u'gender': {u'female': 2},
# u'id': {1: 2},
# u'locale': {u'ko': 2},
# u'uid': {u'eb6f457ff7a3df8106ba': 2}}
#  

    return row

def CreateValuesforReplicationTable(dat):
    ''' This code generates the data needed for Table 1 in the replication paper.
   
    Variable: Observations & Mean & St Dev & Min & Max & Missing
    All Participants:       
    Consent
    Gender  
    Age  
    English Location  
    Laptop or Tablet Device  	
    # Experiments Participated  
    # Experiments Consented  
    Total Consented Participated  
    
    Consenting Subjects Only:       
    
    Gender  
    Age  
    English Location  
    Laptop or Tablet Device  
    Num Diff Games Participated  
    Num Games Consented  
    Total Games Participated  
   
    '''
    headeridx=dict([(j,i) for i,j in enumerate(dat['header'])])
    dat.pop('header')
    #creating groups
    consents=[d for d in dat.values() if d[headeridx['consentedGames']]>0]          #those consenting at least once
    unconsents=[d for d in dat.values() if d[headeridx['unconsentedGames']]>0]      #those not consenting at least once
    neverConsents=[d for d in dat.values() if d[headeridx['consents']]==0]
    
    #Analysis for all participants
    totparticants=len(dat)-1
    print 'All Participants = ', totparticants
    
    #GENDER
    allgenders=len([d for d in dat.values() if d[headeridx['gender']]!=''])         #number of people reporting a gender
    allfemale=sum([d[headeridx['gender']]=='female' for d in dat.values() if d[headeridx['gender']]!=''])   #number reporting female
    allmale=sum([d[headeridx['gender']]=='male' for d in dat.values() if d[headeridx['gender']]!=''])       #number reporting male
    allmisgender=totparticants-allgenders
    allFemaleMean=round((allfemale*1+allmale*0)/float(allgenders),3)
    allFemaleStd=round(np.std([1 for i in xrange(allfemale)]+[0 for i in xrange(allmale)]),3)
    
    #AGE
    allAges=[d for d in dat.values() if d[headeridx['age']]!='']
    allAgesTot=len(allAges)
    allAgeMissing=totparticants-len(allAges)
    allages=[d[headeridx['age']] for d in allAges]
    allAgesMean=round(np.mean(allages),3)
    allAgesStd=round(np.std(allages),3)
    allAgesMax=max(allages)
    allAgesMin=min(allages)
    
    #DESKTOP
    #allDesktop=[d for d in dat.values() if d[headeridx['desktop']]>0]
    allDesktopsTot=sum([d[headeridx['desktop']] for d in dat.values() if d[headeridx['desktop']]!=''])
    alldevices=sum([d[headeridx['desktop']]+d[headeridx['tablet']]+d[headeridx['phone']] for d in dat.values() if d[headeridx['desktop']]!=''])
    allDesktopsMissing=len([d for d in dat.values() if d[headeridx['desktop']]==''])
    allDesktopsMean=round(np.mean([1 for i in xrange(allDesktopsTot)]+[0 for i in xrange(alldevices-allDesktopsTot-allDesktopsMissing)]),3)
    allDesktopsStd=round(np.std([1 for i in xrange(allDesktopsTot)]+[0 for i in xrange(alldevices-allDesktopsTot-allDesktopsMissing)]),3)
    
    #LANGUAGE
    allEnglishTot=sum(['en' in d[headeridx['locale']].lower() for d in dat.values() if d[headeridx['locale']]!=''])
    #allEnglish=sum([d[headeridx['desktop']]+d[headeridx['tablet']]+d[headeridx['phone']] for d in dat.values()])
    allEnglishMissing=len([d for d in dat.values() if d[headeridx['locale']]==''])
    allEnglishMean=round(np.mean([1 for i in xrange(allEnglishTot)]+[0 for i in xrange(totparticants-allEnglishTot-allEnglishMissing)]),3)
    allEnglishStd=round(np.std([1 for i in xrange(allEnglishTot)]+[0 for i in xrange(totparticants-allEnglishTot-allEnglishMissing)]),3)
    
    #CONSENTED PARADIGMS
    allParadigmConsentTot=sum([d[headeridx['consents']] for d in dat.values()])
    allParadigmConsentMean=round(np.mean([d[headeridx['consents']] for d in dat.values()]),3)
    allParadigmConsentStd=round(np.std([d[headeridx['consents']] for d in dat.values()]),3)
    allParadigmConsentMin=min([d[headeridx['consents']] for d in dat.values()])
    allParadigmConsentMax=max([d[headeridx['consents']] for d in dat.values()])
    
    #GAMES PLAYED
    allGamesSum=sum([d[headeridx['totgames']] for d in dat.values()])
    allGamesMean=round(np.mean([d[headeridx['totgames']] for d in dat.values()]),3)
    allGamesStd=round(np.std([d[headeridx['totgames']] for d in dat.values()]),3)
    allGamesMin=min([d[headeridx['totgames']] for d in dat.values()])
    allGamesMax=max([d[headeridx['totgames']] for d in dat.values()])
    
    #CONSENTED GAMES 'consentedGames','unconsentedGames'
    allConsentGamesTot=sum([d[headeridx['consentedGames']] for d in dat.values()])
    allgamesconsent=sum([d[headeridx['consentedGames']]+d[headeridx['unconsentedGames']] for d in dat.values()])
    allConsentGamesMean=round(np.mean([1 for i in xrange(allConsentGamesTot)]+[0 for i in xrange(allgamesconsent-allConsentGamesTot)]),3)
    allConsentGamesStd=round(np.std([1 for i in xrange(allConsentGamesTot)]+[0 for i in xrange(allgamesconsent-allConsentGamesTot)]),3)
    allConsentGamesMax=max([d[headeridx['consentedGames']] for d in dat.values()])
    allConsentGamesMin=min([d[headeridx['consentedGames']] for d in dat.values()])
    
    #WRITE ALL DATA TABLE TO FILE
    #Variable & Observations & Mean & St Dev & Min & Max & Missing 
    with open('C:\Data\Lazer Data\VS\Replication\AllTable.txt','w') as f:
        f.write("&".join(map(str,['Female',totparticants,allFemaleMean,allFemaleStd,0,1,allmisgender]))+'\\\ \n')
        f.write("&".join(map(str,['Age',totparticants,allAgesMean,allAgesStd,allAgesMin,allAgesMax,allAgeMissing]))+'\\\ \n')
        f.write("&".join(map(str,['English Language',totparticants,allEnglishMean,allEnglishStd,0,1,allEnglishMissing]))+'\\\ \n')
        f.write("&".join(map(str,['Desktop Device',allDesktopsTot,allDesktopsMean,allDesktopsStd,0,1,allDesktopsMissing]))+'\\\ \n')
        f.write("&".join(map(str,['Paradigms Consented To', allParadigmConsentTot,allParadigmConsentMean,allParadigmConsentStd,allParadigmConsentMin,allParadigmConsentMax,0]))+'\\\ \n')
        f.write("&".join(map(str,['Games Played',allGamesSum,allGamesMean,allGamesStd,allGamesMin,allGamesMax,0]))+'\\\ \n')
        f.write("&".join(map(str,['\# Consented Games',allConsentGamesTot,allConsentGamesMean,allConsentGamesStd,allConsentGamesMin,allConsentGamesMax,0]))+'\\\ \n')
    
    
    #Analysis for those who consent at least once
    
    allconsent=len(consents) #number of people consenting at least once
    consentfemale=sum([d[headeridx['gender']]=='female' for d in consents if d[headeridx['gender']]!=''])
    consentmale=sum([d[headeridx['gender']]=='male' for d in consents if d[headeridx['gender']]!=''])
    consentmisgender=allconsent-consentfemale-consentmale   #number of participants consenting but without a gender
    consentFemaleMean=round((consentfemale*1+consentmale*0)/float(consentfemale+consentmale),3)
    consentFemaleStd=round(np.std([1 for i in xrange(consentfemale)]+[0 for i in xrange(consentmale)]),3)
    
    consentAges=[d for d in consents if d[headeridx['age']]!='']
    consentAgesTot=len(consentAges)
    consentAgeMissing=allconsent-len(consentAges)
    consentages=[d[headeridx['age']] for d in consentAges]
    consentAgesMean=round(np.mean(consentages),3)
    consentAgesStd=round(np.std(consentages),3)
    consentAgesMax=max(consentages)
    consentAgesMin=min(consentages)
    
    consentDesktopsTot=sum([d[headeridx['desktop']] for d in consents if d[headeridx['desktop']]!=''])
    consentdevices=sum([d[headeridx['desktop']]+d[headeridx['tablet']]+d[headeridx['phone']] for d in consents if d[headeridx['desktop']]!=''])
    consentDesktopsMissing=len([d for d in consents if d[headeridx['desktop']]==''])
    consentDesktopsMean=round(np.mean([1 for i in xrange(consentDesktopsTot)]+[0 for i in xrange(consentdevices-consentDesktopsTot-consentDesktopsMissing)]),3)
    consentDesktopsStd=round(np.std([1 for i in xrange(consentDesktopsTot)]+[0 for i in xrange(consentdevices-consentDesktopsTot-consentDesktopsMissing)]),3)
    
    
    consentEnglishTot=sum(['en' in d[headeridx['locale']].lower() for d in consents if d[headeridx['locale']]!=''])
    #consentEnglish=sum([d[headeridx['desktop']]+d[headeridx['tablet']]+d[headeridx['phone']] for d in dat.values()])
    consentEnglishMissing=len([d for d in consents if d[headeridx['locale']]==''])
    consentEnglishMean=round(np.mean([1 for i in xrange(consentEnglishTot)]+[0 for i in xrange(allconsent-consentEnglishTot-consentEnglishMissing)]),3)
    consentEnglishStd=round(np.std([1 for i in xrange(consentEnglishTot)]+[0 for i in xrange(allconsent-consentEnglishTot-consentEnglishMissing)]),3)
    
    
    #CONSENTED PARADIGMS
    consentParadigmConsentTot=sum([d[headeridx['consents']] for d in consents])
    consentParadigmConsentMean=round(np.mean([d[headeridx['consents']] for d in consents]),3)
    consentParadigmConsentStd=round(np.std([d[headeridx['consents']] for d in consents]),3)
    consentParadigmConsentMin=min([d[headeridx['consents']] for d in consents])
    consentParadigmConsentMax=max([d[headeridx['consents']] for d in consents])   
    
    #GAMES PLAYED
    consentGamesSum=sum([d[headeridx['totgames']] for d in consents])
    consentGamesMean=round(np.mean([d[headeridx['totgames']] for d in consents]),3)
    consentGamesStd=round(np.std([d[headeridx['totgames']] for d in consents]),3)
    consentGamesMin=min([d[headeridx['totgames']] for d in consents])
    consentGamesMax=max([d[headeridx['totgames']] for d in consents])
    
    #CONSENTS
    consentGamesConsentsTot=sum([d[headeridx['consentedGames']] for d in consents])
    consentgamesconsent=sum([d[headeridx['consentedGames']]+d[headeridx['unconsentedGames']] for d in consents])
    consentGamesConsentMean=round(np.mean([1 for i in xrange(consentGamesConsentsTot)]+[0 for i in xrange(consentgamesconsent-consentGamesConsentsTot)]),3)
    consentGamesConsentStd=round(np.std([1 for i in xrange(consentGamesConsentsTot)]+[0 for i in xrange(consentgamesconsent-consentGamesConsentsTot)]),3)
    consentGamesConsentMax=max([d[headeridx['consentedGames']] for d in consents])
    consentGamesConsentMin=min([d[headeridx['consentedGames']] for d in consents])
 
    #WRITE CONSENT DATA TABLE TO FILE
    #Variable & Observations & Mean & St Dev & Min & Max & Missing 
    with open('C:\Data\Lazer Data\VS\Replication\ConsentTable.txt','w') as f:
        f.write("&".join(map(str,['Female',allconsent,consentFemaleMean,consentFemaleStd,0,1,consentmisgender]))+'\\\ \n')
        f.write("&".join(map(str,['Age',allconsent,consentAgesMean,consentAgesStd,consentAgesMin,consentAgesMax,consentAgeMissing]))+'\\\ \n')
        f.write("&".join(map(str,['English Language',allconsent,consentEnglishMean,consentEnglishStd,0,1,consentEnglishMissing]))+'\\\ \n')
        f.write("&".join(map(str,['Desktop Device',consentDesktopsTot,consentDesktopsMean,consentDesktopsStd,0,1,consentDesktopsMissing]))+'\\\ \n')
        f.write("&".join(map(str,['Paradigms Consented To', consentParadigmConsentTot,consentParadigmConsentMean,consentParadigmConsentStd,consentParadigmConsentMin,consentParadigmConsentMax,0]))+'\\\ \n')
        f.write("&".join(map(str,['Games Played',consentGamesSum,consentGamesMean,consentGamesStd,consentGamesMin,consentGamesMax,0]))+'\\\ \n')
        f.write("&".join(map(str,['\# Consented Games',consentGamesConsentsTot,consentGamesConsentMean,consentGamesConsentStd,consentGamesConsentMin,consentGamesConsentMax,0]))+'\\\ \n')
    
    
    #Analysis for those who do not consent at least once
    
    unconsent=len(unconsents) #number of people not consenting at least once
    
    unconsentfemale=sum([d[headeridx['gender']]=='female' for d in unconsents if d[headeridx['gender']]!=''])
    unconsentmale=sum([d[headeridx['gender']]=='male' for d in unconsents if d[headeridx['gender']]!=''])
    #unconsentmale=unconsent-unconsentfemale                    #number of participants not consenting who are male.
    unconsentmisgender=unconsent-unconsentfemale-unconsentmale   #number of participants not consenting but without a gender
    unconsentFemaleMean=round((unconsentfemale*1+unconsentmale*0)/float(unconsentfemale+unconsentmale),3)
    unconsentFemaleStd=round(np.std([1 for i in xrange(int(unconsentfemale))]+[0 for i in xrange(int(unconsentmale))]),3)

    unconsentAges=[d for d in unconsents if d[headeridx['age']]!='']
    unconsentAgesTot=len(unconsentAges)
    unconsentAgeMissing=unconsent-len(unconsentAges)
    unconsentages=[d[headeridx['age']] for d in unconsentAges]
    unconsentAgesMean=round(np.mean(unconsentages),3)
    unconsentAgesStd=round(np.std(unconsentages),3)
    if unconsentages==[]:
        unconsentAgesMax=''
        unconsentAgesMin=''
    else:
        unconsentAgesMax=max(unconsentages)
        unconsentAgesMin=min(unconsentages)
    
    unconsentDesktopsTot=sum([d[headeridx['desktop']] for d in unconsents if d[headeridx['desktop']]!=''])
    unconsentdevices=sum([d[headeridx['desktop']]+d[headeridx['tablet']]+d[headeridx['phone']] for d in unconsents if d[headeridx['desktop']]!=''])
    unconsentDesktopsMean=round(np.mean([1 for i in xrange(int(unconsentDesktopsTot))]+[0 for i in xrange(int(unconsentdevices-unconsentDesktopsTot))]),3)
    unconsentDesktopsStd=round(np.std([1 for i in xrange(int(unconsentDesktopsTot))]+[0 for i in xrange(int(unconsentdevices-unconsentDesktopsTot))]),3)
    unconsentDesktopsMissing=len([d for d in unconsents if d[headeridx['desktop']]==''])

    unconsentEnglishTot=sum(['en' in d[headeridx['locale']].lower() for d in unconsents if d[headeridx['locale']]!=''])
    unconsentEnglishMissing=len([d for d in unconsents if d[headeridx['locale']]==''])
    unconsentEnglishMean=round(np.mean([1 for i in xrange(int(unconsentEnglishTot))]+[0 for i in xrange(int(unconsent-unconsentEnglishTot-unconsentEnglishMissing))]),3)
    unconsentEnglishStd=round(np.std([1 for i in xrange(int(unconsentEnglishTot))]+[0 for i in xrange(int(unconsent-unconsentEnglishTot-unconsentEnglishMissing))]),3)
    
    #CONSENTED PARADIGMS
    unconsentParadigmConsentTot=sum([d[headeridx['consents']] for d in unconsents])
    unconsentParadigmConsentMean=round(np.mean([d[headeridx['consents']] for d in unconsents]),3)
    unconsentParadigmConsentStd=round(np.std([d[headeridx['consents']] for d in unconsents]),3)
    if unconsentages==[]:
        unconsentParadigmConsentMax=''
        unconsentParadigmConsentMin=''
    else:    
        unconsentParadigmConsentMin=min([d[headeridx['consents']] for d in unconsents])
        unconsentParadigmConsentMax=max([d[headeridx['consents']] for d in unconsents])   
    
    #GAMES PLAYED
    unconsentGamesSum=sum([d[headeridx['totgames']] for d in unconsents])
    unconsentGamesMean=round(np.mean([d[headeridx['totgames']] for d in unconsents]),3)
    unconsentGamesStd=round(np.std([d[headeridx['totgames']] for d in unconsents]),3)
    unconsentGamesMin=min([d[headeridx['totgames']] for d in unconsents])
    unconsentGamesMax=max([d[headeridx['totgames']] for d in unconsents])
    
    #CONSENTS
    unconsentGamesConsentsTot=sum([d[headeridx['consentedGames']] for d in unconsents])
    unconsentgamesconsent=sum([d[headeridx['consentedGames']]+d[headeridx['unconsentedGames']] for d in unconsents])
    unconsentGamesConsentsMean=round(np.mean([1 for i in xrange(unconsentGamesConsentsTot)]+[0 for i in xrange(unconsentgamesconsent-unconsentGamesConsentsTot)]),3)
    unconsentGamesConsentsStd=round(np.std([1 for i in xrange(unconsentGamesConsentsTot)]+[0 for i in xrange(unconsentgamesconsent-unconsentGamesConsentsTot)]),3)
    unconsentGamesConsentsMax=max([d[headeridx['consentedGames']] for d in unconsents])
    unconsentGamesConsentsMin=min([d[headeridx['consentedGames']] for d in unconsents])
    
    with open('C:\Data\Lazer Data\VS\Replication\UnconsentTable.txt','w') as f:
        f.write("&".join(map(str,['Female',unconsent,unconsentFemaleMean,unconsentFemaleStd,0,1,unconsentmisgender]))+'\\\ \n')
        f.write("&".join(map(str,['Age',unconsent,unconsentAgesMean,unconsentAgesStd,unconsentAgesMin,unconsentAgesMax,unconsentAgeMissing]))+'\\\ \n')
        f.write("&".join(map(str,['English Language',unconsent,unconsentEnglishMean,unconsentEnglishStd,0,1,unconsentEnglishMissing]))+'\\\ \n')
        f.write("&".join(map(str,['Desktop Device',unconsentDesktopsTot,unconsentDesktopsMean,unconsentDesktopsStd,0,1,unconsentDesktopsMissing]))+'\\\ \n')
        f.write("&".join(map(str,['Paradigms Consented To', unconsentParadigmConsentTot,unconsentParadigmConsentMean,unconsentParadigmConsentStd,unconsentParadigmConsentMin,unconsentParadigmConsentMax,0]))+'\\\ \n')
        f.write("&".join(map(str,['Games Played',unconsentGamesSum,unconsentGamesMean,unconsentGamesStd,unconsentGamesMin,unconsentGamesMax,0]))+'\\\ \n')
        f.write("&".join(map(str,['\\# Consented Games',unconsentGamesConsentsTot,unconsentGamesConsentsMean,unconsentGamesConsentsStd,unconsentGamesConsentsMin,unconsentGamesConsentsMax,0]))+'\\\ \n')
    
    ##Analysis of those who never consent?
    
    neverConsent=len(neverConsents) #number of people not consenting at least once
    
    neverConsentfemale=sum([d[headeridx['gender']]=='female' for d in neverConsents if d[headeridx['gender']]!=''])
    neverConsentmale=sum([d[headeridx['gender']]=='male' for d in neverConsents if d[headeridx['gender']]!=''])
    #neverConsentmale=neverConsent-neverConsentfemale                    #number of participants not consenting who are male.
    neverConsentmisgender=neverConsent-neverConsentfemale-neverConsentmale   #number of participants not consenting but without a gender
    neverConsentFemaleMean=round((neverConsentfemale*1+neverConsentmale*0)/float(neverConsentfemale+neverConsentmale),3)
    neverConsentFemaleStd=round(np.std([1 for i in xrange(int(neverConsentfemale))]+[0 for i in xrange(int(neverConsentmale))]),3)

    neverConsentAges=[d for d in neverConsents if d[headeridx['age']]!='']
    neverConsentAgesTot=len(neverConsentAges)
    neverConsentAgeMissing=neverConsent-len(neverConsentAges)
    neverConsentages=[d[headeridx['age']] for d in neverConsentAges]
    neverConsentAgesMean=round(np.mean(neverConsentages),3)
    neverConsentAgesStd=round(np.std(neverConsentages),3)
    if neverConsentages==[]:
        neverConsentAgesMax=''
        neverConsentAgesMin=''
    else:
        neverConsentAgesMax=max(neverConsentages)
        neverConsentAgesMin=min(neverConsentages)
    
    neverConsentDesktopsTot=sum([d[headeridx['desktop']] for d in neverConsents if d[headeridx['desktop']]!=''])
    neverConsentdevices=sum([d[headeridx['desktop']]+d[headeridx['tablet']]+d[headeridx['phone']] for d in neverConsents if d[headeridx['desktop']]!=''])
    neverConsentDesktopsMean=round(np.mean([1 for i in xrange(int(neverConsentDesktopsTot))]+[0 for i in xrange(int(neverConsentdevices-neverConsentDesktopsTot))]),3)
    neverConsentDesktopsStd=round(np.std([1 for i in xrange(int(neverConsentDesktopsTot))]+[0 for i in xrange(int(neverConsentdevices-neverConsentDesktopsTot))]),3)
    neverConsentDesktopsMissing=len([d for d in neverConsents if d[headeridx['desktop']]==''])

    neverConsentEnglishTot=sum(['en' in d[headeridx['locale']].lower() for d in neverConsents if d[headeridx['locale']]!=''])
    neverConsentEnglishMissing=len([d for d in neverConsents if d[headeridx['locale']]==''])
    neverConsentEnglishMean=round(np.mean([1 for i in xrange(int(neverConsentEnglishTot))]+[0 for i in xrange(int(neverConsent-neverConsentEnglishTot-neverConsentEnglishMissing))]),3)
    neverConsentEnglishStd=round(np.std([1 for i in xrange(int(neverConsentEnglishTot))]+[0 for i in xrange(int(neverConsent-neverConsentEnglishTot-neverConsentEnglishMissing))]),3)
    
    #CONSENTED PARADIGMS
    neverConsentParadigmConsentTot=sum([d[headeridx['consents']] for d in neverConsents])
    neverConsentParadigmConsentMean=round(np.mean([d[headeridx['consents']] for d in neverConsents]),3)
    neverConsentParadigmConsentStd=round(np.std([d[headeridx['consents']] for d in neverConsents]),3)
    if neverConsentages==[]:
        neverConsentParadigmConsentMax=''
        neverConsentParadigmConsentMin=''
    else:    
        neverConsentParadigmConsentMin=min([d[headeridx['consents']] for d in neverConsents])
        neverConsentParadigmConsentMax=max([d[headeridx['consents']] for d in neverConsents])   
    
    #GAMES PLAYED
    neverConsentGamesSum=sum([d[headeridx['totgames']] for d in neverConsents])
    neverConsentGamesMean=round(np.mean([d[headeridx['totgames']] for d in neverConsents]),3)
    neverConsentGamesStd=round(np.std([d[headeridx['totgames']] for d in neverConsents]),3)
    neverConsentGamesMin=min([d[headeridx['totgames']] for d in neverConsents])
    neverConsentGamesMax=max([d[headeridx['totgames']] for d in neverConsents])
    
    #CONSENTS
    neverConsentGamesConsentsTot=sum([d[headeridx['consentedGames']] for d in neverConsents])
    neverConsentgamesconsent=sum([d[headeridx['consentedGames']]+d[headeridx['unconsentedGames']] for d in neverConsents])
    neverConsentGamesConsentsMean=round(np.mean([1 for i in xrange(neverConsentGamesConsentsTot)]+[0 for i in xrange(neverConsentgamesconsent-neverConsentGamesConsentsTot)]),3)
    neverConsentGamesConsentsStd=round(np.std([1 for i in xrange(neverConsentGamesConsentsTot)]+[0 for i in xrange(neverConsentgamesconsent-neverConsentGamesConsentsTot)]),3)
    neverConsentGamesConsentsMax=max([d[headeridx['consentedGames']] for d in neverConsents])
    neverConsentGamesConsentsMin=min([d[headeridx['consentedGames']] for d in neverConsents])
    
    with open('C:\Data\Lazer Data\VS\Replication\NeverConsentTable.txt','w') as f:
        f.write("&".join(map(str,['Female',neverConsent,neverConsentFemaleMean,neverConsentFemaleStd,0,1,neverConsentmisgender]))+'\\\ \n')
        f.write("&".join(map(str,['Age',neverConsent,neverConsentAgesMean,neverConsentAgesStd,neverConsentAgesMin,neverConsentAgesMax,neverConsentAgeMissing]))+'\\\ \n')
        f.write("&".join(map(str,['English Language',neverConsent,neverConsentEnglishMean,neverConsentEnglishStd,0,1,neverConsentEnglishMissing]))+'\\\ \n')
        f.write("&".join(map(str,['Desktop Device',neverConsentDesktopsTot,neverConsentDesktopsMean,neverConsentDesktopsStd,0,1,neverConsentDesktopsMissing]))+'\\\ \n')
        f.write("&".join(map(str,['Paradigms Consented To', neverConsentParadigmConsentTot,neverConsentParadigmConsentMean,neverConsentParadigmConsentStd,neverConsentParadigmConsentMin,neverConsentParadigmConsentMax,0]))+'\\\ \n')
        f.write("&".join(map(str,['Games Played',neverConsentGamesSum,neverConsentGamesMean,neverConsentGamesStd,neverConsentGamesMin,neverConsentGamesMax,0]))+'\\\ \n')
        f.write("&".join(map(str,['\\# Consented Games',neverConsentGamesConsentsTot,neverConsentGamesConsentsMean,neverConsentGamesConsentsStd,neverConsentGamesConsentsMin,neverConsentGamesConsentsMax,0]))+'\\\ \n')
    
    #headeridx=dict([(j,i) for i,j in enumerate(dat['row'])])
    #consents=[d for d in dat.values() if d[headeridx['consentedGames']]>0]
    
    
    #print 'Gender of all Participants = ', [dat['gender'] for uid,dat in demographics.iteritems() if 'gender' in dat.keys() and uid !='count']
    #print 'num ppl with multiple consents = ', [uniques[uid]-len(dat['consent'].keys()) for uid,dat in demographics.iteritems() if uid!='count']
    return
        
        
def createValidationStatsPerGame():
    '''
    Stats:
    Number of Consent/non-consents
    Number of completes/incompletes (both consented and non-consented)
    Number of Bad-Faith data: 'illogical,' 'too fast', 'too long', 'all answers the same', (Consent, non-consent)
    '''
    return

allStudies={'BigFive':'114','Cognitive Reflection':'96','Coll-Indiv':'97','Decision Problems':'94','Egoism':'102','Volunteer-Motivation':'111',
       'Need-Cognition':'95', 'Network_Awareness':'107', 'Social Capital':'113','Random':'104','Reciprocity':'110','Self_Esteem':'108',
       'Self_Monitoring':'109','Web Skill':'112','Which Band':'128','3Cows':'80','Hidden Profile':'82','TSP':'3','Prisoners Dilemma':'81','Flanker':'90','Stroop':'89',
       'Wildcat Wells': '105','Public Goods': '69','demographic':'82','Six Figures':'171','Impression Vignette':'176','justicia':'173',"PWC":'177','system justification':'178'}
experiments={'BigFive':'114','Cognitive Reflection':'96','Coll-Indiv':'97','Decision Problems':'94','Egoism':'102','Volunteer-Motivation':'111',
       'Need-Cognition':'95', 'Network_Awareness':'107', 'Social Capital':'113','Random':'104','Reciprocity':'110','Self_Esteem':'108',
       'Self_Monitoring':'109','Web Skill':'112','Which Band':'128','3Cows':'80','Hidden Profile':'82','TSP':'3','Prisoners Dilemma':'81','Flanker':'90','Stroop':'89',
       'Wildcat Wells': '105','Public Goods': '69','demographic':'82','optimizing opinions':'148','Six Figures':'171'}
#
#replications={'BigFive':'114','Cognitive Reflection':'96','Decision Problems':'94',
#       'Random':'104','3Cows':'80','Hidden Profile':'82','TSP':'3','Prisoners Dilemma':'81','Flanker':'90','Stroop':'89'}
plosRep={'BigFive':'114','Flanker':'90','Stroop':'89','Decision Problems':'94'}
params=[('amt','exclude'),('pi','exclude'),('consent','all_experiments'),('demonstration','exclude'),('start','01/01/2014'),('end',dt.date.strftime(dt.date.today(),"%m/%d/%Y"))]#'11/30/2015')]#dt.date.strftime(dt.date.today(),"%m/%d/%Y"))]
#
test={'Need-Cognition':'95'}
Users={}
Players={}
for g,num in allStudies.iteritems():
    print '\n'+g.upper() + '\n'
    data=urlConstruct(params,num)
    players,Users=users(data,Users,name=g)
    Players[g]=players
Users2=MakeUserFile(Users,Players)
demographics,uniques,totals=ParticipationReport(Users)
dat=flatten(demographics,uniques, totals)
CreateValuesforReplicationTable(dat)