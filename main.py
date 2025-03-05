import os
import mysql.connector
import hashlib
import getpass
from dotenv import load_dotenv
from utils import get_int_range, clear_screen

load_dotenv()

# Database Connection
conn = mysql.connector.connect(
    host=os.environ.get("HOST"),
    user=os.environ.get("USER"),
    password=os.environ.get("PASSWORD"),
    database=os.environ.get("DATABASE"),
)
cursor = conn.cursor()

# Master Password (Stored securely in a real-world scenario)
MASTER_PASSWORD = "SuperSecureMasterKey123"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_company():
    clear_screen()
    master_key = getpass.getpass("\U0001F511 Enter the master password to create a company: ")
    if master_key != MASTER_PASSWORD:
        print("\u274C Incorrect master password! You are not authorized to create a company.")
        return
    
    name = input("\U0001F3E2 Enter new company name: ").strip()
    cursor.execute("SELECT company_id FROM companies WHERE name = %s", (name,))
    if cursor.fetchone():
        print("\u26A0 A company with this name already exists! Try another name.")
        return
    
    special_access_key = hash_password(input("\U0001F511 Set special access key for company: "))
    cursor.execute("INSERT INTO companies (name, special_access_key) VALUES (%s, %s)", (name, special_access_key))
    conn.commit()
    company_id = cursor.lastrowid
    
    print(f"\u2705 Company '{name}' created successfully!")
    username = input("\U0001F464 Set admin username: ").strip()
    password = getpass.getpass("\U0001F511 Set admin password: ")
    
    cursor.execute("INSERT INTO users (username, password_hash, role, company_id) VALUES (%s, %s, 'admin', %s)",
                   (username, hash_password(password), company_id))
    conn.commit()
    print(f"\u2705 Admin '{username}' created successfully!")

def login_company():
    clear_screen()
    cursor.execute("SELECT company_id, name FROM companies")
    companies = cursor.fetchall()
    
    if not companies:
        print("⚠️ No companies found! Please create a company first.")
        return None
    
    print("\n🏢 Available Companies:")
    for idx, (company_id, name) in enumerate(companies, start=1):
        print(f"{idx}. {name}")
    
    try:
        choice = int(input("🔹 Select a company (Enter number): "))
        if 1 <= choice <= len(companies):
            return companies[choice - 1][0]  # Return selected company ID
        else:
            print("⚠️ Invalid choice!")
            return None
    except ValueError:
        print("⚠️ Please enter a valid number!")
        return None

def login_user(company_id):
    clear_screen()
    username = input("\U0001F464 Enter username: ").strip()
    password = getpass.getpass("\U0001F511 Enter password: ")
    
    cursor.execute("SELECT user_id, role FROM users WHERE username = %s AND password_hash = %s AND company_id = %s",
                   (username, hash_password(password), company_id))
    user = cursor.fetchone()
    
    if user:
        print("\u2705 Login successful!")
        return user[0], user[1], company_id  # (user_id, role, company_id)
    else:
        print("\u26A0 Invalid credentials!")
        return None

def add_employee(company_id, role):
    if role != 'admin':
        print("⛔ Only admins can add employees!")
        return
    
    username = input("Enter employee username: ").strip()
    password = getpass.getpass("Enter employee password: ")
    cursor.execute("INSERT INTO users (username, password_hash, role, company_id) VALUES (%s, %s, 'employee', %s)",
                   (username, hash_password(password), company_id))
    conn.commit()
    print(f"✅ Employee '{username}' added successfully!")

def delete_employee(company_id, role):
    if role != 'admin':
        print("⛔ Only admins can delete employees!")
        return
    
    username = input("Enter employee username to delete: ").strip()
    cursor.execute("DELETE FROM users WHERE username = %s AND company_id = %s AND role = 'employee'", (username, company_id))
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✅ Employee '{username}' deleted successfully!")
    else:
        print("⚠️ Employee not found or cannot be deleted!")

