
'''

Completeness: 99% (run on test data, not on final data)
This code cleans the raw csv data for survey-based studies conducted for Radford et al and prints the
subject participation numbers reported in the study
'''
import csv


def directory_crawl(path,dfile):
    '''This code uses the file names of the csv to detect the survey being analyzed and exracts the cleaned data '''
    if "big" in dfile.lower() and 'five' in dfile.lower():
        return(cleanBigFive())
    
    if "africa" in dfile.lower():
        return(cleanAnchoringAfrica())
    
    if "trees" in dfile.lower():
        return(cleanAnchoringTrees())
    
    if "disease" in dfile.lower():
        return(cleanDiseaseProblem())
    
    if 'timed' in dfile.lower()and 'risk' in dfile.lower():
        return(cleanTimedRisk())
    
    if 'six' in dfile.lower() and 'figures' in dfile.lower():
        return(cleanSixFigures())
    
    if 'vignette' in dfile.lower():
        return(cleanImpressionVignette())
    
    if 'protestant' in dfile.lower():
        return(cleanPWC())
    
    if 'system' in dfile.lower() and 'just' in dfile.lower():
        return(cleanSystemJustification())
    


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

def cleanBigFive():
    '''
    Inputs:
        dfile is the raw csv file - 'Raw_Data/BigFive.csv'
    Outputs:
        clean csv file - 'Clean_Data/BigFive.csv'
    '''
    dfile = 'Raw_Data/BigFive.csv'
    output=[]
    
    #set variables to be used
    varids={}
    duplicates=set()
    dupCount=0
    flagCount=0.0
    incompletes=0.0
    bf={'tooQuick':0.0,'variance':0.0}
    
    #import raw csv
    with open(dfile,'rb') as f:
        data=csv.reader(f)
        for i,row in enumerate(data):
            if i==0:
                output.append(row+['ineligible'])
                for j,item in enumerate(row):
                    varids[item]=j              #save index for variables
            else:
                #create flags for data that is unusable (incomplete, bad, >1 time)
                flag=0
                #Check for bad data: too quick 
                if int(row[varids['timeSpent']])<60:
                    bf['tooQuick']+=1
                    flag=1
                
                #Check for bad data: zero variance.
                if len(set(row[1:45]))<2:
                    bf['variance']+=1
                    flag=1
                
                #Check for incomplete data.
                if '' in row[1:45]:
                    flag=1
                    incompletes+=1
                
                #Check if it's the person's first time.
                if row[varids['uid']] in duplicates:
                    flag=1
                    dupCount+=1
                else:
                    duplicates.update([row[varids['uid']]])
                
                flagCount+=flag
                output.append(row+[flag])
                
                
                
    #print the counts
    total=float(i)
    eligible=float(i-flagCount)
    print 'Big Five total = ', total      #subtract 2 header rows
    print 'Big Five eligible = ', eligible, round(eligible/total,3)*100, 'percent'
    print 'Big Five number incompletes = ', incompletes, round(incompletes/total,3)*100, 'percent'
    print 'Big Five number of duplicates = ', dupCount,round(dupCount/total,3)*100, 'percent'
    print 'Big Five number too quick = ', bf['tooQuick'], round(bf['tooQuick']/total,3)*100, 'percent'
    print 'Big Five number with zero variance = ', bf['variance'], round(bf['variance']/total,3)*100, 'percent'
    print 'Big Five - number of final cases in the analysis = ', eligible,round(float(eligible)/total,3)*100, 'percent'
    
    writeCleanData(output,outfile='BigFive')
    
    return #questions,results#,nonConsent#newquestions,valids


