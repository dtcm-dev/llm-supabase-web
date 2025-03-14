from dotenv import load_dotenv, find_dotenv
from supabase import create_client, Client
import os
import sys

class Database:
    def __init__(self):
        dotenv_path = find_dotenv()
        load_dotenv(dotenv_path)
        
        self._url = os.getenv("SUPABASE_URL")
        self._key = os.getenv("SUPABASE_KEY")
        self._client = create_client(self._url, self._key)
    
    @property
    def client(self):
        return self._client

    def login(self, email: str, password: str):
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return response.user, None
        except Exception as e:
            return None, str(e)

    def signup(self, email: str, password: str):
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            return response.user, None
        except Exception as e:
            return None, str(e)

    def authenticate(self):
        while True:
            print("\n=== Authentication ===")
            choice = input("1. Login\n2. Sign up\n3. Exit Program\nChoose an option (1-3): ")
            
            if choice == "3":
                print("Goodbye!")
                sys.exit(0)
                
            email = input("Enter your email: ")
            password = input("Enter your password: ")
            
            if choice == "1":
                user, error = self.login(email, password)
                if user:
                    print("Login successful!")
                    return user
                print(f"Login failed: {error}")
            
            elif choice == "2":
                user, error = self.signup(email, password)
                if user:
                    print("Sign up successful! Please log in.")
                else:
                    print(f"Sign up failed: {error}")
            
            else:
                print("Invalid option. Please try again.")
    