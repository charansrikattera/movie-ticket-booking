import streamlit as st
import sqlite3
import pandas as pd

# SQLite Database connection details
SQLITE_DB_PATH = 'movieDB.db'

# Establish database connection
def get_sqlite_connection():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    return conn

# Fetch available movies
def get_available_movies():
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM movies")
    movies = c.fetchall()
    conn.close()
    return [movie[0] for movie in movies]

# Fetch available theaters
def get_available_theaters():
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("SELECT name, city FROM theaters")
    theaters = c.fetchall()
    conn.close()
    return theaters

# Fetch available theaters for a specific movie
def get_theaters_by_movie(movie_name):
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("SELECT theaters.name FROM theaters JOIN movies ON theaters.id = movies.theater_id WHERE movies.name = ?",
              (movie_name,))
    theaters = c.fetchall()
    conn.close()
    return [theater[0] for theater in theaters]

# Fetch timings for a specific theater
def get_timings_by_theater(theater_name):
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute(
        "SELECT movies.timings FROM movies JOIN theaters ON movies.theater_id = theaters.id WHERE theaters.name = ?",
        (theater_name,))
    timings = c.fetchall()
    conn.close()
    return [timing[0] for timing in timings]

# Fetch movie details
def get_movie_details(movie_id):
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = c.fetchone()
    conn.close()
    return movie

# Fetch theater details
def get_theater_details(theater_id):
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM theaters WHERE id = ?", (theater_id,))
    theater = c.fetchone()
    conn.close()
    return theater

# Fetch booked seats for a movie
def get_booked_seats(movie_id):
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("SELECT seats FROM bookings WHERE movie_id = ?", (movie_id,))
    booked_seats = c.fetchall()
    conn.close()
    return [seat[0] for seat in booked_seats]

# Fetch bookings by movie
def get_bookings_by_movie(movie_id):
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM bookings WHERE movie_id = ?", (movie_id,))
    bookings = c.fetchall()
    conn.close()
    return bookings

# Book ticket
def book_ticket(user_id, movie_id, theater_id, timing, seats):
    conn = get_sqlite_connection()
    c = conn.cursor()
    for seat in seats:
        c.execute("INSERT INTO bookings (user_id, movie_id, theater_id, timing, seats) VALUES (?, ?, ?, ?, ?)",
                  (user_id, movie_id, theater_id, timing, seat))
    conn.commit()
    conn.close()

# Cancel booking
def cancel_booking(user_id, movie_name, theater_name, timing, seats):
    conn = get_sqlite_connection()
    c = conn.cursor()
    seats_to_cancel = tuple(seats)
    query = """
        DELETE FROM bookings
        WHERE user_id = ? AND movie_id = (SELECT id FROM movies WHERE name = ?)
        AND theater_id = (SELECT id FROM theaters WHERE name = ?)
        AND timing = ? AND seats IN (%s)
    """ % ",".join("?" * len(seats_to_cancel))
    params = (user_id, movie_name, theater_name, timing) + seats_to_cancel
    c.execute(query, params)
    conn.commit()
    conn.close()

# Fetch bookings for user
def get_user_bookings(user_id):
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("""
        SELECT bookings.id, movies.name, theaters.name, bookings.timing, bookings.seats
        FROM bookings
        JOIN movies ON bookings.movie_id = movies.id
        JOIN theaters ON bookings.theater_id = theaters.id
        WHERE bookings.user_id = ?
    """, (user_id,))
    bookings = c.fetchall()
    conn.close()
    return bookings

# Initialize session state for the chat
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Initialize session state for the seat selection
if 'selected_seats' not in st.session_state:
    st.session_state['selected_seats'] = []

if 'seat_selection' not in st.session_state:
    st.session_state['seat_selection'] = []

if 'movie_id' not in st.session_state:
    st.session_state['movie_id'] = None

if 'theater_id' not in st.session_state:
    st.session_state['theater_id'] = None

if 'timing' not in st.session_state:
    st.session_state['timing'] = None

if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

