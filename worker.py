import time
import datetime
from supabase import create_client

# Configuração (Use variáveis de ambiente)
supabase = create_client("SUA_URL", "SUA_KEY")

def logica_do_agente(agente):
    """
    Aqui é onde a mágica acontece. 
    Como você não quer IA agora, aqui você usa regras de código:
    Se template == 'Monitor', faça X.
    Se template == 'Relatório', faça Y.
    """
    print(f"[{datetime.datetime.now()}] Processando Agente: {agente['name']}")
    
    # Exemplo de lógica baseada no prompt (Parser Simples)
    if "email" in agente['prompt_config'].lower():
        print(f"-> Simulando envio de e-mail conforme prompt: {agente['prompt_config']}")
    
    # Atualiza o timestamp de última execução
    supabase.table("agents").update({
        "last_run": datetime.datetime.now().isoformat()
    }).eq("id", agente['id']).execute()

def iniciar_motor():
    print("🚀 Motor de Agentes Python Iniciado (Sem n8n)...")
    while True:
        try:
            # Busca agentes que estão ativos
            res = supabase.table("agents").select("*").eq("status", "active").execute()
            agentes = res.data

            for ag in agentes:
                logica_do_agente(ag)
            
            # Frequência de verificação (ex: a cada 30 segundos)
            time.sleep(30)
            
        except Exception as e:
            print(f"❌ Erro no motor: {e}")
            time.sleep(10)

if __name__ == "__main__":
    iniciar_motor()
