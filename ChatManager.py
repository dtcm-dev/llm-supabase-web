from typing import Dict, Optional
import os
from profiles import profiles
from Database import Database
from Chatbot import Chatbot

class ChatManager:
    def __init__(self):
        self.db = Database()
        self.chatbot = None
        self.user = None
        
    def run(self):
        """Main entry point for the chat manager."""
        # First authenticate the user
        self.user = self.db.authenticate()
        if not self.user:
            return
            
        # Initialize chatbot with database and user
        self.chatbot = Chatbot(db=self.db, user=self.user)
        
        print(f"\nWelcome {self.user.email}!")
        
        # Ask user for session choice
        choice = self._get_session_choice()
        if choice == "1":
            if self._load_previous_session():
                self._start_chat()
            else:
                print("\nNo previous sessions found or error loading session.")
                if self._confirm_new_session():
                    self._create_new_session()
                else:
                    return
        else:
            self._create_new_session()
    
    def _get_session_choice(self) -> str:
        """Ask user whether to load previous session or start new one."""
        while True:
            print("\nWhat would you like to do?")
            print("1. Load a previous chat session")
            print("2. Start a new session")
            choice = input("Enter your choice (1 or 2): ").strip()
            
            if choice in ["1", "2"]:
                return choice
            print("Invalid choice. Please enter 1 or 2.")
    
    def _load_previous_session(self) -> bool:
        """Load the previous chat session."""
        history, error = self.chatbot.load_previous_chat_session()
        if error or not history:
            return False
        print("Previous chat session loaded successfully!")
        return True
    
    def _confirm_new_session(self) -> bool:
        """Confirm if user wants to start a new session."""
        while True:
            choice = input("\nWould you like to start a new session instead? (y/n): ").strip().lower()
            if choice in ["y", "yes"]:
                return True
            if choice in ["n", "no"]:
                return False
            print("Please enter 'y' or 'n'.")
    
    def _create_new_session(self):
        """Create a new chat session with selected profile."""
        profile = self._select_profile()

        ## implement profile selection
        
        self._start_chat()
    
    def _start_chat(self):
        """Start the chat interaction."""
        self.chatbot.start()
    
    def _select_profile(self) -> Optional[Dict]:
        """Handle profile selection for new chat sessions."""
        while True:
            print("\nPlease select a profile for your new chat session:")
            for id, profile in profiles.items():
                print(f"{id}. {profile['name']}")
                
            try:
                choice = int(input("\nEnter the profile number: "))
                if choice in profiles:
                    return profiles[choice]
                print("Invalid profile number. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
