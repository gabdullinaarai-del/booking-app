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
    },
    "Оппенгеймер": {
        "image": "https://images.unsplash.com/photo-1690029837549-c1842e472251?q=80&w=400&auto=format&fit=crop",
        "description": "История жизни американского физика-теоретика Роберта Оппенгеймера, руководителя Манхэттенского проекта по созданию атомной бомбы.",
        "year": 2023, "country": "США, Великобритания", "director": "Кристофер Нолан",
        "actors": "Киллиан Мерфи, Эмили Блант, Мэтт Дэймон",
        "premiere": "21 июля 2023", "genre": "Биографический, драма", "age": "18+"
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

col1, col2 = st.columns([1, 2])
with col1:
    st.image(movie_data["image"], use_container_width=True)
with col2:
    st.subheader(f"«{selected_movie}»")
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
    selected_cinema = st.selectbox("📍 Кинотеатр:", cinemas, key="cinema_select")
with col4:
    selected_date = st.date_input("🗓️ Дата сеанса:", min_value=datetime.date.today(), key="date_select")
with col5:
    selected_time = st.selectbox("⏰ Время сеанса:", times, key="time_select")

# 3. Выбор билетов
st.subheader("🎫 Выбор количества билетов")
st.write("Укажите, сколько билетов каждой категории вы хотите купить:")

col_t1, col_t2, col_t3, col_t4 = st.columns(4)
with col_t1: adult_qty = st.number_input(f"Взрослый ({ticket_prices['Взрослый']} тг)", 0, 10, 0, key="adult_qty")
with col_t2: child_qty = st.number_input(f"Детский ({ticket_prices['Детский (до 12 лет)']} тг)", 0, 10, 0, key="child_qty")
with col_t3: student_qty = st.number_input(f"Студенческий ({ticket_prices['Студенческий']} тг)", 0, 10, 0, key="student_qty")
with col_t4: senior_qty = st.number_input(f"Пенсионный ({ticket_prices['Пенсионный']} тг)", 0, 10, 0, key="senior_qty")

total_tickets_to_select = adult_qty + child_qty + student_qty + senior_qty

st.info(f"Вам нужно выбрать {total_tickets_to_select} мест(а).")

# --- 4. Интерактивный план зала (Псевдографика) ---
st.subheader("🪑 Выбор мест на плане зала")
st.markdown("Экран")
st.markdown("---")

# Инициализация выбранных мест в состоянии сессии, если их нет
if 'selected_seats_plan' not in st.session_state:
    st.session_state.selected_seats_plan = []

# Очистка выбранных мест, если изменился сеанс
if st.session_state.get('last_session_key') != (selected_movie, selected_cinema, selected_date, selected_time):
    st.session_state.selected_seats_plan = []
    st.session_state.last_session_key = (selected_movie, selected_cinema, selected_date, selected_time)

# Макет зала: 10 рядов, по 15 мест
num_rows = 10
seats_per_row = 15

# Построение зала
for row in range(1, num_rows + 1):
    cols = st.columns(seats_per_row + 1) # Дополнительная колонка для номера ряда
    
    # Номер ряда
    with cols[0]:
        st.markdown(f"**Ряд {row}:**")

    # Места в ряду
    for seat_num in range(1, seats_per_row + 1):
        seat_id = f"R{row}S{seat_num}" # Уникальный ID для каждого места
        
        # Определяем, выбрано ли это место
        is_selected = seat_id in st.session_state.selected_seats_plan
        
        # Определяем стиль кнопки
        if is_selected:
            button_style = "primary" # Синяя кнопка для выбранного места
        else:
            button_style = "secondary" # Серая кнопка для свободного места

        with cols[seat_num]:
            # Создаем кнопку для каждого места
            if st.button(f"{seat_num}", key=seat_id, type=button_style):
                if is_selected:
                    # Если место уже выбрано, убираем его из списка
                    st.session_state.selected_seats_plan.remove(seat_id)
                elif len(st.session_state.selected_seats_plan) < total_tickets_to_select:
                    # Если место не выбрано и есть свободные места
                    st.session_state.selected_seats_plan.append(seat_id)
                else:
                    # Если выбрано максимальное количество мест
                    st.warning(f"Вы уже выбрали {total_tickets_to_select} мест(а). Отмените выбор, чтобы выбрать другое.")
                # Принудительно перезагружаем страницу, чтобы обновились цвета кнопок
                st.rerun() 

st.markdown("---")
# Выводим выбранные места
if st.session_state.selected_seats_plan:
    st.success(f"Выбранные места: {', '.join(st.session_state.selected_seats_plan)}")
else:
    st.write("Пожалуйста, выберите места на плане зала.")

# --- Итоговая сумма и проверка ---
current_selected_tickets = len(st.session_state.selected_seats_plan)

# Расчет общей стоимости
total_price = (adult_qty * ticket_prices['Взрослый'] + 
               child_qty * ticket_prices['Детский (до 12 лет)'] + 
               student_qty * ticket_prices['Студенческий'] + 
               senior_qty * ticket_prices['Пенсионный'])

st.info(f"**Итого к оплате:** {total_price} тг. (Выбрано {current_selected_tickets} из {total_tickets_to_select} мест)")

# 5. Оформление заказа
st.subheader("👤 Данные покупателя")
name = st.text_input("Ваше имя:", key="buyer_name")
email = st.text_input("Ваш Email:", key="buyer_email")

# Проверяем, можно ли разрешить кнопку бронирования
can_book = (total_tickets_to_select > 0 and 
            current_selected_tickets == total_tickets_to_select and 
            name and email and 
            is_valid_email(email))

if st.button("Оплатить и забронировать", type="primary", disabled=not can_book):
    # Если все проверки пройдены
    ticket_details = f"Взрослых: {adult_qty}, Детских: {child_qty}, Студ: {student_qty}, Пенс: {senior_qty}"
    seats_str = ', '.join(st.session_state.selected_seats_plan) # Сохраняем как R1S5, R2S10

    c.execute('''INSERT INTO bookings 
                 (movie, cinema, show_date, show_time, seats, ticket_types, total_price, name, email) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
              (selected_movie, selected_cinema, str(selected_date), selected_time, seats_str, ticket_details, total_price, name, email))
    conn.commit()
    
    st.success(f"🎬 Ура, {name}! Вы идете на фильм «{selected_movie}»!")
    st.write(f"📍 **Место:** {selected_cinema} | 🗓 **Дата:** {selected_date} | ⏰ **Время:** {selected_time}")
    st.write(f"🪑 **Ваши места:** {seats_str}")
    st.balloons()
    
    # Очищаем выбранные места после успешной брони
    st.session_state.selected_seats_plan = []
    st.rerun() # Перезагружаем, чтобы кнопки стали серыми
else:
    if not can_book and st.session_state.get('button_clicked', False): # Проверяем, пытался ли пользователь нажать
        if not name or not email:
            st.error("⚠️ Пожалуйста, заполните поля с именем и email.")
        elif not is_valid_email(email):
            st.error("⚠️ Введен некорректный Email. Проверьте, есть ли в нем символ '@' и домен (например, .com или .ru).")
        elif total_tickets_to_select == 0:
            st.error("⚠️ Выберите хотя бы один билет.")
        elif current_selected_tickets != total_tickets_to_select:
            st.error(f"⚠️ Выберите {total_tickets_to_select} мест(а). Выбрано: {current_selected_tickets}.")

# --- АДМИН ПАНЕЛЬ ---
st.markdown("---")
st.header("🔒 Панель администратора")
admin_password = st.text_input("Пароль администратора:", type="password", key="admin_pass")

if admin_password == "12345":
    st.subheader("📋 Все проданные билеты")
    df = pd.read_sql_query("SELECT * FROM bookings", conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("Пока нет ни одного бронирования.")
else:
    if admin_password != "":
        st.error("Неверный пароль!")
