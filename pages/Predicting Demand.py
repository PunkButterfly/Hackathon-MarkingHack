import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from datetime import datetime as dt

print(dt.now(), "Predicting Demand Visited")

st.set_page_config(layout="wide")

st.title("Прогнозирование спроса")

st.markdown("Когда возникает локальный дефицит товара, государство заинтересовано в предотвращении этого дефицита, "
            "поэтому ему (государству) выгодно привлекать производителей товара в регион, где ожидается резкий скачек "
            "роста на спрос по товару (группе товаров).  \n"
            "Для предотвращения дефицита мы разработали систему прогнозирования спроса на конкретный `gtin` в конкретном регионе. "
            "В качестве модели используется нейронная сеть LSTM, обучающаяся на данных о спросе для каждой уникальной пары (`gtin`, `reg_id`), "
            "а затем считающая предсказания спроса на 12 недель вперед. "
            "В рамках хакатона для увеличения скорости вычислений мы решили взять только 100 уникальных `gtin` самых популярных (по спросу).  \n"
            "В системе можно увидеть карту регионов, на которой при вводе `gtin` подсвечиваются регионы с максимальной введеной нами **метрикой**. Пусть  \n"
            r"* $\text{predicted window max}$ -- максимальное значение известного спроса за последние 12 недель  " + "\n" +
            r"* $\text{previous window max}$ -- максимальное значение предсказанного спроса за следующие 12 недель.  " + "\n" +
            "Тогда **метрика** вводится как  \n"
            r"$$\text{metric}:=\frac{\text{predicted window max} - \text{previous window max}}{\text{previous window max}}$$  " + "\n" +
            r"Чем **больше** это значение, тем более резкий скачок роста спроса на товар может произойти в регионе. "
            r"Данная разработка может помочь государству выделить регионы, в которые стоит привлечь поставщиков конкретных товаров. "
            r"Для привлечения можно использовать льготы, по типу освобождения от налогов и т.п.")


def plot_graph(df):
    curr_data = df[df['type'] == 'real_data'][['cnt', 'dt']]
    predicted_data = df[df['type'] != 'real_data'][['cnt', 'dt']]
    fig1 = px.line(curr_data, x='dt', y='cnt', title='graph')
    fig2 = px.line(predicted_data, x='dt', y='cnt', )
    fig2['data'][0]['line']['color'] = "#ffa500"
    fig2['data'][0]['line']['dash'] = "dot"
    fig = go.Figure(data=fig1.data + fig2.data)
    return fig


def get_data(data, gtin, reg_id):
    result = data[(data['gtin'] == gtin) & (data['reg_id'] == reg_id)]
    return result


def get_gtins(data):
    result = list(data['gtin'].unique())
    return result


def get_reg_ids(data):
    result = list(data['reg_id'].unique())
    result = [str(x) for x in result]
    return result


data = pd.read_csv("data/regional_predictions.csv")


# Риск дефицита
st.subheader("Риск резкого повышения потребления")

sorted = data.drop_duplicates(subset=["gtin", "reg_id", "metric"], keep="first").sort_values(ascending=False,
                                                                                             by="metric")

st.dataframe(sorted[["gtin", "reg_id", "metric"]].reset_index(drop=True))

# Выбор интересных gtin и региона
st.subheader("Показатели товара в регионе")
# gtin = st.text_input("GTIN товара:", "5FC9EBED793E0DA01BCD8652E0FB1B70")
# reg_id = st.text_input("Регион:", "50")

gtin = st.selectbox("GTIN товара:", get_gtins(sorted))
reg_id = st.selectbox("Регион:", get_reg_ids(sorted))

sample = get_data(data, gtin, int(reg_id)).sort_values('dt')

if sample is not None:
    if len(sample) == 0:
        st.warning('Недостаточно данных')
    else:
        color = "green" if sample["metric"].values[0] < 0 else "red"
        st.markdown(f'<font color={color}><strong>Метрика: {sample["metric"].values[0]}</strong></font>', unsafe_allow_html=True)
        graph = plot_graph(sample)
        st.plotly_chart(graph)

# Риск дефицита товара по регионам
st.subheader("Риск дефицита товара по регионам")

# gtin = st.text_input("Товар:", "5FC9EBED793E0DA01BCD8652E0FB1B70", key="map")
gtin = st.selectbox("GTIN товара::", get_gtins(data))

okato = pd.read_csv('data/okato.csv')
russia_regions = gpd.read_file('data/regions_new.geojson')

regions = sorted[sorted["gtin"] == gtin]["reg_id"].to_list()
metrics = sorted[sorted["gtin"] == gtin]["metric"].to_list()

dictionary = {"REGION_ID": [], "values": []}

# читаем okato и создаём словарь
regions_mapping = {}
for i in range(len(okato)):
    regions_mapping[okato['ISO'][i]] = okato['ОКАТО'][i]

index = 0
for i in regions_mapping.values():
    if i in regions:
        index = regions.index(i)

        dictionary["REGION_ID"].append(i)
        dictionary["values"].append(metrics[index])
    else:
        dictionary["REGION_ID"].append(i)
        dictionary["values"].append(np.NaN)

df = pd.DataFrame(dictionary)

# читаем okato и создаём словарь
regions_mapping = {}
for i in range(len(okato)):
    regions_mapping[okato['ISO'][i]] = okato['ОКАТО'][i]

# добавляем уникальные id'шники регионов
russia_regions['REGION_ID'] = dictionary["REGION_ID"]

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

rel_.add_to(m)

m.save('maps/predictions_map.html')

components.html(open("maps/predictions_map.html", 'r', encoding='utf-8').read(), height=500)
