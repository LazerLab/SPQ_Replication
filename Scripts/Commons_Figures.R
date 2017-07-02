
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

#Commons - 439 0.65444191344 0.630882644207 0.678001182672

points(4,.65, ylim=c(0,1),xlim=c(.5,4.25))
segments(4,.629, x1=4,y1=.675,pch='|')
points(c(4,4),c(.629,.675),pch='-',cex=2)

axis(1,at=c(1,2,3,4),labels=c('Barn','Lean\nBarn','Lean\nCommons', 'Commons'),padj=.3)
dev.off()




########################################################################
#                                   TSP
##########################################################################

dta <- read.data('C://Data//Lazer Data//VS//TSP//Data//01-14-2015_TSP_All.csv',




