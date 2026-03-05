import streamlit as st
import pandas as pd
import sqlite3
import re
import datetime

# --- НАСТРОЙКА БАЗЫ ДАННЫХ ---
conn = sqlite3.connect('cinema.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie TEXT,
        cinema TEXT,
        show_date TEXT,
        show_time TEXT,
        seats TEXT,
        ticket_types TEXT,
        total_price INTEGER,
        name TEXT,
        email TEXT
    )
''')
conn.commit()

# --- ФУНКЦИИ ---
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

# --- БАЗА ДАННЫХ ФИЛЬМОВ (Наш каталог) ---
movies = {
    "Дюна: Часть вторая": {
        "image": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=400&auto=format&fit=crop", # Картинка-заглушка
        "description": "Пол Атрейдес объединяется с Чани и фременами, чтобы отомстить заговорщикам, уничтожившим его семью.",
        "year": 2024, "country": "США, Канада", "director": "Дени Вильнёв",
        "actors": "Тимоти Шаламе, Зендея, Ребекка Фергюсон",
        "premiere": "1 марта 2024", "genre": "Фантастика, боевик", "age": "12+"
    },
    "Мастер и Маргарита": {
        "image": "https://images.unsplash.com/photo-1485846234645-a62644f84728?q=80&w=400&auto=format&fit=crop",
        "description": "Известный писатель оказывается в центре литературного скандала. Вскоре он знакомится с Маргаритой и таинственным Воландом.",
        "year": 2024, "country": "Россия", "director": "Михаил Локшин",
        "actors": "Аугуст Диль, Юлия Снигирь, Евгений Цыганов",
        "premiere": "25 января 2024", "genre": "Драма, фэнтези", "age": "18+"
    }
}

cinemas = [
    "Кинопарк 11 (ул. Абая, 15)", 
    "Евразия Синема (пр. Республики, 42)", 
    "Силвер Скрин (ТРЦ Мега)"
]

times = ["10:00", "12:30", "15:15", "18:00", "20:45", "23:30"]

ticket_prices = {
    "Взрослый": 2500,
    "Детский (до 12 лет)": 1000,
    "Студенческий": 1500,
    "Пенсионный": 1200
}

# --- ИНТЕРФЕЙС САЙТА ---
st.set_page_config(page_title="Кинотеатр онлайн", page_icon="🍿", layout="wide")

st.title("🍿 Бронирование билетов в кино")
st.markdown("---")

# 1. Выбор фильма и показ информации
selected_movie = st.selectbox("🎬 Выберите фильм:", list(movies.keys()))
movie_data = movies[selected_movie]

# Используем колонки для красивого отображения (слева постер, справа текст)
col1, col2 = st.columns([1, 2])

with col1:
    st.image(movie_data["image"], use_container_width=True)

with col2:
    st.subheader("Описание")
    st.write(movie_data["description"])
    st.write(f"**Год выпуска:** {movie_data['year']}")
    st.write(f"**Страна:** {movie_data['country']}")
    st.write(f"**Режиссер:** {movie_data['director']}")
    st.write(f"**Актеры:** {movie_data['actors']}")
    st.write(f"**Премьера:** {movie_data['premiere']}")
    st.write(f"**Жанр:** {movie_data['genre']}")
    st.write(f"**Возрастное ограничение:** 🔴 {movie_data['age']}")

st.markdown("---")

# 2. Настройки сеанса
st.subheader("📅 Выбор сеанса")
col3, col4, col5 = st.columns(3)
with col3:
    selected_cinema = st.selectbox("📍 Кинотеатр:", cinemas)
with col4:
    # Устанавливаем минимальную дату — сегодня
    selected_date = st.date_input("🗓️ Дата сеанса:", min_value=datetime.date.today())
with col5:
    selected_time = st.selectbox("⏰ Время сеанса:", times)

# 3. Выбор билетов
st.subheader("🎫 Выбор билетов")
st.write("Укажите количество билетов каждой категории:")

col_t1, col_t2, col_t3, col_t4 = st.columns(4)
with col_t1: adult_qty = st.number_input(f"Взрослый ({ticket_prices['Взрослый']} тг)", 0, 10, 0)
with col_t2: child_qty = st.number_input(f"Детский ({ticket_prices['Детский (до 12 лет)']} тг)", 0, 10, 0)
with col_t3: student_qty = st.number_input(f"Студенческий ({ticket_prices['Студенческий']} тг)", 0, 10, 0)
with col_t4: senior_qty = st.number_input(f"Пенсионный ({ticket_prices['Пенсионный']} тг)", 0, 10, 0)

total_tickets = adult_qty + child_qty + student_qty + senior_qty
total_price = (adult_qty * ticket_prices['Взрослый'] + 
               child_qty * ticket_prices['Детский (до 12 лет)'] + 
               student_qty * ticket_prices['Студенческий'] + 
               senior_qty * ticket_prices['Пенсионный'])

# 4. Выбор мест
st.subheader("🪑 Выбор мест")
selected_row = st.selectbox("Выберите ряд:", range(1, 11))
# Multiselect позволяет выбрать сразу несколько мест
selected_seats = st.multiselect("Выберите места (номера кресел):", range(1, 21))

# Логическая проверка: количество мест должно совпадать с количеством билетов
if len(selected_seats) != total_tickets:
    if total_tickets > 0:
        st.warning(f"⚠️ Вы выбрали {total_tickets} билет(ов), но отметили {len(selected_seats)} мест(а). Пожалуйста, выберите ровно {total_tickets} мест(а).")

st.info(f"**Сумма к оплате:** {total_price} тг.")

# 5. Оформление заказа
st.subheader("👤 Данные покупателя")
name = st.text_input("Ваше имя:")
email = st.text_input("Ваш Email:")

# Проверяем, можно ли разрешить кнопку бронирования
can_book = total_tickets > 0 and len(selected_seats) == total_tickets

if st.button("Оплатить и забронировать", type="primary", disabled=not can_book):
    if name and email:
        if is_valid_email(email):
            # Формируем строку с информацией о билетах для базы данных
            ticket_details = f"Взрослых: {adult_qty}, Детских: {child_qty}, Студ: {student_qty}, Пенс: {senior_qty}"
            seats_str = f"Ряд {selected_row}, Места: {', '.join(map(str, selected_seats))}"
            
            c.execute('''INSERT INTO bookings 
                         (movie, cinema, show_date, show_time, seats, ticket_types, total_price, name, email) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                      (selected_movie, selected_cinema, str(selected_date), selected_time, seats_str, ticket_details, total_price, name, email))
            conn.commit()
            
            st.success(f"🎬 Ура, {name}! Вы идете на фильм «{selected_movie}»!")
            st.write(f"📍 **Место:** {selected_cinema} | 🗓 **Дата:** {selected_date} | ⏰ **Время:** {selected_time}")
            st.write(f"🪑 **Ваши места:** {seats_str}")
            st.balloons()
        else:
            st.error("⚠️ Введен некорректный Email.")
    else:
        st.error("⚠️ Пожалуйста, заполните поля с именем и email.")

st.markdown("---")

# --- АДМИН ПАНЕЛЬ ---
st.header("🔒 Панель администратора")
admin_password = st.text_input("Пароль администратора:", type="password")

if admin_password == "12345":
    st.subheader("📋 Все проданные билеты")
    df = pd.read_sql_query("SELECT * FROM bookings", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("Пока нет ни одной бронирования.")
