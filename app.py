import streamlit as st
import pandas as pd
import sqlite3
import re  # 1. Новая библиотека для проверки правильности текста

# Функция для проверки корректности email
def is_valid_email(email):
    # Специальный шаблон, который говорит: "текст + @ + текст + . + текст"
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattern, email):
        return True
    return False

# Подключение к базе данных
conn = sqlite3.connect('tickets.db', check_same_thread=False)
c = conn.cursor()

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
        # 2. Проверяем email ПЕРЕД тем, как сохранить в базу
        if is_valid_email(email):
            c.execute('INSERT INTO bookings (event, tickets_count, total_price, name, email) VALUES (?, ?, ?, ?, ?)', 
                      (selected_event, tickets_count, total_price, name, email))
            conn.commit()
            
            st.success(f"Ура, {name}! Вы успешно забронировали {tickets_count} билет(ов) на '{selected_event}'.")
            st.balloons()
        else:
            # 3. Выдаем ошибку, если email написан криво
            st.error("⚠️ Ошибка: Введен некорректный Email. Проверьте, есть ли в нем символ '@' и домен (например, .com или .ru).")
    else:
        st.error("Пожалуйста, заполните поля с именем и email.")

st.markdown("---")

# Секция только для Администратора
st.header("🔒 Панель администратора")
st.write("Введите пароль, чтобы увидеть все бронирования.")

admin_password = st.text_input("Пароль:", type="password")

if admin_password == "12345":
    st.subheader("📋 База данных бронирований")
    
    df = pd.read_sql_query("SELECT * FROM bookings", conn)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("Пока нет ни одного бронирования.")
elif admin_password != "":
    st.error("Неверный пароль!")