def view_contacts(company_id):
    clear_screen()
    cursor.execute("SELECT contact_id, first_name, last_name FROM contacts WHERE company_id = %s", (company_id,))
    contacts = cursor.fetchall()
    
    if not contacts:
        print("📭 No contacts found!")
        return
    
    print("\n📞 Contact Directory:")
    contact_dict = {}  # Dictionary to map IDs for selection

    for index, contact in enumerate(contacts, start=1):
        contact_id, first_name, last_name = contact
        contact_dict[index] = contact_id  # Map index to contact_id
        print(f"{index}. {first_name} {last_name}")

    while True:
        try:
            choice = int(input("\nEnter the number of the contact to view details (or 0 to go back): "))
            if choice == 0:
                return
            if choice in contact_dict:
                selected_id = contact_dict[choice]
                show_contact_details(selected_id)
                break  # Exit loop after showing details
            else:
                print("❌ Invalid choice. Please select a valid number.")
        except ValueError:
            print("❌ Please enter a valid number.")

def show_contact_details(contact_id):
    clear_screen()
    cursor.execute("""
        SELECT contact_id, prefix, first_name, middle_name, last_name, email, 
               home_phone, work_phone, personal_phone, company, position 
        FROM contacts WHERE contact_id = %s
    """, (contact_id,))
    
    contact = cursor.fetchone()
    
    if not contact:
        print("❌ Contact not found!")
        return

    print("\n📞 Contact Details:")
    print("-----------------------------")
    print(f"ID: {contact[0]}")
    print(f"👤 Name: {contact[1] or ''} {contact[2]} {contact[3] or ''} {contact[4]}")
    print(f"📧 Email: {contact[5] or 'N/A'}")
    print(f"🏠 Home Phone: {contact[6] or 'N/A'}")
    print(f"💼 Work Phone: {contact[7] or 'N/A'}")
    print(f"📱 Personal Phone: {contact[8]}")
    print(f"🏢 Company: {contact[9] or 'N/A'}")
    print(f"💼 Position: {contact[10] or 'N/A'}")


def add_contact(company_id, role):
    clear_screen()
    if role != 'admin':
        print("⛔ Only admins can add contacts!")
        return
    
    print("\n📌 Add New Contact:")
    prefix = input("Enter Prefix (Optional): ").strip()
    first_name = input("Enter First Name: ").strip()
    middle_name = input("Enter Middle Name (Optional): ").strip()
    last_name = input("Enter Last Name: ").strip()
    email = input("Enter Email (Optional): ").strip()
    
    # Ensure at least one phone number is provided
    home_phone = input("Enter Home Phone (Optional): ").strip()
    work_phone = input("Enter Work Phone (Optional): ").strip()
    personal_phone = input("Enter Personal Phone (Required): ").strip()
    
    if not personal_phone:
        print("⚠️ Personal phone number is required!")
        return
    
    company = input("Enter Company Name (Optional): ").strip()
    position = input("Enter Position (Optional): ").strip()
    
    cursor.execute(
        "INSERT INTO contacts (company_id, prefix, first_name, middle_name, last_name, email, home_phone, work_phone, personal_phone, company, position) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (company_id, prefix, first_name, middle_name, last_name, email, home_phone, work_phone, personal_phone, company, position)
    )
    conn.commit()
    print("✅ Contact added successfully!")


