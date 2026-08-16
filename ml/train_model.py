import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# ==========================================
# TRAINING DATA
# ==========================================

data = {
    "cgpa": [
        9.5, 9.2, 8.9, 8.7, 8.5,
        8.3, 8.1, 7.9, 7.7, 7.5,
        7.3, 7.1, 6.9, 6.7, 6.5,
        6.2, 6.0, 5.8, 5.5, 5.2
    ],

    "skills": [
        8, 7, 7, 6, 6,
        5, 5, 4, 4, 4,
        3, 3, 3, 2, 2,
        2, 1, 1, 1, 0
    ],

    "placed": [
        1, 1, 1, 1, 1,
        1, 1, 1, 1, 1,
        1, 1, 0, 0, 0,
        0, 0, 0, 0, 0
    ]
}


df = pd.DataFrame(data)


# ==========================================
# FEATURES AND TARGET
# ==========================================

X = df[["cgpa", "skills"]]

y = df["placed"]


# ==========================================
# TRAIN TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ==========================================
# RANDOM FOREST MODEL
# ==========================================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


model.fit(X_train, y_train)


# ==========================================
# ACCURACY
# ==========================================

prediction = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    prediction
)

print("Model Accuracy:", accuracy)


# ==========================================
# SAVE MODEL
# ==========================================

model_folder = os.path.join(
    os.path.dirname(__file__),
    "models"
)

os.makedirs(
    model_folder,
    exist_ok=True
)


model_path = os.path.join(
    model_folder,
    "placement_model.pkl"
)


joblib.dump(
    model,
    model_path
)


print("--------------------------------")
print("Model trained successfully!")
print("--------------------------------")
print("Saved at:")
print(model_path)