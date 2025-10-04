import streamlit as st
import pandas as pd
import requests
from io import StringIO
import chardet

# === НАСТРОЙКА: ВСТАВЬ СВОЙ ПУБЛИЧНЫЙ ID ===
GOOGLE_SHEET_ID = "2PACX-1vRt6mkLcvtneR8oXZVq-NoLBqaK3Hublc8iVRNI7c_TVd3Wk00NeN9NJCCWFXxZyjy5kheBu2wu1kV7"
SHEET_NAME = "Лист1"

# Формируем URL
url = f"https://docs.google.com/spreadsheets/d/e/{GOOGLE_SHEET_ID}/pub?output=csv&sheet={SHEET_NAME}"

# === ЗАГРУЗКА ДАННЫХ С АВТОМАТИЧЕСКИМ ОПРЕДЕЛЕНИЕМ КОДИРОВКИ ===
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
    st.error("❌ Не удалось загрузить или декодировать данные из Google Таблицы.")
    st.write("Проверь:")
    st.write("- Таблица опубликована как CSV (Файл → Опубликовать в Интернете)")
    st.write("- ID скопирован из CSV-ссылки (начинается с 2PACX-...)")
    st.code(f"URL: {url}")
    st.exception(e)
    st.stop()

# === ОЧИСТКА НАЗВАНИЙ КОЛОНОК ===
df.columns = df.columns.str.strip()

# === ВРЕМЕННО: ПОКАЖЕМ, КАК НАЗЫВАЮТСЯ КОЛОНКИ (для отладки) ===
# st.write("🔍 Названия колонок в таблице:")
# st.write(list(df.columns))

# === ПРОВЕРКА НАЛИЧИЯ НУЖНЫХ КОЛОНОК ===
required_columns = ['Должность', 'Отдел', 'Дата обновления', 'Срок актуальности (дней)', 'Путь к PDF']
missing = [col for col in required_columns if col not in df.columns]

if missing:
    st.error(f"❌ В таблице отсутствуют колонки: {', '.join(missing)}")
    st.write("Текущие колонки в файле:")
    st.write(list(df.columns))
    st.write("💡 Совет: проверь первую строку Google Таблицы — названия должны быть точными и без лишних пробелов.")
    st.stop()

# === ОБРАБОТКА ДАННЫХ ===
# Убедимся, что все данные — строки
df = df.astype(str)

# Преобразуем дату
df['Дата обновления'] = pd.to_datetime(df['Дата обновления'], dayfirst=True, errors='coerce')

# Преобразуем срок в число
df['Срок актуальности (дней)'] = pd.to_numeric(df['Срок актуальности (дней)'], errors='coerce')

# Рассчитываем дату окончания актуальности
df['Актуально до'] = df['Дата обновления'] + pd.to_timedelta(df['Срок актуальности (дней)'], unit='D')

# Проверяем просроченность
today = pd.Timestamp.today()
df['Просрочено'] = df['Актуально до'] < today

# Есть ли PDF?
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

# Ссылка на редактирование
st.markdown("[✏️ Редактировать данные в Google Таблице](https://docs.google.com/spreadsheets/d/1Rt6mkLcvtneR8oXZVq-NoLBqaK3Hublc8iVRNI7c_TVd3Wk00NeN9NJCCWFXxZyjy5kheBu2wu1kV7/edit)")