def cleanAnchoringAfrica():
    '''
    Inputs:
        dfile is the raw csv file - 'Raw_Data/Anchoring_Africa.csv'
    Outputs:
        clean csv file - 'Clean_Data/Anchoring_Africa.csv'
    '''
    dfile = 'Raw_Data/Anchoring_Africa.csv'
    output=[]
    
    varids={}
    duplicates=set()
    dupCount=0
    flagCount=0.0
    incompletes=0.0
    bf={'illogical':0.0}
    
    with open(dfile,'rb') as f:
        data=csv.reader(f)
        for i,row in enumerate(data):
            if i==0:
                output.append(row+['ineligible'])
                for j,item in enumerate(row):
                    varids[item]=j
            else:
                #create flags for data that is unusable (incomplete, bad, >1 time)
                flag=0
                
                #Check for incomplete data.
                if row[3]=='' or (row[1]=='' and row[2]==''):
                    flag=1
                    incompletes+=1
                
                #Check if it's the person's first time.
                if row[varids['uid']] in duplicates:
                    flag=1
                    dupCount+=1
                else:
                    duplicates.update([row[varids['uid']]])
                
                #Check for illogical data
                guess=row[3]
                if guess!='':
                    guess=int(guess)    #already flagged as incomplete
                    if row[1]=='' and row[2]=='2' and guess>11:
                        bf['illogical']+=1
                        flag=1
                    if row[1]=='' and row[2]=='1' and guess<13:
                        bf['illogical']+=1
                        flag=1
                    if row[2]=='' and row[1]=='2' and guess>64:
                        bf['illogical']+=1
                        flag=1
                    if row[2]=='' and row[1]=='1' and guess<66:
                        bf['illogical']+=1
                        flag=1
                    
                flagCount+=flag
                output.append(row+[flag])
    
    total=float(i)
    eligible=float(i-flagCount)
    print 'Anchoring Africa total = ', total      #subtract 2 header rows
    print 'Anchoring Africa eligible = ', eligible, round(eligible/total,3)*100, 'percent'
    print 'Anchoring Africa number incompletes = ', incompletes, round(incompletes/total,3)*100, 'percent'
    print 'Anchoring Africa number of duplicates = ', dupCount,round(dupCount/total,3)*100, 'percent'
    print 'Anchoring Africa number too quick = ', bf['illogical'], round(bf['illogical']/total,3)*100, 'percent'
    print 'Anchoring Africa - number of final cases in the analysis = ', eligible,round(float(eligible)/total,3)*100, 'percent'
     
    writeCleanData(output,outfile='Anchoring_Africa')
    return output


def cleanAnchoringTrees():
    '''
    Inputs:
        dfile is the raw csv file - 'Raw_Data/Anchoring_Trees.csv'
    Outputs:
        clean csv file - 'Clean_Data/Anchoring_Trees.csv'
    '''
    dfile = 'Raw_Data/Anchoring_Trees.csv'
    output=[]
    
    varids={}
    duplicates=set()
    dupCount=0
    flagCount=0.0
    incompletes=0.0
    bf={'illogical':0.0}
    
    with open(dfile,'rb') as f:
        data=csv.reader(f)
        for i,row in enumerate(data):
            if i==0:
                output.append(row+['ineligible'])
                for j,item in enumerate(row):
                    varids[item]=j
            else:
                #create flags for data that is unusable (incomplete, bad, >1 time)
                flag=0
                
                #Check for incomplete data.
                if row[3]=='' or (row[1]=='' and row[2]==''):
                    flag=1
                    incompletes+=1
                
                #Check if it's the person's first time.
                if row[varids['uid']] in duplicates:
                    flag=1
                    dupCount+=1
                else:
                    duplicates.update([row[varids['uid']]])
                
                #Check for illogical data
                guess=row[3]
                if guess!='':
                    guess=float(guess)    #already flagged as incomplete
                    if row[1]=='' and row[2]=='2' and guess>999:
                        bf['illogical']+=1
                        flag=1
                    if row[1]=='' and row[2]=='1' and guess<1001:
                        bf['illogical']+=1
                        flag=1
                    if row[2]=='' and row[1]=='2' and guess>84:
                        bf['illogical']+=1
                        flag=1
                    if row[2]=='' and row[1]=='1' and guess<86:
                        bf['illogical']+=1
                        flag=1
                flagCount+=flag
                output.append(row+[flag])
    
    total=float(i)
    eligible=float(i-flagCount)
    print 'Anchoring Trees total = ', total      #subtract 2 header rows
    print 'Anchoring Trees eligible = ', eligible, round(eligible/total,3)*100, 'percent'
    print 'Anchoring Trees number incompletes = ', incompletes, round(incompletes/total,3)*100, 'percent'
    print 'Anchoring Trees number of duplicates = ', dupCount,round(dupCount/total,3)*100, 'percent'
    print 'Anchoring Trees number illogical = ', bf['illogical'], round(bf['illogical']/total,3)*100, 'percent'
    print 'Anchoring Trees - number of final cases in the analysis = ', eligible,round(float(eligible)/total,3)*100, 'percent'
    
    writeCleanData(output,outfile='Anchoring_Trees')
    return output


