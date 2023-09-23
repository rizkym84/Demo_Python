import pickle
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Load the synthetic dataset generated earlier
# Replace 'your_dataset.csv' with the path to your dataset CSV file
# If you're using the same dataset as generated in the previous code, you can skip this step.
df = pd.read_csv('credit_card_transactions.csv')

# Encode categorical features (transaction_type and card_type)
df_encoded = pd.get_dummies(
    df, columns=['transaction_type', 'card_type'], drop_first=True)

# Split the dataset into features (X) and the target variable (y)
X = df_encoded.drop('is_fraud', axis=1)
# drop transaction date
X = X.drop('transaction_date', axis=1)
# drop merchant_id
X = X.drop('merchant_id', axis=1)
# drop customer_id
X = X.drop('customer_id', axis=1)


# READ ALL LOCATION AND MAKE IT AS INTEGER MAPPING
location = X['location'].unique()
location_mapping = dict(zip(location, range(0, len(location) + 1)))
X['location_id'] = X['location'].map(location_mapping).astype(int)

# save location mapping as json file
with open('location_mapping.json', 'w') as fp:
    json.dump(location_mapping, fp)

# drop location
X = X.drop('location', axis=1)  # drop location

# drop card_number
X = X.drop('card_number', axis=1)

y = df_encoded['is_fraud']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# Standardize features (scaling)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Create and train a Logistic Regression model
model = LogisticRegression(random_state=42)
model.fit(X_train, y_train)

# save model to disk
filename = 'finalized_model.sav'
pickle.dump(model, open(filename, 'wb'))


# Make predictions on the test data
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)
class_report = classification_report(y_test, y_pred)

print(f"Accuracy: {accuracy}")
print(f"Confusion Matrix:\n{conf_matrix}")
print(f"Classification Report:\n{class_report}")
