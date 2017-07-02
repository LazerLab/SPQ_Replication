
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv#
#  VOLUNTEER SCIENCE: Big 5 Validation 
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv# 

 
# Data entry:

#setwd("Validation")

dat <- read.csv(file="Clean_Data//BigFive.csv", header=T,  as.is=T) 
labels <- read.csv(file="Clean_Data//BigFive_LABELS.csv", header=T,  as.is=T) 
 
head(dat)
head(labels)
dim(dat)
dim(labels)

colnames(dat)==labels$spss_var
colnames(dat) <- labels$r_var

# Check for repeating answers & missing data
apply(dat[,-1], 1, function(x) length(unique(x))==1)
sum(complete.cases(dat))

# Remove missing data
dat <- dat[complete.cases(dat),]

# Reverse-code the items that are reversed
dat[,labels$reverse==1] <- 6 - dat[,labels$reverse==1]


# We can exclude items that fit poorly before rerunning models:
# exclude <- c("A_fault", "O_routine", "O_unartistic")
# dat <- dat[, !(colnames(dat) %in% exclude)]

# Or exclude all reverse-coded items from the analysis: 
# dat <- dat[,labels$reverse==0] 


# FACTORS:

o_vars <- grep("^O_", colnames(dat), value=T)
n_vars <- grep("^N_", colnames(dat), value=T)
e_vars <- grep("^E_", colnames(dat), value=T)
a_vars <- grep("^A_", colnames(dat), value=T)
c_vars <- grep("^C_", colnames(dat), value=T)

dat <- dat[, sort(colnames(dat))]
head(dat)

# CRONBACH'S ALPHA:

require(psych)

alpha(dat[,o_vars])
alpha(dat[,n_vars])
alpha(dat[,e_vars])
alpha(dat[,a_vars])
alpha(dat[,c_vars])

detach(package:psych)


# CONFIRMATORY FACTOR ANALYSIS

require(lavaan)

# Correlated factor model:
cfa.model <- paste0( "open =~ ", paste(o_vars, collapse=" + "), " \n",
                     "neuro =~ ", paste(n_vars, collapse=" + "), " \n",
                     "extra =~ ", paste(e_vars, collapse=" + "), " \n",
                     "agree =~ ", paste(a_vars, collapse=" + "), " \n",
                     "consc =~ ", paste(c_vars, collapse=" + ")  )
cat(cfa.model)

# Estimate model fit (correlated factors):
fit <- cfa(cfa.model, data = dat, std.lv=T, std.ov=T)
summary(fit, fit.measures = TRUE, standardize = TRUE)

# Orthogonal factors:
fit.ort <- cfa(cfa.model, data = dat, orthogonal = TRUE, std.lv=T, std.ov=T)
summary(fit.ort, fit.measures = TRUE, standardize = TRUE)


detach(package:lavaan)

# CFA plots

library(semPlot)

semPaths(fit, what="std", layout="circle2", edge.label.cex=.6, curvePivot = TRUE, 
         exoVar = FALSE, exoCov = FALSE, edge.color="black") 

semPaths(fit.ort, what="std", layout="circle2", edge.label.cex=.6, curvePivot = TRUE, 
         exoVar = FALSE, exoCov = FALSE, edge.color="black")

detach(package:semPlot)
 

# O_routine & O_unartistic have low factor loading - .19 & .23 


# EXPLORATORY FACTOR ANALYSIS

library(nFactors)

# Scree plot
ev <- eigen(cor(dat[,-45])) # get eigenvalues
ap <- parallel(subject=nrow(dat[,-45]),var=ncol(dat[,-45]), rep=100,cent=.05)
nS <- nScree(x=ev$values, aparallel=ap$eigen$qevpea)
plotnScree(nS) 

detach(package:nFactors)


library(psych)

# Principal components
fit.pc <- princomp(dat[,-45], cor=T)
summary(fit.pc)  
loadings(fit.pc) 
plot(fit.pc ,type="lines")  
fit.pc$scores  
biplot(fit.pc) 

# Varimax rotated principal components 
fit.vrpc <- principal(dat[,-45], nfactors=5, rotate="varimax")
fit.vrpc # print results 
print(fit.vrpc, digits=2, cutoff=.30, sort=F)

# Maximum likelihood factor analysis
fit.mlfa <- factanal(dat[,-45], 5, rotation="varimax")
print(fit.mlfa, digits=2, cutoff=.40, sort=F)


output <- as.data.frame(round(unclass(fit.mlfa$loadings), 2))
colnames(output) <- c("Extraversion","Openness","Conscientiousness","Neuroticism","Agreeableness")
rownames(output) <- sub("(.)_(.)(.*$)", "\\U\\2\\L\\3 (\\U\\1)", rownames(output), perl=T )
output$Mean <- round(colMeans(dat[,1:44]),2)
output$SD <- round(apply(dat[,1:44],2,sd),2)
write.csv(output, "EFA_results_factor_loadings.csv")

detach(package:psych)
 
# Poor loadings: A_fault, O_routine,  O_unartistic 



####vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv####