def cleanDiseaseProblem():
    '''
    Inputs:
        dfile is the raw csv file - 'Raw_Data/Disease_Problem.csv'
    Outputs:
        clean csv file - 'Clean_Data/Disease_Problem.csv'
    '''
    dfile = 'Raw_Data/Disease_Problem.csv'
    output=[]
    
    varids={}
    duplicates=set()
    dupCount=0
    flagCount=0.0
    incompletes=0.0
    with open(dfile,'rb') as f:
        data=csv.reader(f)
        for i,row in enumerate(data):
            if i==0:
                output.append(row+['ineligible'])
                for j,item in enumerate(row):
                    varids[item]=j
            else:
                #create flags for data that is unusable (incomplete, bad, >1 time)
                flag=0
                #find incompletes
                if row[1]=='' and row[2]=='':
                    flag=1
                    incompletes+=1
                #Find duplicate participants
                if row[varids['uid']] in duplicates:
                    flag=1
                    dupCount+=1
                else:
                    duplicates.update([row[varids['uid']]])
                    
                flagCount+=flag
                output.append(row+[flag])
    
    total=float(i)
    eligible=float(i-flagCount)
    print 'Disease Problem total = ', total      #subtract 2 header rows
    print 'Disease Problem eligible = ', eligible, round(eligible/total,3)*100, 'percent'
    print 'Disease Problem number incompletes = ', incompletes, round(incompletes/total,3)*100, 'percent'
    print 'Disease Problem number of duplicates = ', dupCount,round(dupCount/total,3)*100, 'percent'
    print 'Disease Problem - number of final cases in the analysis = ', eligible,round(float(eligible)/total,3)*100, 'percent'
    
    writeCleanData(output,outfile='Disease_Problem')
    return output


def cleanTimedRisk():
    '''
    Inputs:
        dfile is the raw csv file - 'Raw_Data/Timed_Risk_Reward.csv'
    Outputs:
        clean csv file - 'Clean_Data/Timed_Risk_Reward.csv'
    '''
    dfile = 'Raw_Data/Timed_Risk_Reward.csv'
    output=[]
    
    varids={}
    duplicates=set()
    dupCount=0
    flagCount=0.0
    incompletes=0.0
    bf={'variance':0.0}
    with open(dfile,'rb') as f:
        data=csv.reader(f)
        for i,row in enumerate(data):
            if i==0:
                output.append(row+['ineligible'])
                for j,item in enumerate(row):
                    varids[item]=j
            else:
                #create flags for data that is unusable (incomplete, bad, >1 time)
                flag=0
                
                #Find incompletes
                if '' in row[1:9]:
                    incompletes+=1
                    flag=1
                
                #Find duplicates
                if row[varids['uid']] in duplicates:
                    flag=1
                    dupCount+=1
                else:
                    duplicates.update([row[varids['uid']]])
                
                #Find people just clicking the same answer
                if len(set(row[1:45]))<2:
                    bf['variance']+=1
                    flag=1 
                flagCount+=flag
                output.append(row+[flag])

    total=float(i)
    eligible=float(i-flagCount)
    print 'Timed Risk Reward total = ', total      #subtract 2 header rows
    print 'Timed Risk Reward eligible = ', eligible, round(eligible/total,3)*100, 'percent'
    print 'Timed Risk Reward number incompletes = ', incompletes, round(incompletes/total,3)*100, 'percent'
    print 'Timed Risk Reward number of duplicates = ', dupCount,round(dupCount/total,3)*100, 'percent'
    print 'Timed Risk Reward number with zero variance = ', bf['variance'], round(bf['variance']/total,3)*100, 'percent'
    print 'Timed Risk Reward - number of final cases in the analysis = ', eligible,round(float(eligible)/total,3)*100, 'percent'
    
    writeCleanData(output,outfile='Timed_Risk_Reward')
    return output


