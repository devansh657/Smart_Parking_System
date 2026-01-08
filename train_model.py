import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

# ✅ Load Dataset
csv_file_path = "C:/Users/dmodi/Desktop/finalProject/newProjectDev/newProjectDev/backend/data/generated_parking_data_10000_numeric_day.csv"

try:
    df = pd.read_csv(csv_file_path)
    print(f"✅ Data loaded successfully from {csv_file_path}")
except FileNotFoundError:
    print(f"❌ Error: The file {csv_file_path} was not found.")
    exit()

# ✅ Convert 'availability' to Binary
df['availability'] = df['availability'].astype(int)

# ✅ Encode Categorical Variables
label_encoder = LabelEncoder()
if df['day_of_week'].dtype == 'object':
    df['day_of_week'] = label_encoder.fit_transform(df['day_of_week'])

if df['weather'].dtype == 'object':
    df['weather'] = label_encoder.fit_transform(df['weather'])

# ✅ Ensure Numerical Data
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

# ✅ Drop Missing Values
df = df.dropna()

# ✅ Split Features and Labels
X = df.drop('availability', axis=1)
y = df['availability']

# ✅ Balance Dataset Using SMOTE (Oversampling Minority Class)
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

# ✅ Split into Train & Test
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

# ✅ Feature Scaling (Important for XGBoost)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# ✅ Train XGBoost Model (BEST ACCURACY)
model = xgb.XGBClassifier(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=10,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
model.fit(X_train, y_train)

# ✅ Make Predictions
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"🎯 Model Accuracy: {accuracy:.4f}")  # Expect 95-99% Accuracy

# ✅ Save Model
model_dir = 'model'
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

model_save_path = os.path.join(model_dir, 'best_parking_predictor_model.pkl')
joblib.dump(model, model_save_path)
print(f"💾 Model saved to {model_save_path}")

# 📊 FEATURE IMPORTANCE PLOT
plt.figure(figsize=(10, 6))
feature_importance = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
sns.barplot(x=feature_importance, y=feature_importance.index, palette='magma')
plt.xlabel("Feature Importance Score")
plt.ylabel("Features")
plt.title("Feature Importance in Parking Prediction")
plt.show()

# 📊 ACTUAL vs PREDICTED PLOT
plt.figure(figsize=(6, 4))
sns.histplot(y_test, label='Actual', color='blue', alpha=0.6, kde=True)
sns.histplot(y_pred, label='Predicted', color='red', alpha=0.6, kde=True)
plt.legend()
plt.title("Actual vs Predicted Parking Availability")
plt.xlabel("Availability (0 = Not Available, 1 = Available)")
plt.ylabel("Count")
plt.show()

# ✅ Classification Report
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# 📊 CONFUSION MATRIX
from sklearn.metrics import confusion_matrix

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Not Available', 'Available'], yticklabels=['Not Available', 'Available'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix - Parking Availability')
plt.show()
