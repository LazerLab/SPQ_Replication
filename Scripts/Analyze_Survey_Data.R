####################
#Code to clean data for the following studies:
#
#Study 2: Cognitive Bias and Heuristics
#   Disease_Problem     (Line 31)                  
#   Anchoring_Africa    (Line 76)                  <- NEED TO RE-RUN WITH FINAL DATA TO MAKE FIGURES WORK RIGHT
#   Anchoring_Trees     (Line 127)                  <- NEED TO RE-RUN WITH FINAL DATA TO MAKE FIGURES WORK RIGHT
#   Timed_Risk_Reward   (Line 183)
#
#Study 3: Big Five Survey   (Line 235)
#
#Study 4: Justice and Group Influence
#   Complementary Justice   #Continue working after finalizing the timing script which adds 'chain' variable to clean csvs.
#   Group Influence         #Redo this study with the final data. I'm not sure which functions were actually used for the final results
#
#Study 6: Social Dilemmas
#   Just generates the visualizations for these studies
#
# MAYBE THE TSP? its at the end now
#
#DON'T FORGET TO SET THE DIRECTORY
####################

setwd('C:/Data/Lazer Data/VS/Validation Scripts')


####################################################################################################
########################### STUDY 2 - COGNITIVE BIASES AND HEURISTICS ##############################
####################################################################################################

###################### DISEASE PROBLEM

#import data
dta <- read.table('Clean_Data//Disease_Problem.csv', sep=',' , header=TRUE , as.is=TRUE , quote='"')
colnames(dta)<-c('id','saved','dead','timeSpent','uid','ineligible')

#identify experimental condition
dta$condition<-NA
dta$condition[is.na(dta$saved)]<-1
dta$condition[is.na(dta$dead)]<-0

sdta<-subset(dta,dta$ineligible==0)

sdta$choice<-NA
sdta$choice<-rowSums(cbind(sdta$saved,sdta$dead),na.rm=T)

### REPORTED TEST STATISTIC
mod<-fisher.test(sdta$choice,sdta$condition)
print('Test for Disease Problem')
print(prop.table(table(dta$condition,dta$choice),1))
print(mod)


#### PLOT OF MEANS (NOT PUBLISHED IN PAPER)
jpeg('Images//Fig_3_Disease_Problem.jpg')
smean<-mean(sdta$saved[sdta$condition==0],na.rm=T)
dmean<-mean(sdta$dead[sdta$condition==1],na.rm=T)
#barplot(c(smean,dmean),xaxt='n',yaxt='n',add=T,xlab="", ylab="",xlim=c(-.3,1.3),ylim=c(.8,2.2))
plot(0,smean,xlim=c(-.3,1.3),ylim=c(.8,2.2),
    xlab="Experimental Condition",xaxt='n',ylab='Option Chosen',yaxt='n',main='Disease Problem')
points(1,dmean)
axis(1,at=c(0,1),labels=c('Lives-Saved Framing','Deaths-Prevented Framing'))
axis(2,at=c(1,2),labels=c('Certain Effects','Probabilistic Effects'))
conf1<-1.96*(sd(sdta$saved[sdta$condition==0],na.rm=T)/(sum(sdta$saved[sdta$condition==0],na.rm=T)/2))
conf2<-1.96*(sd(sdta$dead[sdta$condition==1],na.rm=T)/(sum(sdta$dead[sdta$condition==1],na.rm=T)/2))
segments(0,smean-conf1,x1=0,y1=smean+conf1,pch='|')
segments(1,dmean-conf2,x1=1,y1=dmean+conf2,pch='|')
points(c(0,0,1,1),c(smean-conf1,smean+conf1,dmean-conf2,dmean+conf2),pch='-',cex=2)
dev.off()


###################### ANCHORING AFRICA

#NOTE - correct answer is 54.  As of 9/8/2015 twenty people have the exact right answer.
dta <- read.table('Clean_Data//Anchoring_Africa.csv', sep=',' , header=TRUE , as.is=TRUE , quote='"')
colnames(dta)<-c('id','highAnchor','lowAnchor','estimate','timeSpent','uid',"ineligible")