def cleanSixFigures():
    '''
    Inputs:
        dfile is the raw csv file - 'Raw_Data/Six_Figures.csv'
    Outputs:
        clean csv file - 'Clean_Data/Six_Figures.csv'
    '''
    dfile = 'Raw_Data/Six_Figures.csv'
    output=[]
    
    varids={}
    duplicates=set()
    dupCount=0
    flagCount=0.0
    incompletes=0.0
    bf={'tooQuick':0.0}
    
    with open(dfile,'rb') as f:
        data=csv.reader(f)
        for i,row in enumerate(data):
            if i==0:
                output.append(row+['ineligible'])
                for j,item in enumerate(row):
                    varids[item]=j
            else:
                #create flags for data that is unusable (incomplete, bad, >1 time)
                flag=0
                
                #Find incompletes
                if sum([''!=r for r in row[1:17]])<3:
                    incompletes+=1
                    flag=1
                
                #Find duplicates
                if row[varids['uid']] in duplicates:
                    flag=1
                    dupCount+=1
                else:
                    duplicates.update([row[varids['uid']]])
                
                #Find people just clicking the same answer
                if int(row[varids['timeSpent']])<10:
                    bf['tooQuick']+=1
                    flag=1 
                flagCount+=flag
                output.append(row+[flag])
    
    total=float(i)
    eligible=float(i-flagCount)
    print 'Six Figures total = ', total      #subtract 2 header rows
    print 'Six Figures eligible = ', eligible, round(eligible/total,3)*100, 'percent'
    print 'Six Figures number incompletes = ', incompletes, round(incompletes/total,3)*100, 'percent'
    print 'Six Figures number of duplicates = ', dupCount,round(dupCount/total,3)*100, 'percent'
    print 'Six Figures number too quick = ', bf['tooQuick'], round(bf['tooQuick']/total,3)*100, 'percent'
    print 'Six Figures - number of final cases in the analysis = ', eligible,round(float(eligible)/total,3)*100, 'percent'
    
    
    writeCleanData(output,outfile='Six_Figures')
    return output

def cleanJustWorldVignette():
    '''
    Inputs:
        dfile is the raw csv file - 'Raw_Data/JW_Vignette.csv'
    Outputs:
        clean csv file - 'Clean_Data/JW_Vignette.csv'
    '''
    dfile = 'Raw_Data/JW_Vignette.csv'
    output=[]
    
    varids={}
    duplicates=set()
    dupCount=0
    flagCount=0.0
    incompletes=0.0
    
    with open(dfile,'rb') as f:
        data=csv.reader(f)
        for i,row in enumerate(data):
            if i==0:
                output.append(row+['ineligible'])
                for j,item in enumerate(row):
                    varids[item]=j
            else:
                #create flags for data that is unusable (incomplete, bad, >1 time)
                flag=0
                
                #Find incompletes
                if sum([''==r for r in row[1:3]])>1:
                    incompletes+=1
                    flag=1
                
                #Find duplicates
                if row[varids['uid']] in duplicates:
                    flag=1
                    dupCount+=1
                else:
                    duplicates.update([row[varids['uid']]])
                flagCount+=flag
                output.append(row+[flag])

    total=float(i)
    eligible=float(i-flagCount)
    print 'Just World Vignette total = ', total      #subtract 2 header rows
    print 'Just World Vignette eligible = ', eligible, round(eligible/total,3)*100, 'percent'
    print 'Just World Vignette number incompletes = ', incompletes, round(incompletes/total,3)*100, 'percent'
    print 'Just World Vignette number of duplicates = ', dupCount,round(dupCount/total,3)*100, 'percent'
    print 'Just World Vignette - number of final cases in the analysis = ', eligible,round(float(eligible)/total,3)*100, 'percent'
    writeCleanData(output,outfile='JW_Vignette')
    return output


