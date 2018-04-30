import os
from sklearn import datasets
from sklearn import linear_model as lm
from sklearn import model_selection as ms
from sklearn import externals as ex


iris_dataset = datasets.load_iris()
X = iris_dataset.data
y = iris_dataset.target
data = ms.train_test_split(X, y)
X_train, X_test, y_train, y_test = data

print("model: logistic regression")
model = lm.LogisticRegression(solver="newton-cg")
model.fit(X_train, y_train)

# Save files into the /task location while the
# task is running to ensure you save all files
# If not present, save in project root
if os.path.isdir(os.path.join("/task")):
    model_path = os.path.join("/task", "model.pkl")
else:
    model_path = os.path.join("model.pkl")
ex.joblib.dump(model, model_path)

train_acc = model.score(X_train, y_train)
test_acc = model.score(X_test, y_test)

print("training accuracy: " + str(train_acc))
print("test accuracy: " + str(test_acc))