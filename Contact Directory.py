import mysql.connector
import hashlib
import getpass
from utils import get_int_range
from termcolor import colored

# Connect to MySQL Database
conn = mysql.connector.connect(
    host="localhost",
    user="root",        
    password="karandeep",        
    database="contact_directory"
)
cursor = conn.cursor()

# Create Tables
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Employee') NOT NULL
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prefix VARCHAR(10),
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    company VARCHAR(100),
    position VARCHAR(100)
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS phone_numbers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contact_id INT NOT NULL,
    type ENUM('Home', 'Work', 'Personal'),
    number VARCHAR(15) NOT NULL,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
)''')

conn.commit()

# Ensure Default Admin Exists
def create_admin():
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        hashed_password = hashlib.sha256("admin".encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'Admin')", ("admin", hashed_password))
        conn.commit()

create_admin()

# Password Hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User Authentication
def login():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    hashed_password = hash_password(password)
    
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, hashed_password))
    user = cursor.fetchone()
    
    if user:
        return user  
    else:
        print("Invalid login. Try again.")
        return None

# Add Employee (Admin Only)
def add_employee():
    username = input("Enter new employee username: ")
    password = getpass.getpass("Enter password: ")
    hashed_password = hash_password(password)
    
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'Employee')", (username, hashed_password))
        conn.commit()
        print(f"Employee '{username}' added successfully.")
    except mysql.connector.IntegrityError:
        print("Username already exists!")

# View All Contacts
def view_contacts():
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()
    
    if not contacts:
        print("No contacts found.")
        return
    
    for contact in contacts:
        print(f"\nID: {contact[0]}\nName: {contact[1] or ''} {contact[2]} {contact[3] or ''} {contact[4]}\nEmail: {contact[5] or 'N/A'}\nCompany: {contact[6] or 'N/A'}\nPosition: {contact[7] or 'N/A'}")
        
        cursor.execute("SELECT type, number FROM phone_numbers WHERE contact_id=%s", (contact[0],))
        phones = cursor.fetchall()
        for phone in phones:
            print(f"   {phone[0]}: {phone[1]}")

# Add Contact (Admin Only)
def add_contact():
    prefix = input("Prefix (Optional): ")
    first_name = input("First Name: ")
    middle_name = input("Middle Name (Optional): ")
    last_name = input("Last Name: ")
    email = input("Email (Optional): ")
    company = input("Company (Optional): ")
    position = input("Position (Optional): ")
    
    cursor.execute("INSERT INTO contacts (prefix, first_name, middle_name, last_name, email, company, position) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                   (prefix, first_name, middle_name, last_name, email, company, position))
    contact_id = cursor.lastrowid
    
    while True:
        phone_type = input("Enter phone type (Home/Work/Personal): ")
        phone_number = input("Enter phone number: ")
        cursor.execute("INSERT INTO phone_numbers (contact_id, type, number) VALUES (%s, %s, %s)", (contact_id, phone_type, phone_number))
        more = input("Add another phone number? (y/n): ")
        if more.lower() != 'y':
            break
    
    conn.commit()
    print("Contact added successfully.")

# Delete Contact (Admin Only)
def delete_contact():
    contact_id = input("Enter Contact ID to delete: ")
    cursor.execute("DELETE FROM contacts WHERE id=%s", (contact_id,))
    conn.commit()
    print("Contact deleted successfully.")

# Main Menu
def main_menu(user):
    while True:
        print("\nMain Menu")
        print("1. View Contacts")
        print("2. Log Out")
        
        if user[3] == 'Admin':  # Admin-only options
            print("3. Add Employee")
            print("4. Add Contact")
            print("5. Delete Contact")
            print(colored("Enter Choice: ", "yellow"), end="")

        choice = get_int_range(1, 2 if user[3] != "Admin" else 5)

        if choice == "1":
            view_contacts()
        elif choice == "2":
            print("Logging out...")
            break
        elif choice == "3" and user[3] == 'Admin':
            add_employee()
        elif choice == "4" and user[3] == 'Admin':
            add_contact()
        elif choice == "5" and user[3] == 'Admin':
            delete_contact()
        else:
            print("Invalid choice. Try again.")

# Start App
def run():
    while True:
        user = login()
        if user:
            main_menu(user)

# Run the app
if __name__ == "__main__":
    run()
