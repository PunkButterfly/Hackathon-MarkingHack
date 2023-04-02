import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster

sale_fields = ['Продажа конечному потребителю в точке продаж',
               'Дистанционная продажа конечному потребителю',
               'Конечная продажа организации', 'Продажи за пределы РФ',
               'Продажа по государственному контракту']

closings = pd.read_parquet("data/Output_short.parquet", engine="fastparquet")  # "data/Output.parquet"
products = pd.read_csv("data/Products.csv")
retails = pd.read_csv("data/Places.csv")


def group_region_retails(product_gtin: str):
    # gtin товаров определенной категории
    # product_ids = self.products[self.products['product_short_name'] == product_type]['gtin']

    # Проданные товары определенного gtin
    sales = closings[(closings['gtin'] == product_gtin) &
                     closings['type_operation'].isin(sale_fields)]

    # Продажи с городами точек продаж
    sales = sales.merge(retails.drop(["inn"], axis=1), left_on='id_sp_',
                        right_on='id_sp_')  # ['id_sp', 'inn', 'region_code']

    # Выделение фич
    grouped = sales.groupby("region_code", group_keys=True)
    # regions = list(groups.keys())

    min_places = []
    max_places = []
    for name, group in grouped:
        min_places.append([sales.iloc[group["price"].idxmin()]["inn"]])
        max_places.append([sales.iloc[group["price"].idxmax()]["inn"]])

    result = {"regions": list(grouped.groups.keys()),
              "mean_prices": grouped["price"].mean().to_list(),
              "min_prices": grouped["price"].min().to_list(),
              "min_places": min_places,
              "max_prices": grouped["price"].max().to_list(),
              "max_places": max_places}

    return result


okato = pd.read_csv('data/okato.csv')

product_gtin = st.text_input("GTIN товара:", "1248F88441BCFC563FB99D77DB0BB80D")
value_type = st.selectbox("Тип значений", ["Минимальная цена", "Максимальная цена", "Средняя цена"])

value_type_mapping = {"Минимальная цена": "min_prices",
                      "Максимальная цена": "max_prices",
                      "Средняя цена": "mean_prices"}

retails_features = group_region_retails(product_gtin)

russia_regions = gpd.read_file('data/regions_new.geojson')

dictionary = {"REGION_ID": [], "values": [], "inns": []}

# читаем okato и создаём словарь
regions_mapping = {}
for i in range(len(okato)):
    regions_mapping[okato['ISO'][i]] = okato['ОКАТО'][i]

index = 0
for i in regions_mapping.values():
    if i in retails_features["regions"]:
        index = retails_features["regions"].index(i)

        dictionary["REGION_ID"].append(i)
        dictionary["values"].append(retails_features[value_type_mapping[value_type]][index])
        if value_type == "Максимальная цена":
            dictionary["inns"].append(retails_features["max_places"][index])
        elif value_type == "Минимальная цена":
            dictionary["inns"].append(retails_features["min_places"][index])
    else:
        dictionary["REGION_ID"].append(i)
        dictionary["values"].append(np.NaN)
        dictionary["inns"].append([])

df = pd.DataFrame(dictionary)

# добавляем уникальные id'шники регионов
# russia_regions['REGION_ID'] = dictionary["REGION_ID"]

russia_regions['REGION_ID'] = russia_regions['ref'].replace(regions_mapping)
russia_regions['REGION_ID'].astype('int64')

m = folium.Map(location=[63.391522, 96.328125], zoom_start=3, tiles="cartodb positron")

rel_ = folium.Choropleth(
    geo_data=russia_regions,
    name='Регионы России',
    data=df,
    columns=['REGION_ID', 'values'],
    key_on='feature.properties.REGION_ID',
    bins=5,
    fill_color='YlOrRd',
    nan_fill_color='white',
    nan_fill_opacity=0.5,
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Регионы России',
    highlight=True,
    show=False
)

okato = okato.set_index('ОКАТО')

marker_cluster = MarkerCluster().add_to(m)

for i in range(len(df)):
    print(int(df.iloc[i]['REGION_ID']))
    x = okato.loc[int(df.iloc[i]['REGION_ID'])]

    if value_type == "Максимальная цена":
        popup_desc = f"<font size='+0.5'><strong>Максимальная цена: {df['values'].loc[i]}<br>Подозрительный дистрибьютор: {df['inns'].loc[i]}</strong></font>"
    elif value_type == "Минимальная цена":
        popup_desc = f"<font size='+0.5'><strong>Минимальная цена: {df['values'].loc[i]}<br>Подозрительный дистрибьютор: {df['inns'].loc[i]}</strong></font>"
    else:
        popup_desc = f"<font size='+0.5'><strong>Средняя цена: {df['values'].loc[i]}</strong></font>"

    folium.Marker(
        location=[x['Ширина'],
                  x['Долгота']],
        popup=popup_desc,  # что видим, когда нажимаем
        tooltip=f"<font size='+0.5'><strong>{x['Название']}</strong></font>",  # что видим, когда наводим
        icon=folium.Icon(color="green", icon="ok-sign"),
    ).add_to(marker_cluster)

rel_.add_to(m)

m.save('maps/analytics_map.html')

components.html(open("maps/analytics_map.html", 'r', encoding='utf-8').read(), height=500)
