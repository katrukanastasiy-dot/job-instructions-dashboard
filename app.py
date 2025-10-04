import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# === НАСТРОЙКА ===
GOOGLE_SHEET_ID = "2PACX-1vRt6mkLcvtneR8oXZVq-NoLBqaK3Hublc8iVRNI7c_TVd3Wk00NeN9NJCCWFXxZyjy5kheBu2wu1kV7".strip()
SHEET_NAME = "Лист1"

url = f"https://docs.google.com/spreadsheets/d/e/{GOOGLE_SHEET_ID}/pub?output=csv&sheet={SHEET_NAME}"

# Загрузка через requests
try:
    response = requests.get(url)
    response.raise_for_status()
    response.encoding = 'utf-8'
    df = pd.read_csv(StringIO(response.text))
except Exception as e:
    st.error("❌ Не удалось загрузить данные из Google Таблицы.")
    st.write("Проверь:")
    st.write("- Таблица опубликована как CSV (Файл → Опубликовать в Интернете)")
    st.write("- Публичный ID скопирован правильно")
    st.write("- Есть хотя бы одна строка данных")
    st.code(f"URL: {url}")
    st.stop()

# Обработка данных
df = df.astype(str)

if 'Дата обновления' in df.columns:
    df['Дата обновления'] = pd.to_datetime(df['Дата обновления'], dayfirst=True, errors='coerce')

if 'Срок актуальности (дней)' in df.columns:
    df['Срок актуальности (дней)'] = pd.to_numeric(df['Срок актуальности (дней)'], errors='coerce')

df['Актуально до'] = df['Дата обновления'] + pd.to_timedelta(df['Срок актуальности (дней)'], unit='D')
today = pd.Timestamp.today()
df['Просрочено'] = df['Актуально до'] < today
df['Есть PDF'] = df['Путь к PDF'].str.strip().notna() & (df['Путь к PDF'].str.strip() != '')

# Дашборд
st.title("📊 Дашборд: Должностные инструкции")

total = len(df)
expired = df['Просрочено'].sum()
missing_pdf = (~df['Есть PDF']).sum()

col1, col2, col3 = st.columns(3)
col1.metric("Всего инструкций", total)
col2.metric("Требуют обновления", expired, delta_color="inverse")
col3.metric("Нет PDF", missing_pdf, delta_color="inverse")

show_expired = st.checkbox("Показать только просроченные")
df_show = df[df['Просрочено']] if show_expired else df

st.dataframe(df_show[[
    'Должность', 'Отдел', 'Дата обновления', 'Актуально до', 'Есть PDF', 'Просрочено'
]].style.applymap(
    lambda x: 'background-color: #ffe6e6' if x else '', subset=['Просрочено']
))

st.markdown(f"[Редактировать в Google Таблице](https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID.split('-')[0]})")
