import streamlit as st

st.set_page_config(page_title="MARKING HACK", layout="wide")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Аналитическая система маркированного рынка")

st.write(
    "В рамках хакатона MARKING HACK команда Punk Butterfly разработала сервис, взаимодействующий с системой маркировки\
     'ЧЕСТНЫЙ ЗНАК', с помощью которого государство может выявлять потенциально подозрительные на мошенничество точки \
     продажи, выявлять монополии среди поставщиков, а также регионы, в которых потенциально может возникнуть дефицит на товары.")

st.write("Навигация по сайту находится в левом выпадающем меню")

st.write("---")
st.subheader("Analytics - Просмотр показателей ритейлеров")
st.write("Выявление подозрительные показатели продаж торговых точек")

st.write("---")
st.subheader("Deviance - Оценка поставщиков на предмет монополии")
st.write("Вычисление индекса Хиршмана-Херфиндаля для поиска монополий среди поставщиков")

st.write("---")
st.subheader("Predicting Demand - Прогнозирование спроса и оценка рисков")
st.write("Предиктивная система для прогнозирования регионального спроса и вычисления метрики рисков повышенного потребления")

st.write("---")
st.subheader("Predicting General - Прогнозирование совокупности спроса и предложения")
st.write("Прогнозирование межрегионального потребления и поставок с последующей оценкой рисков дефицита")


