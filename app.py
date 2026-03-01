import streamlit as st
import pandas as pd

# Инициализация хранилища бронирований в памяти сессии
if 'bookings' not in st.session_state:
    st.session_state.bookings = []

# Настройка страницы
st.set_page_config(page_title="Бронирование билетов", page_icon="🎟️")

st.title("🎟️ Система бронирования билетов")
st.write("Используйте форму ниже, чтобы выбрать мероприятие и купить билет.")

st.markdown("---")

# Доступные мероприятия и цены (в тенге или рублях)
events = {
    "Концерт: 'Симфония Весны'": 15000,
    "Театр: 'Гамлет'": 8000,
    "Стендап-шоу": 5000,
    "Кино: Ночная премьера": 2500
}

# Форма бронирования
st.subheader("Оформление заказа")

# Выбор мероприятия
selected_event = st.selectbox("Выберите мероприятие:", list(events.keys()))
price = events[selected_event]

st.write(f"**Стоимость одного билета:** {price}")

# Выбор количества
tickets_count = st.number_input("Количество билетов:", min_value=1, max_value=10, value=1)
total_price = price * tickets_count

st.info(f"**Итого к оплате:** {total_price}")

# Данные покупателя
name = st.text_input("Ваше имя:")
email = st.text_input("Ваш Email:")

# Кнопка отправки
if st.button("Забронировать", type="primary"):
    if name and email:
        # Сохранение данных
        booking = {
            "Мероприятие": selected_event, 
            "Количество": tickets_count, 
            "Сумма": total_price, 
            "Имя": name, 
            "Email": email
        }
        st.session_state.bookings.append(booking)
        st.success(f"Ура, {name}! Вы успешно забронировали {tickets_count} билет(ов) на '{selected_event}'.")
        st.balloons() # Анимация успеха
    else:
        st.error("Пожалуйста, заполните поля с именем и email, чтобы мы могли отправить вам билеты.")

st.markdown("---")

# Отображение списка бронирований (админ-панель)
if st.session_state.bookings:
    st.subheader("📋 Ваши текущие бронирования")
    df = pd.DataFrame(st.session_state.bookings)
    st.dataframe(df, use_container_width=True)