# Book tickets page
def book_tickets():
    st.subheader("Book Tickets")

    # Fetch available movies and let user select
    movie_names = get_available_movies()
    if not movie_names:
        st.warning("No movies available for booking at the moment.")
        return

    movie_name = st.selectbox("Select Movie", movie_names)
    if movie_name:
        # Fetch available theaters for the selected movie
        theaters = get_theaters_by_movie(movie_name)
        if not theaters:
            st.warning("No theaters available for the selected movie.")
            return

        theater_name = st.selectbox("Select Theater", theaters)
        if theater_name:
            # Fetch available timings for the selected theater
            timings = get_timings_by_theater(theater_name)
            if not timings:
                st.warning("No timings available for the selected theater.")
                return

            timing = st.selectbox("Select Timing", timings)
            if timing:
                # Fetch seat configuration and booked seats for the selected movie and theater
                conn = get_sqlite_connection()
                c = conn.cursor()
                c.execute(
                    "SELECT id, seats FROM movies WHERE name = ? AND theater_id = (SELECT id FROM theaters WHERE name = ?)",
                    (movie_name, theater_name))
                movie = c.fetchone()

                if movie:
                    movie_id = movie[0]
                    seats_config = movie[1].split('x')
                    rows = int(seats_config[0])
                    cols = int(seats_config[1])
                    booked_seats = get_booked_seats(movie_id)

                    seat_selection = []
                    for i in range(rows):
                        row = []
                        for j in range(cols):
                            seat_number = i * cols + j + 1
                            if str(seat_number) in booked_seats:
                                row.append((str(seat_number), True))  # True indicates the seat is booked
                            else:
                                row.append((str(seat_number), False))  # False indicates the seat is available
                        seat_selection.append(row)

                    st.session_state['seat_selection'] = seat_selection
                    st.session_state['movie_id'] = movie_id
                    theater_id = c.execute("SELECT id FROM theaters WHERE name = ?", (theater_name,)).fetchone()[0]
                    st.session_state['theater_id'] = theater_id
                    st.session_state['timing'] = timing

                    st.session_state['selected_seats'] = []  # Reset selected seats

                    conn.close()

                    st.markdown("### Select Seats")
                    selected_seats = []
                    for i, row in enumerate(st.session_state['seat_selection']):
                        cols = st.columns(len(row))
                        for j, (seat_number, is_booked) in enumerate(row):
                            if is_booked:
                                cols[j].checkbox(seat_number, value=True, disabled=True, key=f"{i}-{j}", help="Booked")
                            else:
                                if cols[j].checkbox(seat_number, key=f"{i}-{j}"):
                                    selected_seats.append(seat_number)

                    st.session_state['selected_seats'] = selected_seats

                    if st.button("Confirm Booking"):
                        if not st.session_state['selected_seats']:
                            st.warning("No seats selected. Please select seats to proceed with booking.")
                        else:
                            book_ticket(st.session_state['user'][0], st.session_state['movie_id'],
                                        st.session_state['theater_id'], st.session_state['timing'],
                                        st.session_state['selected_seats'])
                            st.success("Tickets booked successfully")
                            st.session_state['seat_selection'] = []
                            st.session_state['selected_seats'] = []

# Function to handle seat selection
def toggle_seat(seat_number):
    if seat_number in st.session_state['selected_seats']:
        st.session_state['selected_seats'].remove(seat_number)
    else:
        st.session_state['selected_seats'].append(seat_number)

# CSS for custom styling
st.markdown("""
    <style>
    .stCheckbox > div[role='checkbox'] {
        border-radius: 4px;
        border: 2px solid #ccc;
        padding: 5px;
        margin: 2px;
    }
    .stCheckbox > div[role='checkbox']:disabled {
        background-color: #ffdddd;
        border: 2px solid red;
        color: red;
    }
    </style>
    """, unsafe_allow_html=True)

# Ensure admin exists
def ensure_admin_exists():
    conn = get_sqlite_connection()
    c = conn.cursor()
    admin_username = "admin123"
    admin_password = "admin123"
    admin_phone = "0000000000"
    admin_role = "admin"
    c.execute("SELECT * FROM users WHERE username = ?", (admin_username,))
    if c.fetchone() is None:
        c.execute("INSERT INTO users (username, password, phone, role) VALUES (?, ?, ?, ?)",
                  (admin_username, admin_password, admin_phone, admin_role))
        conn.commit()
    conn.close()

ensure_admin_exists()

# Session state initialization
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False
if 'is_owner' not in st.session_state:
    st.session_state['is_owner'] = False
