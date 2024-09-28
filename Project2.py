import tkinter as tk
from tkinter import messagebox
import sqlite3
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import secrets
import string

# Function to generate a key using a master password and store it securely
def derive_key(master_password):
    salt = b'salt_'  # Use a more secure salt in practice
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key

# Encrypt the data using Fernet (AES-256 Encryption)
def encrypt_data(data, key):
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data

# Decrypt the data using Fernet
def decrypt_data(encrypted_data, key):
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return decrypted_data

def generate_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

# Setting up SQLite database and table
def setup_db():
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS passwords
                      (id INTEGER PRIMARY KEY, website TEXT, username TEXT, password TEXT)''')
    conn.commit()
    conn.close()

# Save password to SQLite database
def save_password(website, username, password, key):
    encrypted_password = encrypt_data(password, key)
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)",
                   (website, username, encrypted_password))
    conn.commit()
    conn.close()

# Load saved passwords from SQLite database
def load_passwords(key):
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute("SELECT website, username, password FROM passwords")
    rows = cursor.fetchall()
    passwords = []
    for row in rows:
        decrypted_password = decrypt_data(row[2], key)
        passwords.append(f"Website: {row[0]}, Username: {row[1]}, Password: {decrypted_password}")
    conn.close()
    return passwords

# GUI application using Tkinter
class PasswordManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Manager")
        self.geometry("400x400")
        self.key = None
        
        # Set up the database
        setup_db()

        # Create GUI components
        self.create_widgets()

    def create_widgets(self):
        # Master password entry
        tk.Label(self, text="Master Password:").pack(pady=5)
        self.master_password_entry = tk.Entry(self, show="*", width=30)
        self.master_password_entry.pack(pady=5)
        tk.Button(self, text="Set Master Password", command=self.set_master_password).pack(pady=5)

        # Website Entry
        tk.Label(self, text="Website:").pack(pady=5)
        self.website_entry = tk.Entry(self, width=30)
        self.website_entry.pack(pady=5)

        # Username Entry
        tk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack(pady=5)

        # Password Entry
        tk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self, width=30)
        self.password_entry.pack(pady=5)

        # Generate password button
        tk.Button(self, text="Generate Password", command=self.generate_password).pack(pady=10)

        # Save password button
        tk.Button(self, text="Save Password", command=self.save_password).pack(pady=10)

        # View saved passwords button
        tk.Button(self, text="View Passwords", command=self.view_passwords).pack(pady=10)

    def set_master_password(self):
        master_password = self.master_password_entry.get()
        if master_password:
            self.key = derive_key(master_password)
            messagebox.showinfo("Master Password", "Master Password Set.")
        else:
            messagebox.showerror("Error", "Please enter a master password.")

    def generate_password(self):
        password = generate_password()
        messagebox.showinfo("Generated Password", f"Your password is: {password}")
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

    def save_password(self):
        if not self.key:
            messagebox.showerror("Error", "Set a master password first.")
            return
        
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if website and username and password:
            save_password(website, username, password, self.key)
            messagebox.showinfo("Success", "Password saved successfully!")
        else:
            messagebox.showwarning("Error", "Please fill in all fields.")

    def view_passwords(self):
        if not self.key:
            messagebox.showerror("Error", "Set a master password first.")
            return
        
        passwords = load_passwords(self.key)
        if passwords:
            passwords_str = "\n".join(passwords)
            messagebox.showinfo("Saved Passwords", passwords_str)
        else:
            messagebox.showinfo("Saved Passwords", "No passwords saved yet.")

# Run application
if __name__ == "__main__":
    app = PasswordManagerApp()
    app.mainloop()