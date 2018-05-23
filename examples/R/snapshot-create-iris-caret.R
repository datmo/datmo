## Import data
library(datasets)

df <- iris
head(df) # View first few rows of dataset

## Fit Model
library(caret)

modFit <- train(Species ~., method = "rpart", data=df) #Fit model
print(modFit$finalModel)   #Summarize model text table)

# Visualize Results
library(rpart.plot)
rpart.plot(modFit$finalModel) #create decision tree visualization

#define model configuration to save
config<- paste(sep="",
  "method:", modFit$method)
 # "modelType"= modFit$modelType)

#define metrics to save
stats<- paste(sep="",
  "Accuracy:", modFit$results$Accuracy[1])
  #"Kappa"= modFit$results$Kappa[1]) 

# Create snapshot with configuration and stats
system2("datmo", 
        args=paste("snapshot create", 
          "-m 'a full snapshot'", 
          '--config', config,
          '--stats', stats))
# system2("datmo", args=paste("snapshot create -m 'an inline snapshot' --config ", config, " --stats", stats)  
# system2("datmo", args="snapshot create -m 'an inline snapshot' ") #snapshot create, no metrics, no stats