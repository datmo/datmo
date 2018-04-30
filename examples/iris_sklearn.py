from sklearn import datasets
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import datmo # extra line

# Run `$ datmo init` in your terminal to instantiate a Datmo project

config = { "solver": "newton-cg" } # extra line
iris_dataset = datasets.load_iris()
X, y = iris_dataset.data, iris_dataset.target
X_train, X_test, y_train, y_test = train_test_split(X, y)
model = LogisticRegression(**config).fit(X_train, y_train)

train_acc = model.score(X_train, y_train)
test_acc = model.score(X_test, y_test)

print(train_acc)
print(test_acc)

stats = { "train_accuracy": train_acc, "test_accuracy": test_acc } # extra line
datmo.snapshot.create(message="my first snapshot", config=config, stats=stats) # extra line