
import numpy as np
import csv
import json

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



def cleanCows(data):
    '''Takes raw json data and generates a flat-file structure of person-id-submissions '''
    
    Results=[]
    
    subjects=set()
    incompletes=0.0
    multiplayer=0.0
    repeats=0.0
    
    comTrans={"Barn Feed":0,"Bring to Commons":1}
    subTranslate={'desktop':1,'mobile':2,'tablet':3,'male':1,'female':0}
    
    payoffs=set([str(c['matrices']['payoff']) for c in data])
    conditions={"[[u'-1', u'0', u'0', u'1'], [u'0.75', u'0.75', u'0.75', u'0.75']]": 'barn',
                "[[u'-1', u'0', u'0', u'1'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'leanBarn',
                "[[u'-1', u'0', u'0', u'3'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'leanCommons',
                "[[u'0', u'0', u'0', u'3'], [u'0.25', u'0.25', u'0.25', u'0.25']]": 'commons'}
    
    #iterate through each game and generate data
    for idx,game in enumerate(data):
        line=[]
        #Check for incorrect payoff matrix. Shouldn't happen.
        if str(game['matrices']['payoff']) not in conditions.keys():
            print 'missing this payoff: ', idx,str(game['matrices']['payoff'])
            continue
        #Check for non-consent. Shouldn't happen
        if game['subjects'][0]['consent']==False:
            continue
                
        
        #Exclude multiplayer cases.
        if len(game['subjects'])>1:
            multiplayer+=1
            continue
        
        #Exclude players who started a game but never made it past instructions
        if len(game['submissions'])<3:  
            incompletes+=1
            continue
        
        #Exclude repeats
        if game['subjects'][0]['uid'] not in subjects:
            subjects.update([game['subjects'][0]['uid']])
        else:
            repeats+=1
            continue
        
        gameid=game['id']
        position=str(game['subjects'][0]['id'])
        person = str(game['subjects'][0]['uid'])
        
        #gather subject demographics
        try:
            gender=subTranslate[game['subjects'][0]['gender']]
        except:
            gender=''
        try:
            age=int(game['subjects'][0]['age-bin'])
        except:
            age=''
        try:
            device=subTranslate[game['subjects'][0]['device']]
        except:
            device=''        
        
        #gather game metadata
        opps=sum([position in a['#text'] for a in game['submissions'][0]['val']['activePlayers']])
        cond=conditions[str(game['matrices']['payoff'])]
        
        answers=[]
        oanswers=[]
        
        round_timer=int(game['variables']["experiment_round_timer"])                 
        results_timer=int(game['variables']["result_timer"])
        rnds=[int(a['expRound']) for a in game['submissions'][0]['val']['activePlayers'] if position in a['#text']]
        readyRound=[int(g['round']) for g in game['submissions'] if g['val']=='Ready'][0]
        #iterate through each round
        for index,g in enumerate(game['submissions']):
            if int(g['round'])-readyRound in rnds:  #if round is a game round
                if g['val']=='+30 Seconds':         #if +30 seconds, then player took extra time in instructions.
                    readyRound+=1
                    continue
                
                #if player exceeds time, the decision is made for them. So exclude them from the sample.
                if int(g['round'])-readyRound==1: 
                    maxtime=round_timer
                else:   #if not the first round, max time is previous time plus time given for evaluating results.
                    maxtime=round_timer+results_timer
                    
                time_taken=g['time']-game['submissions'][index-1]['time']
                
                if time_taken>maxtime:
                    #print 'found a lapsed player'
                    answers.append(np.nan)
                    continue
                
                #g=game['submissions'][int(rnd)+2-1]
                for answer in g['val']['answer']:
                    if type(answer)==unicode:       #one game has an odd unicode error
                        #print g
                        continue
                    if answer['subject']==position:
                        answers.append(comTrans[answer['#text']])    #is player's answer
                    else:
                        oanswers.append(comTrans[answer['#text']])   #is the bot's answer, used to see if differences in average bot behavior affects players' choice

        
        mAnswer=np.mean(answers)    #player's average answer across all rounds
        if np.isnan(mAnswer):       #if there's a text value in the list of answers
            incompletes+=1
            continue
        mothAnswer=np.mean(oanswers)
        line=[gameid,person,cond,mAnswer,mothAnswer,gender,age,device] 
        
        Results.append(line)
        
    names=['gameid','person','condition','avg_user_choices','avg_bot_choices','gender','age','device']
    
    print 'Cows - number of original games = ', len(data)
    print 'Cows - number games excluded for multiplayer = ',  multiplayer, round(multiplayer/len(data),3)*100, 'percent'
    print 'Cows - number games excluded for repeats = ',  repeats, round(repeats/len(data),3)*100, 'percent'
    print 'Cows - number games excluded for incompleteness = ', incompletes, round(incompletes/len(data),3)*100, 'percent'
    print 'Cows - number of final cases in the analysis = ', len(Results),round(float(len(Results))/len(data),3)*100, 'percent'
    #cdata=totals(cdata)
    cdata=[names]+Results
    writeCleanData(cdata,outfile='Commons_Dilemma')
    return cdata

data=importData('Raw_Data/Commons_Dilemma.json')
data=cleanCows(data)