def cleanPWE():
    '''
    Inputs:
        dfile is the raw csv file - 'Raw_Data/JW_PWE.csv'
    Outputs:
        clean csv file - 'Clean_Data/JW_PWE.csv'
    '''
    
    dfile = 'Raw_Data/JW_PWE.csv'
    output=[]
    
    varids={}
    duplicates=set()
    dupCount=0
    flagCount=0.0
    incompletes=0.0
    bf={'tooQuick':0.0,'variance':0.0}
    
    with open(dfile,'rb') as f:
        data=csv.reader(f)
        for i,row in enumerate(data):
            if i==0:
                output.append(row+['ineligible'])
                for j,item in enumerate(row):
                    varids[item]=j
            else:
                #create flags for data that is unusable (incomplete, bad, >1 time)
                flag=0
                #Check for bad data: too quick 
                if int(row[varids['timeSpent']])<10:
                    bf['tooQuick']+=1
                    flag=1
                
                #Check for bad data: zero variance.
                if len(set(row[1:17]))<2:
                    bf['variance']+=1
                    flag=1
                    
                #Find incompletes
                if '' in row[1:17]:
                    incompletes+=1
                    flag=1
                
                #Find duplicates
                if row[varids['uid']] in duplicates:
                    flag=1
                    dupCount+=1
                else:
                    duplicates.update([row[varids['uid']]])
                
                flagCount+=flag
                output.append(row+[flag])
    
    
    total=float(i)
    eligible=float(i-flagCount)
    print 'JW PWE total = ', total      #subtract 2 header rows
    print 'JW PWE eligible = ', eligible, round(eligible/total,3)*100, 'percent'
    print 'JW PWE number incompletes = ', incompletes, round(incompletes/total,3)*100, 'percent'
    print 'JW PWE number of duplicates = ', dupCount,round(dupCount/total,3)*100, 'percent'
    print 'JW PWE number too quick = ', bf['tooQuick'], round(bf['tooQuick']/total,3)*100, 'percent'
    print 'JW PWE number with zero variance = ', bf['variance'], round(bf['variance']/total,3)*100, 'percent'
    print 'JW PWE - number of final cases in the analysis = ', eligible,round(float(eligible)/total,3)*100, 'percent'
    
    writeCleanData(output,outfile='JW_PWE')
    return output
    
    

def cleanSystemJustification():
    '''
    Inputs:
        dfile is the raw csv file - 'Raw_Data/JW_System_Justification.csv'
    Outputs:
        clean csv file - 'Clean_Data/JW_System_Justification.csv'
    '''
    
    dfile = 'Raw_Data/JW_System_Justification.csv'
    output=[]
    
    varids={}
    duplicates=set()
    dupCount=0
    flagCount=0.0
    incompletes=0.0
    bf={'tooQuick':0.0,'variance':0.0}
    
    with open(dfile,'rb') as f:
        data=csv.reader(f)
        for i,row in enumerate(data):
            if i==0:
                output.append(row+['ineligible'])
                for j,item in enumerate(row):
                    varids[item]=j
            else:
                #create flags for data that is unusable (incomplete, bad, >1 time)
                flag=0
                #Check for bad data: too quick 
                if int(row[varids['timeSpent']])<10:
                    bf['tooQuick']+=1
                    flag=1
                
                #Check for bad data: zero variance.
                if len(set(row[1:9]))<2:
                    bf['variance']+=1
                    flag=1
                    
                #Find incompletes
                if '' in row[1:9]:
                    incompletes+=1
                    flag=1
                
                #Find duplicates
                if row[varids['uid']] in duplicates:
                    flag=1
                    dupCount+=1
                else:
                    duplicates.update([row[varids['uid']]])
                
                flagCount+=flag
                output.append(row+[flag])
    
    
    total=float(i)
    eligible=float(i-flagCount)
    print 'JW System_Justification total = ', total      #subtract 2 header rows
    print 'JW System_Justification eligible = ', eligible, round(eligible/total,3)*100, 'percent'
    print 'JW System_Justification number incompletes = ', incompletes, round(incompletes/total,3)*100, 'percent'
    print 'JW System_Justification number of duplicates = ', dupCount,round(dupCount/total,3)*100, 'percent'
    print 'JW System_Justification number too quick = ', bf['tooQuick'], round(bf['tooQuick']/total,3)*100, 'percent'
    print 'JW System_Justification number with zero variance = ', bf['variance'], round(bf['variance']/total,3)*100, 'percent'
    print 'JW System_Justification - number of final cases in the analysis = ', eligible,round(float(eligible)/total,3)*100, 'percent'
    
    writeCleanData(output,outfile='JW_System_Justification')
    return output
    
    
cleanBigFive()
cleanAnchoringAfrica()
cleanAnchoringTrees()
cleanDiseaseProblem()
cleanTimedRisk()
cleanSixFigures()
cleanJustWorldVignette()
cleanPWE()
cleanSystemJustification()