#values are '1' for more and '2' for less.
dta$anchor<-NA
dta$anchor[is.na(dta$highAnchor)==FALSE & is.na(dta$lowAnchor)==TRUE]<-1
dta$anchor[is.na(dta$highAnchor)==TRUE & is.na(dta$lowAnchor)==FALSE]<-0

dta$ineligible[dta$id==22243]<-1 #throw out an unfiltered test case - Estimate is 123123123
dta$ineligible[dta$estimate==54]<-1 #throw out cheaters - those who get it exactly right
dta$ineligible[dta$estimate>200]<-1 #throw out outlier estimates
sdta<-subset(dta,dta$ineligible==0)

print(c('Number of final cases = ', length(sdta$uid), 'mean is ', length(sdta$uid)/length(dta$uid)))
print(c('Number Outliers = ',sum(dta$estimate>200,na.rm=T),'mean is ',mean(dta$estimate>200,na.rm=T)))
print(c('Number Cheaters = ',sum(dta$estimate==54,na.rm=T),'mean is ',mean(dta$estimate==54,na.rm=T)))


mod<-aov(estimate~anchor,data=sdta)
print(summary(mod))
print('mean estimate for high anchor')
print(mean(sdta$estimate[sdta$anchor==1]))
print('mean estimate for low anchor')
print(mean(sdta$estimate[sdta$anchor==0]))


#### PLOT OF MEANS
jpeg('Images//Fig_1_Anchoring_Africa.jpg')
h1<-hist(sdta$estimate[sdta$anchor==1])
d1<-density(sdta$estimate[sdta$anchor==1])
h2<-hist(sdta$estimate[sdta$anchor==0])
d2<-density(sdta$estimate[sdta$anchor==0])


plot(h1,col=gray(.1,alpha=.9),xlab="Reported Number of Countries", ylab="Number of Respondents",xlim=c(0,150),ylim=c(0,70),main="Anchoring - African Countries in the UN")
plot(h2,col=gray(.5,alpha=.9),xlab="", ylab="",add=T)#xlim=c(0,100),add=T,main='')

mx=max(h1$counts,h2$counts)

par(new=T)
plot(d1,col=gray(.1),xlim=c(0,150),xlab="", ylab="",yaxt='n',main='')#yaxes=F)
par(new=T)
plot(d2,col=gray(.1),xlim=c(0,150),xlab="", ylab="",yaxt='n',main='')#yaxes=F)
legend("topright",legend=c("Anchor-12 Countries","Anchor-65 Countries"),
  text.col=c(gray(.5),gray(.1)),col=c(gray(.5),gray(.1)))
dev.off()


###################### ANCHORING_TREES
#NOTE - correct answer is 379.3.  As of 9/8/2015 only  people have the exact right answer.

dta <- read.table('Clean_Data//Anchoring_Trees.csv', sep=',' , header=TRUE , as.is=TRUE , quote='"')
colnames(dta)<-c('id','lowAnchor','highAnchor','estimate','timeSpent','uid','ineligible')

dta$anchor<-NA
dta$anchor[is.na(dta$highAnchor)==FALSE & is.na(dta$lowAnchor)==TRUE]<-1
dta$anchor[is.na(dta$highAnchor)==TRUE & is.na(dta$lowAnchor)==FALSE]<-0

#eliminate guesses more than 3 standard deviations away from mean
outlier_cut<-mean(dta$estimate,na.rm=T)+(sd(dta$estimate,na.rm=T)*3)
#dta$ineligible[dta$id==28642]<-1  #toss out one outlier - person who guessed 1500 3x higher than any other guess
dta$ineligible[dta$estimate>(mean(dta$estimate,na.rm=T)+(sd(dta$estimate,na.rm=T)*3))]<-1
dta$ineligible[round(dta$estimate==379)]<-1

sdta<-subset(dta,dta$ineligible==0)

print(c('Number of final cases = ', length(sdta$uid), 'mean is ', length(sdta$uid)/length(dta$uid)))
print(c('Number Outliers = ',sum(dta$estimate>outlier_cut,na.rm=T),'mean is ',mean(dta$estimate>outlier_cut,na.rm=T)))
print(c('Number Cheating = ',sum(round(dta$estimate)==379,na.rm=T),'mean is ',mean(round(dta$estimate)==379,na.rm=T)))


