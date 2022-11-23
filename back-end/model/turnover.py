import pandas as pd
import numpy as np

from plotly.offline import iplot, init_notebook_mode
import plotly.express as px

from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier,GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import train_test_split

from sklearn.preprocessing import LabelEncoder

import joblib


df = pd.read_csv('turnover.csv', encoding = 'ISO-8859-1')

#print('Categorical columns: ')
for col in df.columns:
    if df[col].dtype == 'object':
        values = df[col].value_counts()
        values = dict(values)
        
        #print(str(col))
        label = LabelEncoder()
        label = label.fit(df[col])
        df[col] = label.transform(df[col].astype(str))
        
        new_values = df[col].value_counts()
        new_values = dict(new_values)
        
        value_dict = {}
        i=0
        for key in values:
            value_dict[key] = list(new_values)[i]
            i+= 1
        #print(value_dict)

X = df.drop(columns=['event'])
y = df['event']



X_train, X_test, y_train, y_test = train_test_split(X, y , test_size=0.2)

models = {}
def train_validate_predict(classifiers, x_train, y_train, x_test, y_test, index):
    model = classifiers
    model.fit(x_train, y_train)
    
    y_pred = model.predict(x_test)

    r2 = accuracy_score(y_test, y_pred)
    print(classifiers, r2)
    models[index] = r2

model_names = ['SVC', 'DecisionTreeClassifier', 'AdaBoostClassifier', 'RandomForestClassifier', 'ExtraTreesClassifier', 'LogisticRegression', 'GradientBoostingClassifier']
model_list = [SVC, DecisionTreeClassifier, AdaBoostClassifier, RandomForestClassifier, ExtraTreesClassifier, LogisticRegression, GradientBoostingClassifier]

index = 0
for classifiers in model_list:
    train_validate_predict(classifiers(), X_train, y_train, X_test, y_test, model_names[index])
    index+=1

best_value = max(models.values())
best_model = {i for i in models if models[i]==best_value}
print(best_model)

model = RandomForestClassifier()
model.fit(X_train, y_train)

y_pred = model.predict_proba(X_test)
print([i[1] for i in y_pred])

