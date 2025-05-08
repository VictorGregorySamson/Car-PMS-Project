from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI 
from langchain_core.tools import tool
from dotenv import load_dotenv

from src.core.templates import CorePromptTemplates
import random, re

load_dotenv()

GREETING_RESPONSES = [
    "Hi there! How can I help you today?",
    "Hello! What can I do for you?",
    "Hey! Need any assistance with your staff portal?",
    "Hi, great to see you! How can I assist?"
]

class ChatbotHelper:
    '''This class handles functions that interact with the chatbot'''
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o")
        self.llm_mini = ChatOpenAI(model="gpt-4o-mini")
        self.csv_agent = CSVAgent()

    def classify_query(self, query_data):
        '''Classify the query type to determine the processing route'''
        query = query_data['query'].strip().lower()
        
        # Check for greeting phrases explicitly
        if query in ["hi", "hello", "hey", "slay"]:
            print("[CLASSIFY QUERY] Detected greeting.")
            return {'query': query_data['query'], 'type': 'greeting'}
        
        # Otherwise, delegate to the LLM for classification.
        prompt = CorePromptTemplates.classify_query_prompt(query_data['query'])
        response = self.llm.invoke(prompt).content.strip()
        print('[CLASSIFY QUERY] Classification:', response)
        return {'query': query_data['query'], 'type': response}

    def handle_greeting(self):
        '''Return a dynamic greeting response'''
        return random.choice(GREETING_RESPONSES)
    
    def extract_staff_name(self, query: str) -> str:
        """Extract the staff's username or name from the query."""
        # Sample approach: match common username pattern like 'adamk', 'kellyk'
        import re
        match = re.search(r'\b([a-z]{3,5}k)\b', query.lower())  # matches 'adamk', etc.
        return match.group(1) if match else "the staff"

    def get_response(self, query_data):
        '''Get the response for the query'''
        query = query_data['query']
        query_type = query_data['type']
        
        # 1️⃣ Greetings
        if query_type == 'greeting':
            return self.handle_greeting()
        
        try:
            data = self.csv_agent.get_agent_response(query=query, type=query_type)
            if not data.get('is_successful'):
                return data.get('response', "I'm sorry, I couldn't process that query.")
            
            if query_type == 'manual_query':
                prompt 
                
            
            # 2️⃣ Burnout factors (existing)
            if query_type == 'burnout_factors':
                data['response']['staff_name'] = self.extract_staff_name(query)
                response_data = data['response']
                response_data['total_time_spent'] = response_data.get('total_time_spent_per_minutes', 'N/A')
                response_data['task_count'] = response_data.get('number_of_tasks', 'N/A')
                response_data['avg_time_per_task'] = response_data.get('average_time_per_task_per_minutes', 'N/A')
                
                print("[DEBUG] Burnout data:", response_data)
                prompt = CorePromptTemplates.show_burnout_factors_prompt(query, response_data)
            
            # 3️⃣ Holidays by user
            elif query_type == 'holidays_by_user':
                holidays = data['response']  # list of dicts
                # Short-circuit on empty list
                if not holidays:
                    user = self.extract_staff_name(query)
                    return f"No holidays found for **{user}**."
                prompt = CorePromptTemplates.show_holidays_prompt(query=query, data=holidays)
            
            # 4️⃣ Birthday celebrants by month
            elif query_type == 'birthday_celebrants_by_month':
                birthdays = data['response']  # list of {staff_name, username, birthday}
                prompt = CorePromptTemplates.show_birthdays_prompt(query, birthdays)
            
            # 5️⃣ Holiday swap date
            elif query_type == 'holiday_swap_date':
                swap = data['response']       # dict {swap_date: ...}
                prompt = CorePromptTemplates.show_swap_prompt(query, data['response'])
            
            # 6️⃣ All other queries (staff_details, task_summary, etc.)
            else:
                response_data = data['response']
                print("[DEBUG] General data:", response_data)
                prompt = CorePromptTemplates.get_response_prompt(query=query, data=str(response_data))
            
            # Invoke the LLM
            response = self.llm.invoke(prompt).content
            return response
        
        except Exception as e:
            print("Error during get_response:", e)
            return "An unexpected error occurred. Please try again later."

    
    '''
    CHAIN 
    '''
    def chain_run(self, query):
        '''Get the response for the given query'''
        query_data = {'query': query}

        # Runnables for classification and response generation
        classify_query_runnable = RunnableLambda(lambda x: self.classify_query(x))
        get_response_runnable = RunnableLambda(lambda x: self.get_response(x))

        chain = classify_query_runnable | get_response_runnable
        response = chain.invoke(query_data)
        return response
