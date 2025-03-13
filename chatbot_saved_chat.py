import os
import sys
from datetime import datetime
import json
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, FunctionMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv, find_dotenv
from Database import Database

db = Database()

def login(email: str, password: str):
    try:
        response = db.client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response.user, None
    except Exception as e:
        return None, str(e)

def signup(email: str, password: str):
    try:
        response = db.client.auth.sign_up({
            "email": email,
            "password": password
        })
        return response.user, None
    except Exception as e:
        return None, str(e)

def authenticate():
    while True:
        print("\n=== Authentication ===")
        choice = input("1. Login\n2. Sign up\n3. Exit\nChoose an option (1-3): ")
        
        if choice == "3":
            print("Goodbye!")
            sys.exit(0)
            
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        
        if choice == "1":
            user, error = login(email, password)
            if user:
                print("Login successful!")
                return user
            print(f"Login failed: {error}")
        
        elif choice == "2":
            user, error = signup(email, password)
            if user:
                print("Sign up successful! Please log in.")
            else:
                print(f"Sign up failed: {error}")
        
        else:
            print("Invalid option. Please try again.")

def get_cheapest_rooms():
    limit = 5
    response = db.client.table("hotel_rooms").select("*").order("price_USD").limit(limit).execute()
    data = json.dumps(response.data)
    return data

def get_current_time():
    current_time = datetime.now()
    return f"The current time is {current_time.strftime('%H:%M:%S')}."

def save_chat_session(user_id: str, messages: list):
    try:
        serialized_messages = []
        for msg in messages:
            # convert messages to a serializable format
            pass
        
        # Save to database
        response = db.client.table("chat_sessions").insert({
            "user_id": user_id,
            "messages": json.dumps(serialized_messages),
            "created_at": datetime.now().isoformat()
        }).execute()
        
        return response.data[0], None
    except Exception as e:
        return None, str(e)

def get_user_chat_sessions(user_id: str):
    try:
        response = db.client.table("chat_sessions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return response.data, None
    except Exception as e:
        return None, str(e)

def load_previous_chat_session(user_id: str):
    try:
        # Load the most recent chat session
        pass
    except Exception as e:
        return None, str(e)

FUNCTION_DEFINITIONS = [
    {
        "name": "get_current_time",
        "description": "Returns the current time.",
    },
    {
        "name": "get_cheapest_rooms",
        "description": "Returns the cheapest rooms from our database.",
    }
]

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

if "OPENAI_API_KEY" not in os.environ:
    print("Please set the OPENAI_API_KEY environment variable.")
    sys.exit(1)

model = ChatOpenAI(model="gpt-4o-mini",temperature = 0.5)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant who is friendly and detailed.{personality}"),
    MessagesPlaceholder(variable_name="history"),
    ("human","{input}")
])

personality = "You like explaining things like a helpful hotel concierge. You are able to check the cheapest rooms and have the capability to check the current time."

history = []

# Authenticate user before starting the chat
user = authenticate()   
print(f"\nWelcome {user.email}!")

# Load previous chat session
history, error = load_previous_chat_session(user.id)
if error:
    print(f"Could not load previous chat session: {error}")
    history = []
else:
    print("Previous chat session loaded!")

print("Welcome to the OpenAI Chatbot. Please ask me anything!")

while True:
    user_input = input("You:")
    if user_input.lower() == "exit":
        # Save the chat session before exiting
        if user:
            save_chat_session(user.id, history)
            print("Chat session saved!")
        print("Goodbye!")
        break
    
    formatted_messages = prompt.format_messages(personality=personality,history=history,input=user_input)
    
    try:
        response = model.invoke(formatted_messages, functions=FUNCTION_DEFINITIONS)

        function_call = response.additional_kwargs.get("function_call")

        if function_call:
            function_name = function_call["name"]
            if function_name == "get_current_time":
                result = get_current_time()
            elif function_name == "get_cheapest_rooms":
                result = get_cheapest_rooms()
            else:
                result = "I'm sorry, I don't know how to do that."

            function_message = FunctionMessage(content=result,name=function_name)

            formatted_messages.append(function_message)

            final_response = model.invoke(formatted_messages)

            print(f"\nAI: {final_response.content}\n")

            history.append(HumanMessage(content=user_input))
            history.append(function_message)
            history.append(AIMessage(content=final_response.content))
            
        else:
            print(f"\nAI: {response.content}\n")
            history.append(HumanMessage(content=user_input))
            history.append(AIMessage(content=response.content))
    except Exception as e:
        print("Error:", e)










