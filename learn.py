import pandas as pd

from sklearn.neighbors import NearestNeighbors
import numpy as np
# خواندن فایل Excel
file_path = 'iran_city.xlsx'
df = pd.read_excel(file_path)

# حذف ردیف‌هایی که مختصات نامعتبر دارند
df = df[df['latitude'] != '#VALUE!']
df = df[df['longitude'] != '#VALUE!']

# تبدیل مختصات به عدد
df['latitude'] = df['latitude'].astype(float)
df['longitude'] = df['longitude'].astype(float)


# ایجاد آرایه‌ای از مختصات
coordinates = df[['latitude', 'longitude']].values

# ساخت مدل NearestNeighbors
nn_model = NearestNeighbors(n_neighbors=1, metric='euclidean')
nn_model.fit(coordinates)

# تابع برای پیدا کردن نزدیک‌ترین مختصات
def find_nearest_coordinates(city_name, df, nn_model):
    # پیدا کردن مختصات شهر وارد شده
    city_data = df[df['city'] == city_name]
    
    if city_data.empty:
        return None, None, None
    
    city_coords = city_data[['latitude', 'longitude']].values[0]
    
    # پیدا کردن نزدیک‌ترین همسایه
    distances, indices = nn_model.kneighbors([city_coords])
    
    # اطلاعات شهر نزدیک
    nearest_city = df.iloc[indices[0][0]]
    nearest_city_name = nearest_city['city']
    nearest_latitude = nearest_city['latitude']
    nearest_longitude = nearest_city['longitude']
    
    return nearest_city_name, nearest_latitude, nearest_longitude

# تست تابع
city_name = "آشتیان"
nearest_city, latitude, longitude = find_nearest_coordinates(city_name, df, nn_model)

if nearest_city:
    print(f"نزدیک‌ترین شهر به {city_name}: {nearest_city}")
    print(f"مختصات: عرض جغرافیایی = {latitude}, طول جغرافیایی = {longitude}")
else:
    print(f"شهر {city_name} در داده‌ها یافت نشد.")

import pickle

# ذخیره مدل و داده‌ها
with open('nearest_neighbor_model.pkl', 'wb') as f:
    pickle.dump({
        'nn_model': nn_model,
        'df': df
    }, f)    