mod<-aov(estimate~anchor,data=sdta)
print(summary(mod))
print('mean estimate for high anchor')
print(mean(sdta$estimate[sdta$anchor==1]))
print('mean estimate for low anchor')
print(mean(sdta$estimate[sdta$anchor==0]))


#### PLOT OF MEANS 
jpeg('Images//Fig_1_Anchoring_Trees.jpg')
h1<-hist(sdta$estimate[sdta$anchor==1],breaks=12)
d1<-density(sdta$estimate[sdta$anchor==1])
h2<-hist(sdta$estimate[sdta$anchor==0],breaks=12)
d2<-density(sdta$estimate[sdta$anchor==0])

plot(h1,col=gray(.1,alpha=.9),xlab="Estimated Height (feet)", ylab="Number of Respondents",xlim=c(0,2000),ylim=c(0,150),main="Anchoring - Height of the Tallest Redwood Tree")
plot(h2,col=gray(.5,alpha=.9),xlab="", ylab="",add=T)#xlim=c(0,100),add=T,main='')

par(new=T)
plot(d1,col=gray(.1),xlim=c(0,2000),xlab="", ylab="",yaxt='n',main='')#yaxes=F)
par(new=T)
plot(d2,col=gray(.1),xlim=c(0,2000),xlab="", ylab="",yaxt='n',main='')#yaxes=F)
legend("topright",legend=c("Anchor-85 Feet","Anchor-1000 Feet"),
  text.col=c(gray(.5),gray(.1)),col=c(gray(.5),gray(.1)))
dev.off()


###################### TIMED RISK-REWARD ANALYSIS 

dta <- read.table('Clean_Data///Timed_Risk_Reward.csv', sep=',' , header=TRUE , as.is=TRUE , quote='"')
colnames(dta)<-c('id','benbike','benbooze','benchem','benpest','riskbike','riskbooze','riskchem','riskpest','timeSpent','uid','ineligible')

dta<-subset(dta,dta$ineligible==0)
print(c('Number of cases for timed risk reward =',length(dta$id)))

print('Test global correlation')
d<-stack(dta)
cor.test(as.numeric(d$value[grep('ben',d$ind)]), as.numeric(d$value[grep('risk',d$ind)]))

#test individual correlations
bike<-cor.test(dta$benbike,dta$riskbike)
print('Bike Correlation')
print(bike)
#print(c('mean benefit bike',round(mean(dta$benbike,na.rm=T),3),'mean risk bike',round(mean(dta$riskbike,na.rm=T),3)))
#print(c('std benefit bike',round(sd(dta$benbike,na.rm=T),3),'std risk bike',round(sd(dta$riskbike,na.rm=T),3)))

booze<-cor.test(dta$benbooze,dta$riskbooze)
print('Alcohol Correlation')
print(booze)
#print(c('mean benefit booze',round(mean(dta$benbooze,na.rm=T),3),'mean risk booze',round(mean(dta$riskbooze,na.rm=T),3)))
#print(c('std benefit booze',round(sd(dta$benbooze,na.rm=T),3),'std risk booze',round(sd(dta$riskbooze,na.rm=T),3)))

chemical<-cor.test(dta$benchem,dta$riskchem)
print('Chemical Plants Correlation')
print(chemical)
#print(c('mean benefit chem',round(mean(dta$benchem,na.rm=T),3),'mean risk chem',round(mean(dta$riskchem,na.rm=T),3)))
#print(c('std benefit chem',round(sd(dta$benchem,na.rm=T),3),'std risk chem',round(sd(dta$riskchem,na.rm=T),3)))

pesticide<-cor.test(dta$benpest,dta$riskpest)
print('Pesticide Correlation')
print(pesticide)
#print(c('mean benefit pest',round(mean(dta$benpest,na.rm=T),3),'mean risk pest',round(mean(dta$riskpest,na.rm=T),3)))
#print(c('std benefit pest',round(sd(dta$benpest,na.rm=T),3),'std risk pest',round(sd(dta$riskpest,na.rm=T),3)))


