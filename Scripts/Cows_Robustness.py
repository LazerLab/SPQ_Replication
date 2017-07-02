
# -*- coding: utf-8 -*-
'''
Created on Fri May 19 2016

@author: Jason Radford

This code is built off of the PD_Robustness.py.  It examines several questions related to the robustness of the Commons results.
First, if we include subjects who first participated prior to the published study (i.e. before 12/09/2015),
do the results change?  That is, if subjects participate in a prior Cows study, can they participate
in a future Cows study.

Second, in general, do subjects who participate more than once have a different strategy, controlling for
payoffs?
Third, did subjects in commensurable conditions prior to 12/09/2015 make similar choices?
'''

import datetime as dt
import json
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde,ttest_ind
from matplotlib import pyplot as pp
import urllib
from httplib2 import Http
import scipy as sp
import scipy.stats
import cPickle

def urlConstruct(params):
    tok='a2001b6f077291c6e92365bc28d982752b966f58'
    url='http://volunteerscience.com/data/81/?format=json&'+urllib.urlencode(params)+'&token='+tok
    client=Http()
    content = client.request(url,method='GET',body='')
    data = json.loads(content[1])['tests']
    return data

def importData(fname):
    with open(fname,'rb') as f:
        a=f.read()
    data=json.loads(a)
    return data['tests']

