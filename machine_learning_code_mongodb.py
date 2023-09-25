import pickle
import json
import pandas as pd
import pymongo
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Setting koneksi ke database mongodb
client = pymongo.MongoClient("mongodb://doitAdmin:doitAdminAt2023@digital-optima.com:27017/?authMechanism=DEFAULT&tls=false")

# Tentukan basis data (database) dan koleksi (collection) yang ingin Anda baca
db = client["klaim_asuransi"]
collection = db["data_klaim"]

# Lakukan query untuk mengambil data dari koleksi tersebut
data = collection.find()

# Konversi data MongoDB menjadi DataFrame pandas
df = pd.DataFrame(list(data))

# Encode fitur kategori (transaction_type dan card_type)
df_encoded = pd.get_dummies(
    df, columns=['transaction_type', 'card_type'], drop_first=True)

# Bagi dataset menjadi fitur (X) dan variabel target (y)
X = df_encoded.drop('is_fraud', axis=1)
# Hapus kolom tambahan sesuai kebutuhan
X = X.drop(['transaction_date', 'merchant_id', 'customer_id', 'location', 'card_number'], axis=1)

# Lakukan langkah-langkah preprocessing data sesuai kebutuhan

# Bagi data menjadi set pelatihan dan pengujian
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# Standarisasi fitur (scaling)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Buat dan latih model Regresi Logistik
model = LogisticRegression(random_state=42)
model.fit(X_train, y_train)

# Simpan model ke disk
filename = 'finalized_model1.sav'
pickle.dump(model, open(filename, 'wb'))

# Lakukan prediksi pada data uji
y_pred = model.predict(X_test)

# Evaluasi model
akurasi = accuracy_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)
class_report = classification_report(y_test, y_pred)

print(f"Akurasi: {akurasi}")
print(f"Matrix Confusi:\n{conf_matrix}")
print(f"Laporan Klasifikasi:\n{class_report}")
print(df_encoded.columns)


# Tutup koneksi MongoDB
client.close()
