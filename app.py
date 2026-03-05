import streamlit as st
import pandas as pd
import sqlite3

# 1. Подключение к базе данных (создаст файл tickets.db, если его нет)
conn = sqlite3.connect('tickets.db', check_same_thread=False)
c = conn.cursor()

# 2. Создание таблицы для хранения (запустится один раз)
c.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event TEXT,
        tickets_count INTEGER,
        total_price INTEGER,
        name TEXT,
        email TEXT
    )
''')
conn.commit()

# Настройка страницы
st.set_page_config(page_title="Бронирование билетов", page_icon="🎟️")

st.title("🎟️ Система бронирования билетов")
st.write("Используйте форму ниже, чтобы выбрать мероприятие и купить билет.")
st.markdown("---")

# Доступные мероприятия
events = {
    "Концерт: 'Симфония Весны'": 15000,
    "Театр: 'Гамлет'": 8000,
    "Стендап-шоу": 5000,
    "Кино: Ночная премьера": 2500
}

st.subheader("Оформление заказа")
selected_event = st.selectbox("Выберите мероприятие:", list(events.keys()))
price = events[selected_event]

st.write(f"**Стоимость одного билета:** {price} тг.")

tickets_count = st.number_input("Количество билетов:", min_value=1, max_value=10, value=1)
total_price = price * tickets_count

st.info(f"**Итого к оплате:** {total_price} тг.")

name = st.text_input("Ваше имя:")
email = st.text_input("Ваш Email:")

# Кнопка отправки
if st.button("Забронировать", type="primary"):
    if name and email:
        # 3. Сохранение данных прямо в базу данных SQLite
        c.execute('INSERT INTO bookings (event, tickets_count, total_price, name, email) VALUES (?, ?, ?, ?, ?)', 
                  (selected_event, tickets_count, total_price, name, email))
        conn.commit()
        
        st.success(f"Ура, {name}! Вы успешно забронировали {tickets_count} билет(ов) на '{selected_event}'.")
        st.balloons()
    else:
        st.error("Пожалуйста, заполните поля с именем и email.")

st.markdown("---")

# 4. Секция только для Администратора
st.header("🔒 Панель администратора")
st.write("Введите пароль, чтобы увидеть все бронирования.")

# Поле для пароля (символы скрыты звездочками)
admin_password = st.text_input("Пароль:", type="password")

# Простая проверка пароля (например, пароль будет 12345)
if admin_password == "12345":
    st.subheader("📋 База данных бронирований")
    
    # Достаем все данные из базы
    df = pd.read_sql_query("SELECT * FROM bookings", conn)
    
    if not df.empty:
        # Показываем таблицу
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("Пока нет ни одного бронирования.")
elif admin_password != "":
    st.error("Неверный пароль!")
