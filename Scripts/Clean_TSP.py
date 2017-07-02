'''
Code created to analyze the TSP data for the replication paper.  It is based on earlier, reporting code called TSPclean.py.

Date Created: January 14, 2015

'''
import csv
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde,ttest_ind
from matplotlib import pyplot as pp
import urllib
from httplib2 import Http
import datetime as dt
import json, ast, re
from collections import Counter


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


def importMapData():
    maps_file='C:\Data\Lazer Data\VS\maps_20.txt'
    with open(maps_file,'rb') as f:
        map_text = f.read().split(';\n')
        
    maps_difficulty_file='C:\Data\Lazer Data\VS\maps_convexHull.txt'
    with open(maps_difficulty_file,'rb') as f:
        map_hull_num = dict([(int(idx),int(dif)) for (idx,dif) in [a.split(',') for a in f.read().split('\n')]])
    
    mapdata = dict()
    for line in map_text:
        if len(line) > 0:
            split_text = line.split(' = ')
            map_id = re.findall(r'map\[(\d+)\]',split_text[0])[0]
            map_best_distance = ast.literal_eval(split_text[1])[2][0]
            seq=ast.literal_eval(split_text[1])[1]
            #labels = ['positions','order','solution']
            #zipped = dict(zip(labels,map_values))
            mapdata[int(map_id)] = [int(map_best_distance),map_hull_num[int(map_id)],seq]
    return mapdata

def Compare(points1,points2):
    '''
    Compares number of edges correct
    '''
    edge1=[]
    edge2=[]
    for i,p in enumerate(points1):
        if i!=0:
            edge1.append([last1,p])
            edge2.append([last2,points2[i]])
        last1=p
        last2=points2[i]
            
    count=0
    for e in edge1:
        if e in edge2 or [e[1],e[0]] in edge2:
            count+=1
    #highest possible is 19
    return count

def cleanTSP(data,mapdata):
    '''This turns the TSP json data into a flat file where each row represents a round for a person for a game.
    It excludes multiplayer games'''
    
    subTranslate={'desktop':1,'mobile':2,'tablet':3,'male':1,'female':0}
    gameSubjectsDict={}
    gameMeta={}
    flatData=[]
    seconds=set()
    subjects=set()
    incompletes=0.0
    repeats=0.0
    mobile=0.0
    for num,line in enumerate(data):
        
        #Mobile users are excluded here.
        if line['variables']['num_cities']!='20':
            mobile+=1
            continue
        
        #Check for non-consent. Shouldn't happen
        if line['subjects'][0]['consent']==False:
            continue
        
        
        #gather subject demographics
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
        
        gameid=str(line['id'])
        date=line['date']
        
        
        if len(line['submissions'])>0:
            gameMeta[gameid]=[]           
            for i,sub in enumerate(line['submissions']):
                rndData={}
                rndid=int(sub['round'])
                #this is only for game-specific variables
                if rndid==0:
                    continue
                #only use data from the first round
                elif rndid==101:
                    map_id=int(sub['val']['solution']['map'])
                    #if map_id>90: print line
                    hull=mapdata[map_id][1]
                    #if hull==15:
                    #    print map_id,int(sub['val']['solution']['dist']),line['subjects']
                    if int(sub['val']['solution']['dist'])>0:
                        score=(int(sub['val']['solution']['dist'])-mapdata[map_id][0])/float(mapdata[map_id][0])
                        accuracy=Compare(ast.literal_eval(sub['val']['solution']['#text']),tuple(mapdata[map_id][2]))
                    else:
                        incompletes+=1
                        continue
                        #score=''
                        #accuracy=''
                    if 'keys' not in rndData.keys():
                        rndData['keys']=sub.keys()+sub['val']['solution'].keys()
                        rnkeys=sub.keys()+sub['val']['solution'].keys()
                    rndData[gameid+'_'+str(rndid)]=sub.values()+sub['val']['solution'].values()
                    flatRow=[date,gameid,score,hull,accuracy,gender,age,device]+sub.values()+sub['val']['solution'].values()#+gameMeta[gameid]+subjectData[sub['subject']]
                    flatData.append(flatRow)
    for i,line in enumerate(flatData):
        ditems=[j for j,item in enumerate(line) if type(item)==dict]
        flatData[i]=[item for item in line if type(item) != dict]
    flatKeys=['date','gameid','score','hull','correct','gender','age','device']+rnkeys#+gameMeta['keys']+subjectData['keys']
    flatKeys=[item for i,item in enumerate(flatKeys) if i not in ditems]
    #metaData={'gameMeta':[k for k in gameMeta['keys'] if type(k) != dict],'subjectMeta':[k for k in subjectData['keys'] if type(k) != dict],'rndMeta':[k for k in rnkeys if type(k) != dict]}
    fdata=[flatKeys]+flatData
    
    names=['gameid','person','condition','avg_user_choices','avg_bot_choices','gender','age','device']    
     
    print 'TSP - number of original games = ', len(data)
    print 'TSP - number games excluded for mobile = ',  mobile, round(mobile/len(data),3)*100, 'percent'
    print 'TSP - number games excluded for incompleteness = ', incompletes, round(incompletes/len(data),3)*100, 'percent'
    print 'TSP - number of final cases in the analysis = ', len(flatData),round(float(len(flatData))/len(data),3)*100, 'percent'
    
    writeCleanData(fdata,outfile='TSP')
    
    return fdata



data=importData('Raw_Data/TSP.json')
mapdata=importMapData()
data=cleanTSP(data,mapdata)
