import os
import json
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, FunctionMessage, SystemMessage
from typing import List, Dict, Any, Optional
from config import FUNCTION_DEFINITIONS

class Chatbot:
    def __init__(self, db=None, user=None):
        self.db = db
        self.user = user
        self.history = []
        
        # Initialize OpenAI model
        if "OPENAI_API_KEY" not in os.environ:
            raise EnvironmentError("Please set the OPENAI_API_KEY environment variable.")
        
        self.model = ChatOpenAI(model="gpt-4o-mini", temperature=1)
        self.personality = "You like explaining things like a helpful hotel concierge. You are able to check the cheapest rooms and have the capability to check the current time."
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant who is friendly and detailed.{personality}"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

    def get_cheapest_rooms(self):
        limit = 5
        response = self.db.client.table("hotel_rooms").select("*").order("price_USD").limit(limit).execute()
        return json.dumps(response.data)

    def get_current_time(self):
        current_time = datetime.now()
        return f"The current time is {current_time.strftime('%H:%M:%S')}."

    def save_chat_session(self):
        try:
            serialized_messages = []
            for msg in self.history:
                if isinstance(msg, HumanMessage):
                    serialized_messages.append({"role": "human", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    serialized_messages.append({"role": "ai", "content": msg.content})
                elif isinstance(msg, FunctionMessage):
                    serialized_messages.append({"role": "function", "content": msg.content, "name": msg.name})

            response = self.db.client.table("chat_sessions").insert({
                "user_id": self.user.id,
                "messages": json.dumps(serialized_messages),
                "created_at": datetime.now().isoformat()
            }).execute()

            return response.data[0], None
        except Exception as e:
            return None, str(e)

    def load_previous_chat_session(self):
        try:
            response = self.db.client.table("chat_sessions").select("*").eq("user_id", self.user.id).order("created_at", desc=True).execute()
            
            if not response.data:
                return [], None
            
            latest_session = response.data[0]
            messages = json.loads(latest_session["messages"])
            
            for msg in messages:
                if msg["role"] == "human":
                    self.history.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "ai":
                    self.history.append(AIMessage(content=msg["content"]))
                elif msg["role"] == "function":
                    self.history.append(FunctionMessage(content=msg["content"], name=msg["name"]))
            
            return self.history, None
        except Exception as e:
            return None, str(e)

    def process_user_input(self, user_input: str):
        try:
            formatted_messages = self.prompt.format_messages(
                personality=self.personality,
                history=self.history,
                input=user_input
            )
            
            response = self.model.invoke(formatted_messages, functions=FUNCTION_DEFINITIONS)
            function_call = response.additional_kwargs.get("function_call")

            if function_call:
                function_name = function_call["name"]
                if function_name == "get_current_time":
                    result = self.get_current_time()
                elif function_name == "get_cheapest_rooms":
                    result = self.get_cheapest_rooms()
                else:
                    result = "I'm sorry, I don't know how to do that."

                function_message = FunctionMessage(content=result, name=function_name)
                formatted_messages.append(function_message)
                final_response = self.model.invoke(formatted_messages)

                self.history.extend([
                    HumanMessage(content=user_input),
                    function_message,
                    AIMessage(content=final_response.content)
                ])
                
                return final_response.content
            else:
                self.history.extend([
                    HumanMessage(content=user_input),
                    AIMessage(content=response.content)
                ])
                return response.content

        except Exception as e:
            return f"Error: {str(e)}"

    def start(self):
        print("Starting chat...")

        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                self.save_chat_session()
                print("Chat session saved!")
                print("Goodbye!")
                break
            
            response = self.process_user_input(user_input)
            print(f"\nAI: {response}\n")