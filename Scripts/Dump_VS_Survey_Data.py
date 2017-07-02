
'''
Dump_VS_Survey_Data.py

This code calls the VS api and dumps all the relevant survey data into a json file

'''


import json
import urllib
import httplib2
import os


def apiCall(params,gameNum):
    tok='9eb10bd50a56c89825ab6bcccffb76ebd81b0d62'
    url='http://volunteerscience.com/data/'+gameNum+'/?format=json&'+urllib.urlencode(params)+'&token='+tok
    client=httplib2.Http(disable_ssl_certificate_validation=True)
    content = client.request(url,method='GET',body='')
    data = json.loads(content[1])['tests']
    return data

def getFiles(fname):
    fname='C:\Data\Lazer Data\VS\\'+fname+'.json'
    print fname
    with open(fname,'rb') as f:
        a=f.read()
    data=json.loads(a)
    return data['tests']


def SurveyMetaData(gameData, name):
    users=[]
    gameids=[]
    userdict={}
    nonconsents=0.0
    for line in gameData:
        for s in line['subjects']:
            if s['consent']!=False:
                if 'age-bin' in s.keys():
                    if s['age-bin']<3:
                        nonconsents+=1
                        continue
                users.append(s['uid'])
                gameids.append(str(line['id']))
                userdict[str(line['id'])]=s['uid']  #note only works for single player game.
            else:
                nonconsents+=1
    print name,'-  number excluded for nonconsents = ',  nonconsents, round(nonconsents/len(gameData),3), 'percent' 
    return gameids,users,userdict


def getData(games,params):
   
        #gameids,users,udict=SurveyMetaData(data[g],g)
        #userdict.update(udict)
        #consented_games[g]=gameids
        #Users[g]=users
    return 



games={'BigFive':'114','Cognitive Reflection':'96','Decision Problems':'94','Random':'104','Reciprocity':'110',
       'Timed Risk-Reward':'168','justicia':'173','Protestant Work Ethic':'177','System Justification':'178','Vignette':'176','Six Figures':'171'}    
params=[('amt','exclude'),('pi','exclude'),('variables','all'),('demonstration','exclude'),('start','01/01/2014'),('end','12/31/2015')]#dt.date.strftime(dt.date.today(),"%m/%d/%Y"))]


for name,num in games.iteritems():
    print '\n'+g.upper() + '\n'
    data=apiCall(params,num)
    with open('Dump_Data/'+name+'.json','wb') as f:
        json.dump(data,f)
#
#path='C:\Data\Lazer Data\VS\SurveyData\Raw'
#for dfile in os.listdir(path):
#    print dfile
#    if '.' in dfile:
#        questions, results=ex.directory(path,dfile,userdict)
#    