if 'is_user' not in st.session_state:
    st.session_state['is_user'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

# Login
def login(username, password):
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

# Sign up
def sign_up(username, password, phone):
    conn = get_sqlite_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, phone, role) VALUES (?, ?, ?, ?)",
                  (username, password, phone, 'user'))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Add theater owner
def add_theater_owner(username, password, phone, theater_name):
    conn = get_sqlite_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, phone, role) VALUES (?, ?, ?, ?)",
                  (username, password, phone, 'owner'))
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        owner_id = c.fetchone()[0]
        c.execute("INSERT INTO theaters (name, city, owner_id) VALUES (?, ?, ?)", (theater_name, '', owner_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Remove user
def remove_user(user_id):
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    c.execute("DELETE FROM theaters WHERE owner_id = ?", (user_id,))
    conn.commit()
    conn.close()

# Add movie
def add_movie(owner_id, name, city, theater_id, timings, seats):
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("INSERT INTO movies (name, city, theater_id, timings, seats) VALUES (?, ?, ?, ?, ?)",
              (name, city, theater_id, timings, seats))
    conn.commit()
    conn.close()

# Remove movie
def remove_movie(movie_id):
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()

# Cancel Ticket User Interface
def cancel_ticket():
    st.subheader("Cancel Ticket")

    # Retrieve user information and bookings
    user_id = st.session_state['user'][0]
    bookings = get_user_bookings(user_id)

    # If no bookings are found
    if not bookings:
        st.info("No bookings found. You have no tickets to cancel.")
        return

    # Display booking options in a more visual manner
    booking_options = [
        f" Movie: {booking[1]}\n Theater: {booking[2]}\n Time: {booking[3]}"
        for booking in bookings
    ]
    selected_booking = st.selectbox("Select a booking to cancel", booking_options)

    if selected_booking:
        # Extract booking details
        booking_index = booking_options.index(selected_booking)
        booking_id, movie_name, theater_name, timing, seats = bookings[booking_index]
        seats_to_cancel = st.multiselect("Select seats to cancel", seats.split(','))

        # Cancellation button with visual cue
        if st.button("Cancel Selected Seats"):
            if seats_to_cancel:
                # Perform cancellation
                cancel_booking(user_id, movie_name, theater_name, timing, seats_to_cancel)
                st.success(
                    f"Successfully cancelled seats {', '.join(seats_to_cancel)} for {movie_name} at {theater_name} on {timing}."
                )
            else:
                st.warning("No seats selected for cancellation. Please select seats to cancel.")

# Fetch registered movies
def get_registered_movies():
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM movies")
    movies = c.fetchall()
    conn.close()
    return movies

# Fetch registered theaters
def get_registered_theaters():
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM theaters")
    theaters = c.fetchall()
    conn.close()
    return theaters

# Fetch registered users
def get_registered_users():
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE role = 'user'")
    users = c.fetchall()
    conn.close()
    return users

# Fetch registered owners
def get_registered_owners():
    conn = get_sqlite_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE role = 'owner'")
    owners = c.fetchall()
    conn.close()
    return owners

# User Interface Components
def user_login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login(username, password)
        if user:
            st.session_state['user'] = user
            st.session_state['is_admin'] = (user[4] == 'admin')
            st.session_state['is_owner'] = (user[4] == 'owner')
            st.session_state['is_user'] = (user[4] == 'user')
            st.session_state['page'] = 'home'
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

def user_signup():
    st.subheader("Sign Up")
    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")
    phone = st.text_input("Phone Number")
    if st.button("Sign Up"):
        if sign_up(username, password, phone):
            st.success("Sign Up successful")
            st.session_state['page'] = 'login'
            st.experimental_rerun()
        else:
            st.error("Username already exists")

def view_bookings():
    st.subheader("Your Bookings")
    if st.session_state['user']:
        user_id = st.session_state['user'][0]
        conn = get_sqlite_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM bookings WHERE user_id = ?", (user_id,))
        user_bookings = c.fetchall()
        conn.close()
        if user_bookings:
            for booking in user_bookings:
                movie = get_movie_details(booking[2])
                theater = get_theater_details(booking[3])
                st.write(f"Movie: {movie[1]}, Theater: {theater[1]}, Time: {booking[4]}, Seats: {booking[5]}")
        else:
            st.write("No bookings found")

def admin_controls():
    if st.session_state['is_admin']:
        st.subheader("Admin Controls")

        with st.expander("Registered Movies"):
            movies = get_registered_movies()
            movies_df = pd.DataFrame(movies, columns=["ID", "Name", "City", "Theater ID", "Timings", "Seats"])
            st.session_state['movies_ids'] = movies_df["ID"].tolist()
            for i, row in movies_df.iterrows():
                cols = st.columns((7, 1))
                cols[0].write(f"{row['Name']} in {row['City']} (Timings: {row['Timings']})")
                cols[1].checkbox("", key=f"movie_{i}")

        with st.expander("Registered Theaters"):
            theaters = get_registered_theaters()
            theaters_df = pd.DataFrame(theaters, columns=["ID", "Name", "City", "Owner ID"])
            st.session_state['theaters_ids'] = theaters_df["ID"].tolist()
            for i, row in theaters_df.iterrows():
                cols = st.columns((7, 1))
                cols[0].write(f"{row['Name']} in {row['City']}")
                cols[1].checkbox("", key=f"theater_{i}")

        with st.expander("Registered Users"):
            users = get_registered_users()
            users_df = pd.DataFrame(users, columns=["ID", "Username", "Password", "Phone", "Role"])
            st.session_state['users_ids'] = users_df["ID"].tolist()
            for i, row in users_df.iterrows():
                cols = st.columns((7, 1))
                cols[0].write(f"User: {row['Username']}, Phone: {row['Phone']}")
                cols[1].checkbox("", key=f"user_{i}")

        with st.expander("Registered Theater Owners"):
            owners = get_registered_owners()
            owners_df = pd.DataFrame(owners, columns=["ID", "Username", "Password", "Phone", "Role"])
            st.session_state['owners_ids'] = owners_df["ID"].tolist()
            for i, row in owners_df.iterrows():
                cols = st.columns((7, 1))
                cols[0].write(f"Owner: {row['Username']}, Phone: {row['Phone']}")
                cols[1].checkbox("", key=f"owner_{i}")

        if st.button("Remove Selected Users/Owners"):
            selected_users = [st.session_state['users_ids'][i] for i in range(len(users_df)) if
                              st.session_state.get(f"user_{i}")]
            selected_owners = [st.session_state['owners_ids'][i] for i in range(len(owners_df)) if
                               st.session_state.get(f"owner_{i}")]
            selected_ids = selected_users + selected_owners
            for user_id in selected_ids:
                remove_user(user_id)
            st.experimental_rerun()

        st.subheader("Add Theater Owner")
        username = st.text_input("New Owner Username")
        password = st.text_input("New Owner Password", type="password")
        phone = st.text_input("Owner Phone Number")
        theater_name = st.text_input("Theater Name")
        if st.button("Add Owner"):
            if add_theater_owner(username, password, phone, theater_name):
                st.success("Theater owner added successfully")
            else:
                st.error("Username already exists")

def owner_controls():
    if st.session_state['is_owner']:
        st.subheader("Owner Controls")
        owner_id = st.session_state['user'][0]
        add_or_remove = st.radio("Add or Remove Movie", ('Add', 'Remove'))
        if add_or_remove == 'Add':
            movie_name = st.text_input("Movie Name")
            city = st.text_input("City")
            conn = get_sqlite_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM theaters WHERE owner_id = ?", (owner_id,))
            theaters = c.fetchall()
            conn.close()
            theater = st.selectbox("Select Theater", theaters, format_func=lambda x: x[1])
            start_time = st.time_input('Select start time')
            end_time = st.time_input('Select end time')
            timings = f"{start_time}-{end_time}"
            rows = st.number_input("Number of rows", min_value=1, step=1)
            cols = st.number_input("Number of columns", min_value=1, step=1)
            seats = f"{rows}x{cols}"
            if st.button("Add Movie"):
                add_movie(owner_id, movie_name, city, theater[0], timings, seats)
                st.success("Movie added successfully")
        elif add_or_remove == 'Remove':
            conn = get_sqlite_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM movies WHERE theater_id IN (SELECT id FROM theaters WHERE owner_id = ?)",
                      (owner_id,))
            movies = c.fetchall()
            conn.close()
            movie = st.selectbox("Select Movie to Remove", movies, format_func=lambda x: x[1])
            if st.button("Remove Movie"):
                remove_movie(movie[0])
                st.success("Movie removed successfully")
        st.write("Booked Tickets:")
        conn = get_sqlite_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM movies WHERE theater_id IN (SELECT id FROM theaters WHERE owner_id = ?)", (owner_id,))
        movies = c.fetchall()
        conn.close()
        for movie in movies:
            bookings = get_bookings_by_movie(movie[0])
            if bookings:
                for booking in bookings:
                    conn = get_sqlite_connection()
                    c = conn.cursor()
                    user = c.execute("SELECT * FROM users WHERE id = ?", (booking[1],)).fetchone()
                    conn.close()
                    st.write(
                        f"Movie: {movie[1]}, User: {user[1]}, Phone: {user[3]}, Time: {booking[4]}, Seats: {booking[5]}")

# Function to handle user input
def handle_input():
    user_input = st.session_state.user_input
    st.session_state['messages'].append(("user", user_input))

    if "movies" in user_input.lower():
        movies = get_available_movies()
        if movies:
            response = "Available movies:\n" + "\n".join(movies)
        else:
            response = "No movies available."
    elif "theaters" in user_input.lower():
        theaters = get_available_theaters()
        if theaters:
            response = "Available theaters:\n" + "\n".join([f"{theater[0]} in {theater[1]}" for theater in theaters])
        else:
            response = "No theaters available."
    elif "book" in user_input.lower() or "seats" in user_input.lower():
        st.session_state['page'] = 'book_tickets'
        response = "Redirecting to booking interface..."
    else:
        response = "I can help you with finding available movies, theaters or booking tickets. Please ask about 'movies', 'theaters' or use 'book' followed by details."

    st.session_state['messages'].append(("bot", response))
    st.session_state.user_input = ""  # Clear input field

# Main Application Logic
st.sidebar.title("Online Movie Ticket Booking")

if st.session_state['user'] is None:
    choice = st.sidebar.selectbox("Choose Action", ["Login", "Sign Up"])
    if choice == "Login":
        st.session_state['page'] = 'login'
        user_login()
    else:
        st.session_state['page'] = 'signup'
        user_signup()
else:
    st.sidebar.write(f"Welcome, {st.session_state['user'][1]}!")
    if st.sidebar.button("Logout"):
        st.session_state['user'] = None
        st.session_state['is_admin'] = False
        st.session_state['is_owner'] = False
        st.session_state['is_user'] = False
        st.session_state['page'] = 'login'
        st.experimental_rerun()
    if st.sidebar.button("Book Tickets"):
        st.session_state['page'] = 'book_tickets'
        st.experimental_rerun()
    if st.sidebar.button("View Bookings"):
        st.session_state['page'] = 'view_bookings'
        st.experimental_rerun()
    if st.sidebar.button("Cancel Ticket"):
        st.session_state['page'] = 'cancel_ticket'
        st.experimental_rerun()

    if st.session_state['is_admin']:
        admin_controls()
    if st.session_state['is_owner']:
        owner_controls()
    if st.session_state['is_user']:
        if st.session_state['page'] == 'book_tickets':
            book_tickets()
        elif st.session_state['page'] == 'view_bookings':
            view_bookings()
        elif st.session_state['page'] == 'cancel_ticket':
            cancel_ticket()
        else:
            # Chatbot interface for user
            st.title("Cinema Ticket Chatbot")
            chat_container = st.container()
            # Display chat messages
            with chat_container:
                for user, msg in st.session_state['messages']:
                    if user == "user":
                        st.markdown(f"**You:** {msg}")
                    else:
                        st.markdown(f"**Bot:** {msg}")
            # Fixed input field at the bottom
            st.markdown(
                """
                <style>
                .fixed-input {
                    position: fixed;
                    bottom: 0;
                    width: 100%;
                    background-color: white;
                    padding: 10px;
                    box-shadow: 0 -1px 5px rgba(0, 0, 0, 0.1);
                }
                .fixed-input > div {
                    max-width: 800px;
                    margin: auto;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            input_placeholder = st.empty()
            with input_placeholder.container():
                user_input = st.text_input("Enter your message here", key="user_input", on_change=handle_input,
                                           placeholder="Type a message...", label_visibility="collapsed")
