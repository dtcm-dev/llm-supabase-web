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
    ## implement this function
    pass


def signup(email: str, password: str):
    ## implement this function
    pass

def authenticate():
    ## implement this function
    pass

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










