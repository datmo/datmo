library(datasets)
library(caret)
library(rpart.plot)

## Import data
df <- iris
head(df) # View first few rows of dataset

## Fit Model
modFit <- train(Species ~., method = "rpart", data=df) #Fit model
print(modFit$finalModel)   #Summarize model

# Visualize Results
rpart.plot(modFit$finalModel) #create decision tree visualization

## Define the properties we want to log in the snapshot
# Define configuration to save
config<- paste(sep="",
               " --config method:", modFit$method,
               " --config modelType:", modFit$modelType)

#define metrics to save from the model
stats<- paste(sep="",
              " --stats Accuracy:", modFit$results$Accuracy[1],
              " --stats Kappa:", modFit$results$Kappa[1])

# Create snapshot with configuration and stats
system2("datmo", args=paste("snapshot create", "-m 'Whoah, my first snapshot!'", config, stats), timeout=15)