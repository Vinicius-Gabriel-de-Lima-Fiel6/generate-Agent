import time
import os
from groq import Groq
from supabase import create_client

# Configurações (Use st.secrets ou variáveis de ambiente)
client = Groq(api_key="SUA_CHAVE_GROQ")
supabase = create_client("URL_SUPABASE", "KEY_SUPABASE")

def executar_agente_ia(agente):
    print(f"🤖 IA processando agente: {agente['name']}")
    
    # Prompt de Sistema (Invisível ao usuário) que define o comportamento
    system_prompt = f"""
    Você é um agente autônomo da empresa {agente['company_id']}.
    Sua tarefa é seguir a configuração do usuário: {agente['prompt_config']}
    Responda de forma executiva e direta. Se precisar simular uma ação, descreva-a.
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.5,
            max_tokens=1024
        )
        
        resposta = completion.choices[0].message.content
        
        # Salva o resultado no banco para o usuário ver no Streamlit
        supabase.table("agents").update({
            "last_result": resposta,
            "last_run": "now()"
        }).eq("id", agente['id']).execute()
        
    except Exception as e:
        print(f"Erro na Groq: {e}")

def loop_principal():
    while True:
        # Busca agentes ativos que não rodaram nos últimos 10 minutos (exemplo)
        agentes = supabase.table("agents").select("*").eq("status", "active").execute().data
        
        for ag in agentes:
            executar_agente_ia(ag)
            
        time.sleep(60) # Intervalo entre ciclos

if __name__ == "__main__":
    loop_principal()