def edit_contact(company_id, role):
    clear_screen()

    if role != 'admin':
        print("⛔ Only admins can edit contacts!")
        return

    # Fetch and display contact names and IDs
    cursor.execute("SELECT contact_id, first_name, last_name FROM contacts WHERE company_id = %s", (company_id,))
    contacts = cursor.fetchall()

    if not contacts:
        print("📭 No contacts found!")
        return

    print("\n📞 Contact Directory:")
    contact_dict = {}  # Map index to contact_id

    for index, contact in enumerate(contacts, start=1):
        contact_id, first_name, last_name = contact
        contact_dict[index] = contact_id
        print(f"{index}. {first_name} {last_name}")

    while True:
        try:
            choice = int(input("\nEnter the number of the contact to edit (or 0 to cancel): "))
            if choice == 0:
                return
            if choice in contact_dict:
                selected_id = contact_dict[choice]
                break
            else:
                print("❌ Invalid choice. Please select a valid number.")
        except ValueError:
            print("❌ Please enter a valid number.")

    # Fetch current details of the selected contact
    cursor.execute("""
        SELECT prefix, first_name, middle_name, last_name, email, 
               home_phone, work_phone, personal_phone, company, position 
        FROM contacts WHERE contact_id = %s AND company_id = %s
    """, (selected_id, company_id))
    
    contact = cursor.fetchone()

    if not contact:
        print("⚠️ Contact not found or does not belong to your company!")
        return

    (current_prefix, current_first, current_middle, current_last, current_email, 
     current_home, current_work, current_personal, current_company, current_position) = contact

    # Prompt user to enter new values (leave blank to keep existing ones)
    print("\n📝 Edit Contact Details (leave blank to keep current values)")
    new_prefix = input(f"Enter new prefix [{current_prefix or 'N/A'}]: ").strip() or current_prefix
    new_first = input(f"Enter new first name [{current_first}]: ").strip() or current_first
    new_middle = input(f"Enter new middle name [{current_middle or 'N/A'}]: ").strip() or current_middle
    new_last = input(f"Enter new last name [{current_last}]: ").strip() or current_last
    new_email = input(f"Enter new email [{current_email or 'N/A'}]: ").strip() or current_email
    new_home = input(f"Enter new home phone [{current_home or 'N/A'}]: ").strip() or current_home
    new_work = input(f"Enter new work phone [{current_work or 'N/A'}]: ").strip() or current_work
    new_personal = input(f"Enter new personal phone [{current_personal}]: ").strip() or current_personal
    new_company = input(f"Enter new company [{current_company or 'N/A'}]: ").strip() or current_company
    new_position = input(f"Enter new position [{current_position or 'N/A'}]: ").strip() or current_position

    # Update database with new values
    cursor.execute("""
        UPDATE contacts 
        SET prefix = %s, first_name = %s, middle_name = %s, last_name = %s, 
            email = %s, home_phone = %s, work_phone = %s, personal_phone = %s, 
            company = %s, position = %s
        WHERE contact_id = %s AND company_id = %s
    """, (new_prefix, new_first, new_middle, new_last, new_email, 
          new_home, new_work, new_personal, new_company, new_position, 
          selected_id, company_id))

    conn.commit()
    print("✅ Contact updated successfully!")


def delete_contact(company_id, role):
    clear_screen()
    if role != 'admin':
        print("⛔ Only admins can delete contacts!")
        return
    
    contact_id = input("Enter Contact ID to delete: ").strip()
    cursor.execute("DELETE FROM contacts WHERE contact_id = %s AND company_id = %s", (contact_id, company_id))
    conn.commit()
    print("✅ Contact deleted successfully!")

def main():
    clear_screen()
    print("\U0001F4DE Welcome to the Contact Directory")
    while True:
        print("\n1️⃣ Create New Company (Master Password Required)")
        print("2️⃣ Log in to a Company")
        print("3️⃣ Exit")
        choice = input("🔹 Choose an option: ")
        
        if choice == "1":
            create_company()
        elif choice == "2":
            company_id = login_company()
            if company_id:
                user = login_user(company_id)
                if user:
                    user_id, role, company_id = user
                    while True:
                        print("\n📌 Main Menu")
                        print("1️⃣ View Contacts")
                        if role == 'admin':
                            print("2️⃣ Add Contact")
                            print("3️⃣ Edit Contact")
                            print("4️⃣ Delete Contact")
                            print("5️⃣ Add Employee")
                            print("6️⃣ Delete Employee")
                        print("7️⃣ Logout")
                        
                        option = input("🔹 Choose an option: ")
                        
                        if option == "1":
                            view_contacts(company_id)
                        elif option == "2" and role == 'admin':
                            add_contact(company_id, role)
                        elif option == "3" and role == 'admin':
                            edit_contact(company_id, role)
                        elif option == "4" and role == 'admin':
                            delete_contact(company_id, role)
                        elif option == "5" and role == 'admin':
                            add_employee(company_id, role)
                        elif option == "6" and role == 'admin':
                            delete_employee(company_id, role)
                        elif option == "7":
                            print("\U0001F44B Logging out...")
                            break
        elif choice == "3":
            print("👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
