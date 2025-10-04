import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# === НАСТРОЙКА: вставь сюда ID своей Google Таблицы ===
GOOGLE_SHEET_ID = "2PACX-1vRt6mkLcvtneR8oXZVq-NoLBqaK3Hublc8iVRNI7c_TVd3Wk00NeN9NJCCWFXxZyjy5kheBu2wu1kV7"  # ← ЗАМЕНИ НА СВОЙ ID!
SHEET_NAME = "Лист1"  # или как у тебя назван лист

# Ссылка для чтения таблицы как CSV
url = f"https://docs.google.com/spreadsheets/d/e/{GOOGLE_SHEET_ID}/pub?output=csv&sheet={SHEET_NAME}"

# Загружаем данные с явным указанием кодировки
try:
    df = pd.read_csv(url, encoding='utf-8')
except UnicodeDecodeError:
    st.error("Не удалось прочитать данные. Проверь, что таблица опубликована как CSV и содержит корректные данные.")
    st.stop()

# Убедимся, что все строки — строки (на случай, если pandas неправильно их интерпретировал)
df = df.astype(str)

# Преобразуем дату — если столбец "Дата обновления" есть
if 'Дата обновления' in df.columns:
    try:
        df['Дата обновления'] = pd.to_datetime(df['Дата обновления'], dayfirst=True, errors='coerce')
    except Exception as e:
        st.warning(f"Не удалось преобразовать дату: {e}")

# Считаем срок актуальности
if 'Срок актуальности (дней)' in df.columns:
    df['Срок актуальности (дней)'] = pd.to_numeric(df['Срок актуальности (дней)'], errors='coerce')

# Дата окончания актуальности
df['Актуально до'] = df['Дата обновления'] + pd.to_timedelta(df['Срок актуальности (дней)'], unit='D')

# Проверяем просроченность
today = pd.Timestamp.today()
df['Просрочено'] = df['Актуально до'] < today

# Есть PDF?
df['Есть PDF'] = df['Путь к PDF'].str.strip().notna() & (df['Путь к PDF'].str.strip() != '')

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
    df_filtered = df[df['Просрочено']]
else:
    df_filtered = df

# Таблица
st.dataframe(
    df_filtered[[
        'Должность', 'Отдел', 'Дата обновления', 
        'Актуально до', 'Есть PDF', 'Просрочено'
    ]].style.applymap(
        lambda x: 'background-color: #ffe6e6' if x else '', subset=['Просрочено']
    )
)

# Ссылка на таблицу
st.markdown(f"[Редактировать данные в Google Таблице](https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID})")
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