#PLOT RESULTS
jpeg('Images//Fig_1_Timed_Risk_Reward.jpg')
plot(1,bike$estimate, ylim=c(-.5,.5),xlim=c(.5,4.5),
    main='Correlation of Risk and Reward',xaxt='n', xlab='',ylab="Risk-Reward Correlation (with 95% CI)")
segments(1,bike$conf.int[1],x1=1,y1=bike$conf.int[2],pch='|')
points(c(1,1),c(bike$conf.int[1],bike$conf.int[2]),pch='-',cex=2)

points(2,booze$estimate, ylim=c(-.5,.5),xlim=c(.5,4.5))
segments(2,booze$conf.int[1],x1=2,y1=booze$conf.int[2],pch='|')
points(c(2,2),c(booze$conf.int[1],booze$conf.int[2]),pch='-',cex=2)

points(3,chemical$estimate, ylim=c(-.5,.5),xlim=c(.5,4.5))
segments(3,chemical$conf.int[1],x1=3,y1=chemical$conf.int[2],pch='|')
points(c(3,3),c(chemical$conf.int[1],chemical$conf.int[2]),pch='-',cex=2)

points(4,pesticide$estimate, ylim=c(-.5,.5),xlim=c(.5,4.5))
segments(4,pesticide$conf.int[1],x1=4,y1=pesticide$conf.int[2],pch='|')
points(c(4,4),c(pesticide$conf.int[1],pesticide$conf.int[2]),pch='-',cex=2)

axis(1,at=c(1,2,3,4),labels=c('Bicycles','Alcohol','Chem. Plants','Pesticides'))

abline(0,0)
dev.off()

####################################################################################################
########################### STUDY 3 - BIG FIVE PERSONALITY INVENTORY ###############################
####################################################################################################


dat <- read.csv(file="Clean_Data//BigFive.csv", header=T,  as.is=T) 
labels <- read.csv(file="Clean_Data//BigFive_LABELS.csv", header=T,  as.is=T) 
 
#head(dat)
#head(labels)
#dim(dat)
#dim(labels)

#colnames(dat)==labels$spss_var
colnames(dat) <- labels$r_var

# Remove Ineligible data
dat<-subset(dat,dat$ineligible==0)

# Reverse-code the items that are reversed
dat[,labels$reverse==1] <- 6 - dat[,labels$reverse==1]


# FACTORS:

o_vars <- grep("^O_", colnames(dat), value=T)
n_vars <- grep("^N_", colnames(dat), value=T)
e_vars <- grep("^E_", colnames(dat), value=T)
a_vars <- grep("^A_", colnames(dat), value=T)
c_vars <- grep("^C_", colnames(dat), value=T)

dat <- dat[, sort(colnames(dat))]
head(dat)

#####################
# CRONBACH'S ALPHA:
#####################
require(psych)

alpha(dat[,o_vars]) #Openness
alpha(dat[,n_vars]) #Neuroticism
alpha(dat[,e_vars]) #Extraversion
alpha(dat[,a_vars]) #Agreeableness
alpha(dat[,c_vars]) #Conscientiousness

detach(package:psych)


# EXPLORATORY FACTOR ANALYSIS
# SCREE PLOT (NOT PUBLISHED IN PAPER)
library(nFactors)

# Scree plot
ev <- eigen(cor(dat[,c(-27,-46,-47,-48)])) # get eigenvalues
ap <- parallel(subject=nrow(dat[,c(-27,-46,-47,-48)]),var=ncol(dat[,c(-27,-46,-47,-48)]), rep=100,cent=.05)
nS <- nScree(x=ev$values, aparallel=ap$eigen$qevpea)
plotnScree(nS) 

detach(package:nFactors)


##########################
# REPORTED FIT
##########################
library(psych)

# Varimax rotated principal components 
sdat<-subset(dat, select=-c(ineligible,uid,timeSpent,testID))
fit.vrpc <- principal(sdat, nfactors=5, rotate="varimax") 
print(fit.vrpc, digits=2, cutoff=.30, sort=F)

