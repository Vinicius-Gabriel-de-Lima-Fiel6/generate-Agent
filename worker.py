import time
from groq import Groq
from supabase import create_client
import datetime

# Setup
# Substitua pelas suas chaves ou use variáveis de ambiente
GROQ_API_KEY = "SUA_CHAVE_GROQ"
SUPABASE_URL = "SUA_URL"
SUPABASE_KEY = "SUA_KEY"

groq_client = Groq(api_key=GROQ_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def rodar_motor():
    print("🚀 Motor de IA Iniciado. Monitorando agentes ativos...")
    
    while True:
        try:
            # 1. Busca agentes ativos que ainda não têm resultado ou precisam de atualização
            res = supabase.table("agents").select("*").eq("status", "active").execute()
            agentes = res.data

            for ag in agentes:
                # Evita re-processar se já rodou recentemente (ex: nos últimos 5 min)
                # Para o teste ser "funcional de fato", vamos rodar se o result estiver vazio
                if not ag['last_result']:
                    print(f"⚙️ Processando: {ag['name']}")
                    
                    prompt_sistema = "Você é um consultor B2B sênior. Responda de forma prática e acionável."
                    
                    completion = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": prompt_sistema},
                            {"role": "user", "content": ag['prompt_config']}
                        ],
                        temperature=0.7,
                    )
                    
                    resultado = completion.choices[0].message.content
                    
                    # 2. Devolve o resultado pro Supabase
                    supabase.table("agents").update({
                        "last_result": resultado,
                        "last_run": datetime.datetime.now().isoformat()
                    }).eq("id", ag['id']).execute()
                    
                    print(f"✅ Agente {ag['name']} atualizado.")

            time.sleep(10) # Checa o banco a cada 10 segundos
            
        except Exception as e:
            print(f"❌ Erro no loop: {e}")
            time.sleep(20)

if __name__ == "__main__":
    rodar_motor()
