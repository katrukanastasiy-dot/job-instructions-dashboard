import streamlit as st
import pandas as pd
import requests
from io import StringIO
import chardet

# === ПОЛНАЯ CSV-ССЫЛКА НАПРЯМУЮ (рабочая!) ===
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRt6mkLcvtneR8oXZVq-NoLBqaK3Hublc8iVRNI7c_TVd3Wk00NeN9NJCCWFXxZyjy5kheBu2wu1kV7/pub?gid=0&single=true&output=csv"

# === ЗАГРУЗКА ДАННЫХ ===
try:
    response = requests.get(url)
    response.raise_for_status()
    
    # Определяем кодировку
    detected = chardet.detect(response.content)
    encoding = detected['encoding'] or 'utf-8'
    
    # Декодируем текст
    text = response.content.decode(encoding)
    
    # Загружаем в pandas
    df = pd.read_csv(StringIO(text))
    
except Exception as e:
    st.error("❌ Не удалось загрузить данные из Google Таблицы.")
    st.write("Проверь:")
    st.write("- Таблица опубликована как CSV")
    st.write("- Ссылка в коде совпадает с той, что работает в браузере")
    st.code(f"URL: {url}")
    st.exception(e)
    st.stop()

# === ОЧИСТКА НАЗВАНИЙ КОЛОНОК ===
df.columns = df.columns.str.strip()

# === ПРОВЕРКА НАЛИЧИЯ НУЖНЫХ КОЛОНОК ===
required_columns = ['Должность', 'Отдел', 'Дата обновления', 'Срок актуальности (дней)', 'Путь к PDF']
missing = [col for col in required_columns if col not in df.columns]

if missing:
    st.error(f"❌ В таблице отсутствуют колонки: {', '.join(missing)}")
    st.write("Текущие колонки:")
    st.write(list(df.columns))
    st.write("💡 Проверь первую строку Google Таблицы — названия должны быть точными.")
    st.stop()

# === ОБРАБОТКА ДАННЫХ ===
df = df.astype(str)

# Дата обновления
df['Дата обновления'] = pd.to_datetime(df['Дата обновления'], dayfirst=True, errors='coerce')

# Срок в днях
df['Срок актуальности (дней)'] = pd.to_numeric(df['Срок актуальности (дней)'], errors='coerce')

# Актуально до
df['Актуально до'] = df['Дата обновления'] + pd.to_timedelta(df['Срок актуальности (дней)'], unit='D')

# Просрочено?
today = pd.Timestamp.today()
df['Просрочено'] = df['Актуально до'] < today

# Есть PDF?
df['Есть PDF'] = df['Путь к PDF'].str.strip().notna() & (df['Путь к PDF'].str.strip() != '') & (df['Путь к PDF'].str.strip().str.lower() != 'nan')

# === ДАШБОРД ===
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
df_to_show = df[df['Просрочено']] if show_expired else df

# Таблица
st.dataframe(
    df_to_show[[
        'Должность', 'Отдел', 'Дата обновления', 
        'Актуально до', 'Есть PDF', 'Просрочено'
    ]].style.applymap(
        lambda x: 'background-color: #ffe6e6' if x else '', subset=['Просрочено']
    )
)

# Ссылка на редактирование (подставь свою обычную ссылку на таблицу)
st.markdown("[✏️ Редактировать данные в Google Таблице](https://docs.google.com/spreadsheets/d/1Rt6mkLcvtneR8oXZVq-NoLBqaK3Hublc8iVRNI7c_TVd3Wk00NeN9NJCCWFXxZyjy5kheBu2wu1kV7/edit)")
