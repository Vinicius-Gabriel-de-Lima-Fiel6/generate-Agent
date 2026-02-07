import os
from groq import Groq
import google.generativeai as genai

def get_llm_response(agent_config, history):
    provider = agent_config['provider']
    
    if provider == 'groq':
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        # Formata o prompt do sistema + histórico
        messages = [{"role": "system", "content": agent_config['system_prompt']}] + history
        
        completion = client.chat.completions.create(
            model=agent_config['model_name'],
            messages=messages,
            temperature=agent_config['temperature'],
            stream=True
        )
        return completion

    elif provider == 'gemini':
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel(agent_config['model_name'])
        # Gemini usa um formato de chat diferente, simplificando:
        chat = model.start_chat(history=[])
        return chat.send_message(history[-1]['content'], stream=True)
