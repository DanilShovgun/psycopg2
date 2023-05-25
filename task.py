import psycopg2

def create_db(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS phones (
            id SERIAL PRIMARY KEY,
            client_id INTEGER REFERENCES clients(id),
            phone VARCHAR(255) UNIQUE NOT NULL
        );
    """)
    conn.commit()


def add_client(conn, first_name, last_name, email, phones=None):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id",
                   (first_name, last_name, email))
    client_id = cursor.fetchone()[0]
    if phones:
        for phone in phones:
            cursor.execute("INSERT INTO phones (client_id, phone) VALUES (%s, %s)", (client_id, phone))
    conn.commit()


def add_phone(conn, client_id, phone):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO phones (client_id, phone) VALUES (%s, %s)", (client_id, phone))
    conn.commit()


def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    cursor = conn.cursor()
    if first_name:
        cursor.execute("UPDATE clients SET first_name = %s WHERE id = %s", (first_name, client_id))
    if last_name:
        cursor.execute("UPDATE clients SET last_name = %s WHERE id = %s", (last_name, client_id))
    if email:
        cursor.execute("UPDATE clients SET email = %s WHERE id = %s", (email, client_id))
    if phones:
        cursor.execute("DELETE FROM phones WHERE client_id = %s", (client_id,))
        for phone in phones:
            cursor.execute("INSERT INTO phones (client_id, phone) VALUES (%s, %s)", (client_id, phone))
    conn.commit()


def delete_phone(conn, client_id, phone):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM phones WHERE client_id = %s AND phone = %s", (client_id, phone))
    conn.commit()


def delete_client(conn, client_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM phones WHERE client_id = %s", (client_id,))
    cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
    conn.commit()


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    cursor = conn.cursor()
    if first_name:
        cursor.execute("SELECT * FROM clients WHERE first_name = %s", (first_name,))
    elif last_name:
        cursor.execute("SELECT * FROM clients WHERE last_name = %s", (last_name,))
    elif email:
        cursor.execute("SELECT * FROM clients WHERE email = %s", (email,))
    elif phone:
        cursor.execute("SELECT * FROM clients INNER JOIN phones ON clients.id = phones.client_id WHERE phones.phone = %s", (phone,))
    else:
        return None
    return cursor.fetchall()


with psycopg2.connect(database="clients_db", user="postgres", password="postgres") as conn:
    create_db(conn)
    add_client(conn, "John", "Doe", "john.doe@example.com", ["555-1234", "555-5678"])
    add_phone(conn, 1, "555-9999")
    change_client(conn, 1, last_name="Smith", email="john.smith@example.com")
    delete_phone(conn, 1, "555-1234")
    print(find_client(conn, last_name="Smith"))
    delete_client(conn, 1)

conn.close()