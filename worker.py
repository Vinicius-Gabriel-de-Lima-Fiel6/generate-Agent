import time
import datetime
from groq import Groq
from supabase import create_client

# Configuração
client = Groq(api_key="SUA_CHAVE_GROQ")
supabase = create_client("URL_SUPABASE", "KEY_SUPABASE")

def calcular_proxima_data(frequencia):
    agora = datetime.datetime.now()
    if frequencia == 'diario':
        return agora + datetime.timedelta(days=1)
    if frequencia == 'mensal':
        return agora + datetime.timedelta(days=30)
    if frequencia == 'anual':
        return agora + datetime.timedelta(days=365)
    return None

def processar_agentes():
    agora = datetime.datetime.now().isoformat()
    
    # Busca agentes ativos que já passaram da hora de rodar (next_run <= agora)
    # ou que nunca rodaram (next_run is null)
    res = supabase.table("agents").select("*")\
        .eq("status", "active")\
        .or_(f"next_run.lte.{agora},next_run.is.null")\
        .execute()
    
    for ag in res.data:
        print(f"🤖 Executando agente recorrente: {ag['name']}")
        
        # 1. IA Processa a tarefa
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Você é um assistente de automação corporativa."},
                {"role": "user", "content": f"Tarefa: {ag['prompt_config']}"}
            ]
        )
        resultado = completion.choices[0].message.content
        
        # 2. Calcula próxima execução
        proxima = calcular_proxima_data(ag.get('frequency', 'diario'))
        
        # 3. Atualiza o banco
        supabase.table("agents").update({
            "last_result": resultado,
            "last_run": agora,
            "next_run": proxima.isoformat() if proxima else None
        }).eq("id", ag['id']).execute()
        
        print(f"✅ Tarefa concluída. Próxima execução: {proxima}")

if __name__ == "__main__":
    while True:
        processar_agentes()
        time.sleep(60) # Checa a cada minuto