# Maximum likelihood factor analysis
fit.mlfa <- factanal(sdat, 5, rotation="varimax")
print(fit.mlfa, digits=2, cutoff=.40, sort=F)

output <- as.data.frame(round(unclass(fit.mlfa$loadings), 2))
rownames(output) <- sub("(.)_(.)(.*$)", "\\U\\2\\L\\3 (\\U\\1)", rownames(output), perl=T )
output$Mean <- round(colMeans(sdat),2)
output$SD <- round(apply(sdat,2,sd),2)
write.csv(output, "Images//Table_2_Big_Five_Factor_Loadings.csv")

detach(package:psych)



####################################################################################################
########################### STUDY 4 - JUSTICE AND GROUP INFLUENCE ##################################
####################################################################################################


###################### SIX FIGURES ANALYSIS

###
# In all conditions, Figure E is always shown. In the incorrect conditions, Figures E and A are shown.
# In the correct conditions, Figures E and U are shown.
#
#
###
dta <- read.table('Clean_Data///Six_Figures.csv', sep=',' , header=TRUE , as.is=TRUE , quote='"')
colnames(dta)<-c('id','A1','E1','I1','O1','R1','U1','MajCor','MajIn','MinCor','MinIn','A2','E2','I2','O2','R2','U2',
    'timeSpent','uid','ineligible')
print(c('Number of original cases =',length(dta$id[dta$ineligible==0])))

#Recode the unselected answers to zero instead of missing
dta$A1[is.na(dta$A1)==T]<-0
dta$E1[is.na(dta$E1)==T]<-0
dta$I1[is.na(dta$I1)==T]<-0
dta$O1[is.na(dta$O1)==T]<-0
dta$R1[is.na(dta$R1)==T]<-0
dta$U1[is.na(dta$U1)==T]<-0
dta$A2[is.na(dta$A2)==T]<-0
dta$E2[is.na(dta$E2)==T]<-0
dta$I2[is.na(dta$I2)==T]<-0
dta$O2[is.na(dta$O2)==T]<-0
dta$R2[is.na(dta$R2)==T]<-0
dta$U2[is.na(dta$U2)==T]<-0

#Code the experimental condition
dta$Condition<-NA
dta$Condition[dta$MajCor==1]<-'MajCor'  #majority correct
dta$Condition[dta$MajIn==1]<-'MajIn'    #majority incorrect
dta$Condition[dta$MinIn==1]<-'MinIn'    #minority incorrect
dta$Condition[dta$MinCor==1]<-'MinCor'  #majority correct
dta$Condition<-as.factor(dta$Condition)

dta$Cor<-0
dta$Cor[dta$Condition=='MajCor'|dta$Condition=='MinCor']<-1
dta$Maj<-0
dta$Maj[dta$Condition=='MajCor'|dta$Condition=='MajIn']<-1


#First, do people who didn't have a correct response in the first round, pick it up when
#they see it in the correct condition more often than in the incorrect condition?

dta$precorrect<-dta$U1+dta$E1   #0 means they missed everything, 1 they missed one, 2 they got both correct
dta$postcorrect<-dta$U2+dta$E2
dta$change<-dta$postcorrect-dta$precorrect #Note, this can be negative if people change/forget a correct answer
sdta<-subset(dta,dta$precorrect<2)
fit<-aov(sdta$change~as.factor(sdta$Cor))
summary(fit)
print("Participants' likelihood of changing scores in incorrect and correct conditions")
prop.table(table(sdta$change,sdta$Cor),2)

####################
#Test of the first original finding: Do participants converge to majority opinion moreso than minority condition?
#This could mean two things: they converge to majority in the correct condition more
#than those in minority correct condition (i.e. converge only when correct)
#Or, this could mean they converge irrespective of whether majority is correct.
####################
####
#Do they converge irrespective of correctness?

#still using sdta which excludes players who got both U and E correct in the first round and so
#could not be effected by the treatment.
sdta$converge<-0
sdta$converge[sdta$Condition=='MajCor'&sdta$E2==1&sdta$U2==1]<-1
sdta$converge[sdta$Condition=='MajIn'&sdta$E2==1&sdta$A2==1]<-1
sdta$converge[sdta$Condition=='MinIn'&sdta$E2==1&sdta$A2==1]<-1
sdta$converge[sdta$Condition=='MinCor'&sdta$E2==1&sdta$U2==1]<-1

