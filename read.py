import pickle
import pandas as pd
df1 = pd.read_excel("cc.xlsx")
city_names = [city for city in df1['AreaName'].values]
print(city_names)
# بارگذاری مدل و داده‌ها
with open('nearest_neighbor_model.pkl', 'rb') as f:
    data = pickle.load(f)
    nn_model = data['nn_model']
    df = data['df']

# تابع برای پیدا کردن نزدیک‌ترین مختصات
def find_nearest_coordinates(city_name, df, nn_model):
    city_data = df[df['city'] == city_name]
    
    if city_data.empty:
        return None, None, None
    
    city_coords = city_data[['latitude', 'longitude']].values[0]
    distances, indices = nn_model.kneighbors([city_coords])
    
    nearest_city = df.iloc[indices[0][0]]
    nearest_city_name = nearest_city['city']
    nearest_latitude = nearest_city['latitude']
    nearest_longitude = nearest_city['longitude']
    
    return nearest_city_name, nearest_latitude, nearest_longitude

# تست تابع
city = []
lat= []
long = []
for city_name in city_names:
     nearest_city_name,latitude, longitude = find_nearest_coordinates(city_name, df, nn_model)
     city.append(city)
     lat.append(latitude)
     long.append( longitude)
new_df = pd.DataFrame()
new_df['city'] = city
new_df['lat'] = lat
new_df['long'] = long
print(new_df)