def removeCondition(data):
    #following reviewer 3, we remove a fourth condition which changed the PNSE as well as the payoffs and so
    #confounded our experimental results
    cdata=[]
    conditions={"[[u'-1', u'0', u'0', u'1'], [u'0.75', u'0.75', u'0.75', u'0.75']]": 'barn',
                "[[u'-1', u'0', u'0', u'1'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'leanBarn',
                "[[u'-1', u'0', u'0', u'3'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'leanCommons',
                "[[u'0', u'0', u'0', u'3'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'commons'}
    for game in data:
        if str(game['matrices']['payoff']) in conditions.keys():
            cdata.append(game)
    
    return cdata

def removeAllDuplicates(old,data):
    '''
    This code removes experiments with subjects who participated in previous prisoner's dilemma study as well as those
    who participate twice in current study.
    1. Find gameids from all PD games (in old)
    2. Find userids from those old games.
    3. Exclude those userids from new games (in data).
    '''
    from collections import Counter
    olds=set()
    games=set()
    oldids=set([g['id'] for g in old])
    dids=set([g['id'] for g in data])
    priors=list(oldids.difference(dids))   #pull out gameids that only exist in previous games
    
    oldsubjects=[]
    for game in old:
        if game['id'] not in priors:
            break
        for subject in game['subjects']:
            oldsubjects.append(subject['uid'])
    oldsubjects=Counter(oldsubjects)
    
    eligible=[]
    ineligible=[]
    clean_data=[]
    for game in data:
        gameid=game['id']
        for subject in game['subjects']:
            uid=subject['uid']
            if uid in oldsubjects.keys():
                oldsubjects[uid]+=1
                ineligible.append(gameid)
            else:
                oldsubjects[uid]=1
                eligible.append(gameid)
                clean_data.append(game)
                
    return clean_data


def ImportUserData():
    '''
    This code loads data from users across games donated for the validation study.
    Returns: users[uid]=[uid,gender,age,language,desk,phone,tablet,consents,totgames,uniquegames,consentedGames,unconsentedGames]
           users[str]=[str,category,nominal,category,count,count,count,count,count,count,count,count]
    '''
    with open('Clean_Data/userDemoDict.pkl','r') as f:
        users=cPickle.load(f)
    return users


def easyCounts(data):
    #for game in data:
    #    consents+=sum([sub['consent']!=False for sub in game['subjects']])
           
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
    NumParticipants=len(set(ids))
    #print "Number of Unique Participants in %s = %d \n" % (game,NumParticipants)
    #results=[NumNonConsentGames,numValidGames,NumValidRounds,NumParticipants]
    return #results


def Cows_Clean_First_Experiment(data):
    '''
    Summary: Tests whether including prior participants produces different results from including
    only new participants
    
    This function processes the raw json data and excludes participants who do not consent and multi-person experiments
    '''
    
    data=removeOld(old,data)
    #import generic user data from Subject_Participation.py
    userdict=ImportUserData()
    #Format cleaning variables for the analysis
    Results=[]
    incompletes=0.0
    pdTrans={"Don't Testify":0,"Testify":1}                                     #dictionary to recode player choices
    subTranslate={'desktop':1,'mobile':2,'tablet':3,'male':1,'female':0}        #dictionary to recode demographic variables
    
    payoffs=set([str(c['matrices']['payoff']) for c in data])
    conditions={"[[u'-1', u'0', u'0', u'1'], [u'0.75', u'0.75', u'0.75', u'0.75']]": 'barn',
                "[[u'-1', u'0', u'0', u'1'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'leanBarn',
                "[[u'-1', u'0', u'0', u'3'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'leanCommons',
                "[[u'0', u'0', u'0', u'3'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'commons'}
    
    #check to make sure formatting is correct
    if len(payoffs)!=len(conditions):
        print 'error: unexpected payoffs! \n',payoffs, conditions
    
    #iterate through each game and generate data
    subjects=set(['0']) #subject '0' is always a bot
    for idx,game in enumerate(data):
        
        
        #exclude players who started a game but never made it past instructions (and therefore breaks later code)
        if len(game['submissions'])<3:  
            incompletes+=1
            continue

        #exclude any experiments not using conditions (should not occur)
        if str(game['matrices']['payoff']) not in conditions.keys():
            continue
        
        Exclude=False
        num_subjects=0
        for subject in game['subjects']:
            #exclude experiments if one subject has already participated
            if str(subject['uid']) in subjects and subject['uid']!='0':
                Exclude=True
            else:
                subjects.update([subject['uid']])
            #Exclude games if one subject does not consent
            if subject['consent']==False:
                Exclude=True
        
            if subject['uid']!=0:
                num_subjects+=1
            
        #Enforce exclusions
        if Exclude==True:
            continue
            
        
        line=[]
        gameid=game['id']
        position=str(game['subjects'][0]['id'])
        person = str(game['subjects'][0]['uid'])
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
        cond=conditions[str(game['matrices']['payoff'])]
        
        #get sequence of rounds containing subject e.g. [TRUE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE]
        opps=sum([position in a['#text'] for a in game['submissions'][0]['val']['activePlayers']])
        
        #get list of round for subject
        rnds=[int(a['expRound']) for a in game['submissions'][0]['val']['activePlayers'] if position in a['#text']]
        

        readyRound=[int(g['round']) for g in game['submissions'] if g['val']=='Ready'][-1]   #the initial round, required to adjust rnds.
        round_timer=int(game['variables']["experiment_round_timer"])                 
        results_timer=int(game['variables']["result_timer"])
        #For the validation paper, we only look at the player's first choice.
        Exclude=False
        choices=[]
        for index,g in enumerate(game['submissions']):
            if int(g['round'])-readyRound in rnds:
                #if player exceeds time, the decision is made for them. So exclude them from the sample.
                if rnds==1: #if first round, maxtime is ?
                    maxtime=round_timer
                else:
                    maxtime=round_timer+results_timer
                time_taken=g['time']-game['submissions'][index-1]['time']
                if time_taken>maxtime:
                    #print 'found a lapsed player'
                    Exclude=True
                    continue
                else:
                    for answer in g['val']['answer']:
                        #Some errors get printed here. I should be able to delete this after excluding non-consented users
                        if type(answer)==unicode:
                            continue
                        #if 'subject' not in answer.keys():
                        #    print idx,answer
                        if answer['subject']==position:
                                choices.append(pdTrans[answer['#text']])
                    #else:
                    #    oanswers.append(pdTrans[answer['#text']])
                    #nth+=1
        if choices==[]:
            Exclude=True
        if Exclude==False:
            line=[gameid,person,cond,np.mean(choices),gender, age, device]
            if person in userdict.keys():            
                line+=userdict[person]
            else:
                line+=['' for j in userdict.values()[0]]
            Results.append(line)
 
    header=['gameid','person','cond','choices','gender','age','device']+userdict['header']
    return Results,header



def Cows_Clean_First_Round(data):
    '''
    Summary: This function processes the raw json data and excludes participants who do not consent and multi-person experiments
    '''
    
    #import generic user data from Subject_Participation.py
    userdict=ImportUserData()
    #Format cleaning variables for the analysis
    Results=[]
    incompletes=0.0
    pdTrans={"Don't Testify":0,"Testify":1}                                     #dictionary to recode player choices
    subTranslate={'desktop':1,'mobile':2,'tablet':3,'male':1,'female':0}        #dictionary to recode demographic variables
    
    payoffs=set([str(c['matrices']['payoff']) for c in data])
    conditions={"[[u'-1', u'0', u'0', u'1'], [u'0.75', u'0.75', u'0.75', u'0.75']]": 'barn',
                "[[u'-1', u'0', u'0', u'1'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'leanBarn',
                "[[u'-1', u'0', u'0', u'3'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'leanCommons',
                "[[u'0', u'0', u'0', u'3'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'commons'}
    
    #check to make sure formatting is correct
    if len(payoffs)!=len(conditions):
        print 'error: unexpected payoffs! \n',payoffs, conditions
    
    #iterate through each game and generate data
    subjects=set(['0']) #subject '0' is always a bot
    for idx,game in enumerate(data):
        
        
        #exclude players who started a game but never made it past instructions (and therefore breaks later code)
        if len(game['submissions'])<3:  
            incompletes+=1
            continue

        #exclude any experiments not using conditions (should not occur)
        if str(game['matrices']['payoff']) not in conditions.keys():
            continue
        
        Exclude=False
        num_subjects=0
        for subject in game['subjects']:
            #exclude experiments if one subject has already participated
            if str(subject['uid']) in subjects and subject['uid']!='0':
                Exclude=True
            else:
                subjects.update([subject['uid']])
            #Exclude games if one subject does not consent
            if subject['consent']==False:
                Exclude=True
        
            if subject['uid']!=0:
                num_subjects+=1
            
        #Enforce exclusion
        if Exclude==True:
            continue
            
        
        line=[]
        gameid=game['id']
        position=str(game['subjects'][0]['id'])
        person = str(game['subjects'][0]['uid'])
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
        cond=conditions[str(game['matrices']['payoff'])]
        
        #get sequence of rounds containing subject e.g. [TRUE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE]
        opps=sum([position in a['#text'] for a in game['submissions'][0]['val']['activePlayers']])
        
        #get list of round for subject
        rnds=[int(a['expRound']) for a in game['submissions'][0]['val']['activePlayers'] if position in a['#text']]
        answers=[]
        oanswers=[]

        readyRound=[int(g['round']) for g in game['submissions'] if g['val']=='Ready'][-1]   #the initial round, required to adjust rnds.
        round_timer=int(game['variables']["experiment_round_timer"])                 
        results_timer=int(game['variables']["result_timer"])
        #For the validation paper, we only look at the player's first choice.
        Exclude=False
        for index,g in enumerate(game['submissions']):
            if int(g['round'])-readyRound == rnds[0]:
                
                #if player exceeds time, the decision is made for them. So exclude them from the sample.
                if rnds==1: #if first round, maxtime is ?
                    maxtime=round_timer
                else:
                    maxtime=round_timer+results_timer
                time_taken=g['time']-game['submissions'][index-1]['time']
                if time_taken>maxtime:
                    #print 'found a lapsed player'
                    Exclude=True
                    continue
                
                else:
                    for answer in g['val']['answer']:
                        #Some errors get printed here. I should be able to delete this after excluding non-consented users
                        if type(answer)==unicode:
                            continue
                        #if 'subject' not in answer.keys():
                        #    print idx,answer
                        if answer['subject']==position:
                                choice=pdTrans[answer['#text']]
                    #else:
                    #    oanswers.append(pdTrans[answer['#text']])
                    #nth+=1
        if Exclude==False:
            line=[gameid,person,cond,choice,gender, age, device]
            if person in userdict.keys():            
                line+=userdict[person]
            else:
                line+=['' for j in userdict.values()[0]]
            Results.append(line)
            
 
    header=['gameid','person','cond','choice','gender','age','device']+userdict['header']
    return Results,header


def Cows_Clean_First_Session(data):
    '''
    Summary: This function processes the raw json data and excludes participants who do not consent and multi-person experiments
    '''
    
    #import generic user data from Subject_Participation.py
    userdict=ImportUserData()
    #Format cleaning variables for the analysis
    Results=[]
    incompletes=0.0
    pdTrans={"Don't Testify":0,"Testify":1}                                     #dictionary to recode player choices
    subTranslate={'desktop':1,'mobile':2,'tablet':3,'male':1,'female':0}        #dictionary to recode demographic variables
    
    payoffs=set([str(c['matrices']['payoff']) for c in data])
    conditions={"[[u'-1', u'0', u'0', u'1'], [u'0.75', u'0.75', u'0.75', u'0.75']]": 'barn',
                "[[u'-1', u'0', u'0', u'1'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'leanBarn',
                "[[u'-1', u'0', u'0', u'3'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'leanCommons',
                "[[u'0', u'0', u'0', u'3'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'commons'}
    
    #check to make sure formatting is correct
    if len(payoffs)!=len(conditions):
        print 'error: unexpected payoffs! \n',payoffs, conditions
    
    #iterate through each game and generate data
    subjects=set(['0']) #subject '0' is always a bot
    for idx,game in enumerate(data):
        
        #exclude experiments manually for odd data
        
        #exclude players who started a game but never made it past instructions (and therefore breaks later code)
        if len(game['submissions'])<3:  
            incompletes+=1
            continue

        #exclude any experiments not using conditions (should not occur)
        if str(game['matrices']['payoff']) not in conditions.keys():
            continue
        
        Exclude=False
        num_subjects=0
        for subject in game['subjects']:
            #exclude experiments if one subject has already participated
            if str(subject['uid']) in subjects and subject['uid']!='0':
                Exclude=True
            else:
                subjects.update([subject['uid']])
            #Exclude games if one subject does not consent
            if subject['consent']==False:
                Exclude=True
        
            if subject['uid']!=0:
                num_subjects+=1
            
        #Enforce exclusions
        if Exclude==True:
            continue
            
        
        line=[]
        gameid=game['id']
        position=str(game['subjects'][0]['id'])
        person = str(game['subjects'][0]['uid'])
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
        cond=conditions[str(game['matrices']['payoff'])]
        
        #get sequence of rounds containing subject e.g. [TRUE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE]
        opps=sum([position in a['#text'] for a in game['submissions'][0]['val']['activePlayers']])
        
        #get list of round for subject
        rnds=[int(a['expRound']) for a in game['submissions'][0]['val']['activePlayers'] if position in a['#text']]
        

        readyRound=[int(g['round']) for g in game['submissions'] if g['val']=='Ready'][-1]   #the initial round, required to adjust rnds.
        round_timer=int(game['variables']["experiment_round_timer"])                 
        results_timer=int(game['variables']["result_timer"])
        #For the validation paper, we only look at the player's first choice.
        Exclude=False
        choices=[]
        for index,g in enumerate(game['submissions']):
            if int(g['round'])-readyRound in rnds:
                #if player exceeds time, the decision is made for them. So exclude them from the sample.
                if rnds==1: #if first round, maxtime is ?
                    maxtime=round_timer
                else:
                    maxtime=round_timer+results_timer
                time_taken=g['time']-game['submissions'][index-1]['time']
                if time_taken>maxtime:
                    #print 'found a lapsed player'
                    Exclude=True
                    continue
                else:
                    for answer in g['val']['answer']:
                        #Some errors get printed here. I should be able to delete this after excluding non-consented users
                        if type(answer)==unicode:
                            continue
                        #if 'subject' not in answer.keys():
                        #    print idx,answer
                        if answer['subject']==position:
                                choices.append(pdTrans[answer['#text']])
                    #else:
                    #    oanswers.append(pdTrans[answer['#text']])
                    #nth+=1
        if choices==[]:
            Exclude=True
        if Exclude==False:
            line=[gameid,person,cond,np.mean(choices),gender, age, device]
            if person in userdict.keys():            
                line+=userdict[person]
            else:
                line+=['' for j in userdict.values()[0]]
            Results.append(line)
 
    header=['gameid','person','cond','choices','gender','age','device']+userdict['header']
    return Results,header


def Cows_Clean_All_Sessions(data):
    '''
    Summary: This function processes the raw json data and excludes participants who do not consent and multi-person experiments
    '''
    
    #import generic user data from Subject_Participation.py
    userdict=ImportUserData()
    #Format cleaning variables for the analysis
    Results=[]
    incompletes=0.0
    pdTrans={"Don't Testify":0,"Testify":1}                                     #dictionary to recode player choices
    subTranslate={'desktop':1,'mobile':2,'tablet':3,'male':1,'female':0}        #dictionary to recode demographic variables
    
    payoffs=set([str(c['matrices']['payoff']) for c in data])
    conditions={"[[u'3', u'0'], [u'10', u'3']]":'testify',
                "[[u'3', u'0'], [u'10', u'1']]":'leanTestify',                  #This was dropped in Dec 2015 before the reddit burst
                "[[u'3', u'0'], [u'5', u'1']]":'leanNot',
                "[[u'5', u'3'], [u'5', u'1']]":'notTestify'}                    #condition excluded following reviewer 1's recommendation
    
    #check to make sure formatting is correct
    if len(payoffs)!=len(conditions):
        print 'error: unexpected payoffs! \n',payoffs, conditions
    
    #iterate through each game and generate data
    #subjects=set(['0']) #subject '0' is always a bot
    for idx,game in enumerate(data):
        
        #exclude experiments manually for odd data
        
        #exclude players who started a game but never made it past instructions (and therefore breaks later code)
        if len(game['submissions'])<3:  
            incompletes+=1
            continue

        #exclude any experiments not using conditions (should not occur)
        if str(game['matrices']['payoff']) not in conditions.keys():
            continue
        
        Exclude=False
        num_subjects=0
        for subject in game['subjects']:
            #exclude experiments if one subject has already participated
            #if str(subject['uid']) in subjects and subject['uid']!='0':
            #    Exclude=True
            #else:
            #    subjects.update([subject['uid']])
            #Exclude games if one subject does not consent
            if subject['consent']==False:
                Exclude=True
        
            if subject['uid']!=0:
                num_subjects+=1
            
        #Enforce exclusions
        if Exclude==True:
            continue
            
        
        line=[]
        gameid=game['id']
        position=str(game['subjects'][0]['id'])
        person = str(game['subjects'][0]['uid'])
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
        cond=conditions[str(game['matrices']['payoff'])]
        
        #get sequence of rounds containing subject e.g. [TRUE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE]
        opps=sum([position in a['#text'] for a in game['submissions'][0]['val']['activePlayers']])
        
        #get list of round for subject
        rnds=[int(a['expRound']) for a in game['submissions'][0]['val']['activePlayers'] if position in a['#text']]
        

        readyRound=[int(g['round']) for g in game['submissions'] if g['val']=='Ready'][-1]   #the initial round, required to adjust rnds.
        round_timer=int(game['variables']["experiment_round_timer"])                 
        results_timer=int(game['variables']["result_timer"])
        #For the validation paper, we only look at the player's first choice.
        Exclude=False
        choices=[]
        for index,g in enumerate(game['submissions']):
            if int(g['round'])-readyRound in rnds:
                #if player exceeds time, the decision is made for them. So exclude them from the sample.
                if rnds==1: #if first round, maxtime is ?
                    maxtime=round_timer
                else:
                    maxtime=round_timer+results_timer
                time_taken=g['time']-game['submissions'][index-1]['time']
                if time_taken>maxtime:
                    #print 'found a lapsed player'
                    Exclude=True
                    continue
                else:
                    for answer in g['val']['answer']:
                        #Some errors get printed here. I should be able to delete this after excluding non-consented users
                        if type(answer)==unicode:
                            continue
                        #if 'subject' not in answer.keys():
                        #    print idx,answer
                        if answer['subject']==position:
                                choices.append(pdTrans[answer['#text']])
                    #else:
                    #    oanswers.append(pdTrans[answer['#text']])
                    #nth+=1
        if choices==[]:
            Exclude=True
        if Exclude==False:
            line=[gameid,person,cond,np.mean(choices),gender, age, device]
            if person in userdict.keys():            
                line+=userdict[person]
            else:
                line+=['' for j in userdict.values()[0]]
            Results.append(line)
 
    header=['gameid','person','cond','choices','gender','age','device']+userdict['header']
    return Results,header


def Cows_Clean_Not_First_Sessions(data):
    '''
    Summary: This function processes the raw json data and excludes participants who do not consent and multi-person experiments
    '''
    
    #import generic user data from Subject_Participation.py
    userdict=ImportUserData()
    #Format cleaning variables for the analysis
    Results=[]
    incompletes=0.0
    pdTrans={"Don't Testify":0,"Testify":1}                                     #dictionary to recode player choices
    subTranslate={'desktop':1,'mobile':2,'tablet':3,'male':1,'female':0}        #dictionary to recode demographic variables
    
    payoffs=set([str(c['matrices']['payoff']) for c in data])
    conditions={"[[u'3', u'0'], [u'10', u'3']]":'testify',
                "[[u'3', u'0'], [u'10', u'1']]":'leanTestify',                  #This was dropped in Dec 2015 before the reddit burst
                "[[u'3', u'0'], [u'5', u'1']]":'leanNot',
                "[[u'5', u'3'], [u'5', u'1']]":'notTestify'}                    #condition excluded following reviewer 1's recommendation
    
    #check to make sure formatting is correct
    if len(payoffs)!=len(conditions):
        print 'error: unexpected payoffs! \n',payoffs, conditions
    
    #iterate through each game and generate data
    subjects=set(['0']) #subject '0' is always a bot
    for idx,game in enumerate(data):
        
        #exclude experiments manually for odd data
        
        #exclude players who started a game but never made it past instructions (and therefore breaks later code)
        if len(game['submissions'])<3:  
            incompletes+=1
            continue

        #exclude any experiments not using conditions (should not occur)
        if str(game['matrices']['payoff']) not in conditions.keys():
            continue
        
        Exclude=False
        num_subjects=0
        for subject in game['subjects']:
            #exclude experiments if one subject has already participated
            if str(subject['uid']) not in subjects and subject['uid']!='0':
                Exclude=True
                subjects.update([subject['uid']])
            else:
                subjects.update([subject['uid']])
            #Exclude games if one subject does not consent
            if subject['consent']==False:
                Exclude=True
        
            if subject['uid']!=0:
                num_subjects+=1
            
        #Enforce exclusions
        if Exclude==True:
            continue
            
        
        line=[]
        gameid=game['id']
        position=str(game['subjects'][0]['id'])
        person = str(game['subjects'][0]['uid'])
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
        cond=conditions[str(game['matrices']['payoff'])]
        
        #get sequence of rounds containing subject e.g. [TRUE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, TRUE, FALSE, FALSE]
        opps=sum([position in a['#text'] for a in game['submissions'][0]['val']['activePlayers']])
        
        #get list of round for subject
        rnds=[int(a['expRound']) for a in game['submissions'][0]['val']['activePlayers'] if position in a['#text']]
        

        readyRound=[int(g['round']) for g in game['submissions'] if g['val']=='Ready'][-1]   #the initial round, required to adjust rnds.
        round_timer=int(game['variables']["experiment_round_timer"])                 
        results_timer=int(game['variables']["result_timer"])
        #For the validation paper, we only look at the player's first choice.
        Exclude=False
        choices=[]
        for index,g in enumerate(game['submissions']):
            if int(g['round'])-readyRound in rnds:
                #if player exceeds time, the decision is made for them. So exclude them from the sample.
                if rnds==1: #if first round, maxtime is ?
                    maxtime=round_timer
                else:
                    maxtime=round_timer+results_timer
                time_taken=g['time']-game['submissions'][index-1]['time']
                if time_taken>maxtime:
                    #print 'found a lapsed player'
                    Exclude=True
                    continue
                else:
                    for answer in g['val']['answer']:
                        #Some errors get printed here. I should be able to delete this after excluding non-consented users
                        if type(answer)==unicode:
                            continue
                        #if 'subject' not in answer.keys():
                        #    print idx,answer
                        if answer['subject']==position:
                                choices.append(pdTrans[answer['#text']])
                    #else:
                    #    oanswers.append(pdTrans[answer['#text']])
                    #nth+=1
        if choices==[]:
            Exclude=True
        if Exclude==False:
            line=[gameid,person,cond,np.mean(choices),gender, age, device]
            if person in userdict.keys():            
                line+=userdict[person]
            else:
                line+=['' for j in userdict.values()[0]]
            Results.append(line)
 
    header=['gameid','person','cond','choices','gender','age','device']+userdict['header']
    return Results,header

    
def totals(cdata):
    count={}
    bf={}
    for l in cdata:
        if l[1] in count:
            count[l[1]]+=1
        else:
            count[l[1]]=1
            #if l[len(l)-2]<.65:
            #    bf[l[0]]=l[len(l)-2]
    print '\n Total Unique Players = ', len(count)
    print 'Total Players w/Multiple participation =', len([c for c,v in count.iteritems() if v>1]), ' and percent multiple = ',len([c for c,v in count.iteritems() if v>1])/float(len(count)    )
    print 'Total Games = ', len(set([d[0] for d in cdata]))
    #print 'Total Observations = ', len(cdata) #unnecessary, obs-level is game, not round
    #print 'Bad Faith (<65%) =', len(bf), ' percent: ', float(len(bf))/len(count)
    
    #The following commented-out code is only used when analyzing multiple rounds
    #completes=dict([(str(d[1]),d[6]-len(d[7])) for d in cdata])
    #print 'total incomplete games = ', sum([c>0 for c in completes.values()]), ' and percent complete = ', sum([c>0 for c in completes.values()])/float(len(completes))
    
    #print '\n Cleaning data of incompletes and inaccuarates'
    clean=[]
    #dones=set()
    for line in cdata:
    #    if line[6]-len(line[7])>0:
    #        continue
        clean.append(line)
    
    print "final number of games = ", len(clean), ' by percent: ', float(len(clean))/len(cdata)
    print "final number of complete games",len(set([l[0] for l in clean])), ' percent of the original games ', len(set([l[0] for l in clean]))/float(len(set([d[0] for d in cdata])))
    return clean

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    print n, m, m-h, m+h
    return m, m-h, m+h


def testPD(res):
    '''
    header=['gameid','person','cond','choice','gender','age','device']+userdict['header']
        
    '''
    testify=[a[3] for a in res if a[2]=='testify']
    ltestify=[a[3] for a in res if a[2]=='leanTestify']
    lnot=[a[3] for a in res if a[2]=='leanNot']
    notestifies=[a[3] for a in res if a[2]=='notTestify']
    print 'Testify conf-int'
    vci=mean_confidence_interval(testify, confidence=0.95)
    print 'Lean Testify conf-int'
    tci=mean_confidence_interval(ltestify, confidence=0.95)
    print 'Lean Not Testify conf-int'
    bci=mean_confidence_interval(lnot, confidence=0.95)
    print 'Not Testify conf-int'
    ntci=mean_confidence_interval(notestifies, confidence=0.95)
    print np.mean(testify),np.mean(ltestify),np.mean(lnot)#,np.mean(notestifies)
    t,p=ttest_ind(testify,ltestify)
    print 'T-test for Testify vs. Lean Testify shows t = %f at p=%f for means of %f and %f' % (t,p,np.mean(testify),np.mean(ltestify))
    t,p=ttest_ind(testify,lnot)
    print 'T-test for Testify vs. Lean Not Testify shows t = %f at p=%f for means of %f and %f' % (t,p,np.mean(testify),np.mean(lnot))
    t,p=ttest_ind(ltestify,lnot)   
    print 'T-test for Lean Not Testify vs. Lean Testify shows t = %f at p=%f for means of %f and %f' % (t,p,np.mean(lnot),np.mean(ltestify))
    t,p=ttest_ind(lnot,notestifies)
    print 'T-test for Lean Not Testify vs. Not Testify shows t = %f at p=%f for means of %f and %f' % (t,p,np.mean(lnot),np.mean(notestifies))
    t,p=ttest_ind(ltestify,notestifies)
    print 'T-test for Lean Testifies vs. NotTestifies shows t = %f at p=%f for means of %f and %f' % (t,p,np.mean(ltestify),np.mean(notestifies))
    return

#params=[('amt','exclude'),('pi','exclude'),('variables','all'),('start','01/07/2015'),('end','01/01/2016')]#dt.date.strftime(dt.date.today(),"%m/%d/%Y"))]
#data=urlConstruct(params)

old=importData('Raw_Data/All_Three_Cows.json')
data=importData('Raw_Data/Three_Cows.json')
data=removeCondition(data)
easyCounts(data)


#results,header=Cows_Clean_First_Round(data)
#results=totals(results)
#testPD(results)

#results,header=Cows_Clean_First_Session(data)
##results=totals(results)
#testPD(results)


######## Test removal of prior participants and duplicate participants
clean=removeAllDuplicates(old,data)
results,header=Cows_Clean_First_Session(clean)
print 'results for study participants excluding those from prior PD studies'
testPD(results)

results,header=Cows_Clean_First_Session(data)
print 'results for study participants including those from prior PD studies'
testPD(results)

results,header=Cows_Clean_First_Session(old)
print 'results for all participants including those from prior PD studies'
testPD(results)

###Compare those participating for the first time versus
###data for every participant regardless of repetition
#Results indicate people testify much more after their first session
results,header=Cows_Clean_First_Session(old)
print 'results for all participants including those from prior PD studies'
testPD(results)

results,header=Cows_Clean_Not_First_Sessions(old[30:])
print 'results for all participants including those from prior PD studies'
testPD(results)


##Results indicate very few people (4 out of possible 278) participated before.
#4 people participated for the first time before current PD study.
##3 cows will offer a better test of this


'''
we didn't add the commons condition "[[u'0', u'0', u'0', u'3'], [u'0.25', u'0.25', u'0.25', u'0.25']]"
until 12/09/2015
'''