fit<-aov(sdta$converge~as.factor(sdta$Maj))
summary(fit)
print("Participants' likelihood of changing scores in incorrect and correct conditions")
prop.table(table(sdta$converge,sdta$Maj),1)

####
#Do they converge only in the correct conditions? (NOT REPORTED - Answer is no)
csdta<-subset(sdta,sdta$Cor==1)
fit<-aov(csdta$converge~as.factor(csdta$Maj))
summary(fit)
print("Participants' likelihood of changing scores in incorrect and correct conditions")
prop.table(table(csdta$converge,csdta$Maj),1)

####################
#Test of the second original finding: Do participants in the minority correct condition find
#more correct answers in the second round than subjects in the majority correct condition?
#
####################
dta$corbefore<-dta$E1+dta$I1+dta$R1+dta$U1 #number of correct responses in the first round
dta$incorbefore<-dta$A1+dta$O1          #number of incorrect responses in the first round
dta$beforeTotal<-dta$E1+dta$I1+dta$R1+dta$U1+dta$A1+dta$O1  #number of total responses in the first round
dta$corafter<-dta$E2+dta$I2+dta$R2+dta$U2  #number of correct responses in the second round
dta$incorafter<-dta$A1+dta$O1           #number of incorrect responses in the second round
dta$afterTotal<-dta$E2+dta$I2+dta$R2+dta$U2+dta$A1+dta$O1 #number of total responses in the second round
dta$gain<-dta$corafter-dta$corbefore

sdta<-subset(dta,(dta$corbefore<4&dta$Cor==1))  #exclude those who got every answer right in the first round and those in the incorrect conditions

fit<-aov(sdta$gain~as.factor(sdta$Maj))
summary(fit)
print("Participants' likelihood of changing scores in incorrect and correct conditions")
prop.table(table(sdta$gain,sdta$Maj),2)




###################### COMPLEMENTARY JUSTICE


vig<-read.table('Clean_Data//JW_Vignette.txt', sep=',' , header=TRUE , as.is=TRUE , quote='"')
vig$Condition<-NA
vig$Condition[vig$X12==1]<-'Non-Complementary'
vig$Condition[vig$X4==1]<-'Complementary'
vig<-vig[,c('Condition','uid','chain')]


pwc <- read.table('Clean_Data//JW_PWE.txt', sep=',' , header=TRUE , as.is=TRUE , quote='"')
pwc$pwcScore<-rowMeans(pwc[,2:17], na.rm = TRUE)
pwc<-pwc[,c('uid','pwcScore','chain')]


sj <- read.table('Clean_Data//JW_System_Justification.txt', sep=',' , header=TRUE , as.is=TRUE , quote='"')
sj$sjScore<-rowMeans(sj[,2:9], na.rm = TRUE)
sj <- sj[,c('sjScore','uid','chain','timeSpent')]

dta<-merge(pwc,sj,by=c("uid",'chain'))
dta<-merge(dta,vig,by=c("uid",'chain'))
dta<-subset(dta,is.na(dta$chain)==F)

dta$medpwc<-NA
dta$medpwc[dta$pwcScore<median(dta$pwcScore,na.rm=T)]<-0
dta$medpwc[dta$pwcScore>=median(dta$pwcScore,na.rm=T)]<-1
dta$medpwc<-as.factor(dta$medpwc)

########
# Preliminary Test 1: Protestant Work Ethic and System Justification are positively correlated
########

print("Correlation between Protestant Work Ethic and System Justification")
print(cor.test(dta$pwcScore,dta$sjScore))


#### Importing Reaction Times from Lexical Task
#Have to aggregate timing (it's round-level data), then merge

timing <- read.table('Clean_Data/JW_Reaction_Time.txt', sep=',' , header=TRUE , as.is=TRUE , quote='"')

#exclude incorrect and unreasonably slow rounds (2000 ms is two seconds)
timing$trash<-0
timing$trash[timing$reactTime>2000]<-1  #exclude extreme responses
timing$trash[timing$correct==0]<-1      #exclude incorrect rounds


