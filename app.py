import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# === НАСТРОЙКА: вставь сюда ID своей Google Таблицы ===
GOOGLE_SHEET_ID = "2PACX-1vRt6mkLcvtneR8oXZVq-NoLBqaK3Hublc8iVRNI7c_TVd3Wk00NeN9NJCCWFXxZyjy5kheBu2wu1kV7"  # ← ЗАМЕНИ НА СВОЙ ID!
SHEET_NAME = "Лист1"  # или как у тебя назван лист

# Ссылка для чтения таблицы как CSV
url = f"https://docs.google.com/spreadsheets/d/e/{GOOGLE_SHEET_ID}/pub?output=csv&sheet={SHEET_NAME}"

# Загружаем данные
try:
    df = pd.read_csv(url, encoding='utf-8')
except UnicodeDecodeError:
    # Если не сработало — пробуем другую кодировку (на всякий случай)
    df = pd.read_csv(url, encoding='cp1251')
except Exception as e:
    st.error(f"Ошибка при загрузке данных: {str(e)}")
    st.write(f"URL: {url}")
    st.stop()

# Преобразуем дату
df['Дата обновления'] = pd.to_datetime(df['Дата обновления'], dayfirst=True)
df['Срок актуальности (дней)'] = pd.to_numeric(df['Срок актуальности (дней)'], errors='coerce')

# Считаем дату окончания актуальности
df['Актуально до'] = df['Дата обновления'] + pd.to_timedelta(df['Срок актуальности (дней)'], unit='D')

# Проверяем, просрочено ли
today = datetime.today()
df['Просрочено'] = df['Актуально до'] < today

# Отмечаем, есть ли PDF (если поле не пустое)
df['Есть PDF'] = df['Путь к PDF'].notna() & (df['Путь к PDF'] != '')

# === Выводим дашборд ===
st.title("📊 Дашборд: Должностные инструкции")

# Статистика
total = len(df)
expired = df['Просрочено'].sum()
missing_pdf = (~df['Есть PDF']).sum()

col1, col2, col3 = st.columns(3)
col1.metric("Всего инструкций", total)
col2.metric("Требуют обновления", expired, delta_color="inverse")
col3.metric("Нет PDF", missing_pdf, delta_color="inverse")

# Фильтр
show_expired = st.checkbox("Показать только просроченные")

if show_expired:
    df = df[df['Просрочено']]

# Таблица
st.dataframe(df[[
    'Должность', 'Отдел', 'Дата обновления', 
    'Актуально до', 'Есть PDF', 'Просрочено'
]].style.applymap(
    lambda x: 'background-color: #ffe6e6' if x else '', subset=['Просрочено']
))

# Ссылка на таблицу
st.markdown(f"[Редактировать данные в Google Таблице](https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID})")
