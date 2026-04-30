import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from datetime import timedelta

st.set_page_config(page_title="Inventory Optimizer", layout="wide")

# Загрузка модели
@st.cache_resource
def load_model():
    return joblib.load('model.pkl')

try:
    model = load_model()
    model_loaded = True
except:
    model_loaded = False

st.title("📦 Оптимизация складских запасов")
st.sidebar.header("Настройки логистики")

# Входные параметры
lead_time = st.sidebar.slider("Lead Time (дней до поставки)", 1, 30, 7)
current_stock = st.sidebar.number_input("Текущий остаток на складе", value=50000)

st.write("### Прогноз и рекомендации")

if model_loaded:
    # Создаем даты для прогноза
    future = model.make_future_dataframe(periods=lead_time)
    forecast = model.predict(future)
    
    # Берем только прогнозный период
    prediction = forecast.tail(lead_time)
    
    exp_demand = prediction['yhat'].sum()
    yhat_upper = prediction['yhat_upper'].sum()
    safety_stock = (yhat_upper - exp_demand) * 0.5
else:
    # Резервный вариант, если модель не найдена
    st.warning("Файл модели не найден. Используются демонстрационные данные.")
    exp_demand = 126762
    safety_stock = 44621

reorder_point = exp_demand + safety_stock
restock_qty = max(0, reorder_point - current_stock)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Прогноз спроса", f"{exp_demand:,.0f} ед.")
with col2:
    st.metric("Страховой запас", f"{safety_stock:,.0f} ед.")
with col3:
    st.metric("Рекомендация к закупке", f"{restock_qty:,.0f} ед.", delta_color="inverse")

# Визуализация
st.write("#### Уровни запасов")
fig = go.Figure()
fig.add_trace(go.Bar(name='Текущий запас', x=['Статус'], y=[current_stock], marker_color='blue'))
fig.add_trace(go.Bar(name='Необходимо закупить', x=['Статус'], y=[restock_qty], marker_color='orange'))
fig.update_layout(barmode='stack', height=400)
st.plotly_chart(fig, use_container_width=True)