#Create subject-level variables from round-level reaction time data:
#Add numValidRounds, 
s<-subset(timing,timing$trash==0)
ag<-aggregate(s$round,by=list(s$uid,s$chain),length)
colnames(ag)<-c('uid','chain','numValidRounds')
dta<-merge(dta,ag,by=c('uid','chain'))

#Add mean reaction time for neutral word stimuli
s<-subset(timing,(timing$justiceWord==0&timing$nonword==0))
ag<-aggregate(s$reactTime,by=list(s$uid,s$chain),mean)
colnames(ag)<-c('uid','chain','meanNeutral')
dta<-merge(dta,ag,by=c('uid','chain'))

#Add mean reaction time for justice word stimuli
s<-subset(timing,(timing$justiceWord==1))
ag<-aggregate(s$reactTime,by=list(s$uid,s$chain),mean)
colnames(ag)<-c('uid','chain','meanJustice')
dta<-merge(dta,ag,by=c('uid','chain'))

#Add mean reaction time for nonword stimuli
s<-subset(timing,(timing$nonword==1))
ag<-aggregate(s$reactTime,by=list(s$uid,s$chain),mean)
colnames(ag)<-c('uid','chain','meanNonword')
dta<-merge(dta,ag,by=c('uid','chain'))

########### ANALYSIS
#Only use those who answered all lexical rounds correctly in less than 2 seconds
#The problem with accepting people with errors is that the errors are dispersed
#unequally across conditions. People were more likely to incorrectly identify nonwords (87% accuracy)
#but were most likely to identify justice words (98% accuracy)

sdta<-subset(dta,dta$numValidRounds==15)

#Testing Effect on System Justification Score
mod<-aov(sjScore~Condition*medpwc,data=sdta)
summary(mod)
print(c('eta-squared=',summary.lm(mod)$r.squared))
print(model.tables(mod,'means'))

#Testing effect on justice reaction times
mod<-aov(log(meanJustice)~Condition*medpwc,data=sdta)
summary(mod)
print(model.tables(mod,'means'))



####################################################################################################
########################### STUDY 6 - SOCIAL DILEMMAS ##############################################
####################################################################################################


####################
#These figures were excluded in the final publication.
####################


#NOTE, HERE WE ONLY GENERATE THE FINAL IMAGEs BASED ON NUMBERS
#GENERATED BY THE SCRIPTS Analyze_PD.py AND Analyze_Commons.py


###################### COMMONS DILEMMA
jpeg('Images//Commons.jpg')

#Barn - 432 0.372685185185 0.345416837101 0.399953533269
plot(1,.372, ylim=c(0,1),xlim=c(.5,4.5),
    main='Average Choice in Commons Dilemma',xaxt='n', xlab='Prediction',ylab="Percent Choosing Commons")
segments(1,.345, x1=1,y1=.40,pch='|')
points(c(1,1),c(.345,.40),pch='-',cex=2)

#Lean Barn - 445 0.540031210986 0.516737466472 0.56332495550
points(2,.54, ylim=c(0,1),xlim=c(.5,4.25))
segments(2,.517, x1=2,y1=.563,pch='|')
points(c(2,2),c(.517,.563),pch='-',cex=2)

#Lean Commons - 453 0.612950699043 0.590304955179 0.635596442908
points(3,.61, ylim=c(0,1),xlim=c(.5,4.25))
segments(3,.59, x1=3,y1=.636,pch='|')
points(c(3,3),c(.59,.636),pch='-',cex=2)

#Commons - 448 0.652008928571 0.628704674571 0.675313182572
points(4,.65, ylim=c(0,1),xlim=c(.5,4.25))
segments(4,.629, x1=4,y1=.675,pch='|')
points(c(4,4),c(.629,.675),pch='-',cex=2)

axis(1,at=c(1,2,3,4),labels=c('Barn','Lean\nBarn','Lean\nCommons', 'Commons'),padj=.3)
dev.off()




########################################################################
#                                   TSP
##########################################################################

dta <- read.data('C://Data//Lazer Data//VS//TSP//Data//01-14-2015_TSP_All.csv',




