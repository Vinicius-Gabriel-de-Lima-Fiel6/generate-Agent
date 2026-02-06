import streamlit as st
import json
from groq import Groq
from datetime import datetime
import re

# ==================== CONFIG ====================
st.set_page_config(
    page_title="AgentAI - Engenharia de Prompts Avançada",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

groq_client = Groq("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")

# ==================== SISTEMA DE ENGENHARIA DE PROMPTS ====================

class EngenhariaPrompts:
    """Sistema avançado de engenharia de prompts para criar agentes"""
    
    @staticmethod
    def analisar_prompt_usuario(prompt: str, groq_key: str) -> dict:
        """Analisa o prompt do usuário e extrai intenções"""
        
        system_prompt = """Você é um especialista em análise de prompts para automação.
        
Analise o prompt do usuário e retorne um JSON com:
{
  "intenção_principal": "qual é o objetivo principal",
  "entidades": ["lista", "de", "entidades", "mencionadas"],
  "integrações_necessárias": ["Discord", "Gmail", "Google Sheets", "APIs", etc],
  "tipo_agente": "monitoramento|processamento|sincronização|notificação|análise|customizado",
  "frequência_estimada": "webhook|5min|15min|hourly|daily|weekly",
  "complexidade": 1-10,
  "pré_requisitos": ["lista", "de", "dados", "necessários"],
  "casos_especiais": ["lista", "de", "edge cases"]
}

Retorne APENAS o JSON, sem explicações."""
        
        response = groq_client.chat.completions.create(
            model="Llama-3.3-70B-Versatile",
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            api_key=groq_key
        )
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response.choices[0].message.content)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {}
    
    @staticmethod
    def expandir_para_fluxo_detalhado(analise: dict, prompt_original: str, groq_key: str) -> dict:
        """Expande a análise em um fluxo detalhado com steps"""
        
        system_prompt = f"""Você é um especialista em design de workflows e automações.

Baseado nesta análise inicial:
{json.dumps(analise, indent=2, ensure_ascii=False)}

E neste prompt do usuário:
"{prompt_original}"

Crie um FLUXO DETALHADO com a estrutura:
{{
  "nome_agente": "Nome descritivo",
  "descricao": "Descrição completa",
  "diagrama": "ASCII art do fluxo",
  "steps": [
    {{
      "id": 1,
      "nome": "Nome do step",
      "tipo": "trigger|processamento|validação|ação|notificação",
      "descrição": "O que faz",
      "inputs": ["dados de entrada"],
      "outputs": ["dados de saída"],
      "condicionalidades": ["se X então Y"],
      "integrações": ["APIs/apps necessários"],
      "tratamento_erros": "Como lidar com falhas"
    }}
  ],
  "variáveis_necessárias": {{"chave": "descrição"}},
  "API_endpoints": ["lista de APIs a usar"],
  "webhooks_necessários": ["lista de webhooks"],
  "rate_limits": "Considerar limites de taxa",
  "retry_strategy": "Como fazer retry em falhas",
  "logging_monitoring": "Como monitorar execução"
}}

Retorne APENAS o JSON bem estruturado."""
        
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            max_tokens=3000,
            system=system_prompt,
            messages=[{"role": "user", "content": "Crie o fluxo detalhado"}],
            api_key=groq_key
        )
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response.choices[0].message.content)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {}
    
    @staticmethod
    def gerar_codigo_executavel(fluxo: dict, prompt_original: str, groq_key: str) -> dict:
        """Gera código Python executável para o agente"""
        
        system_prompt = f"""Você é um especialista em Python e automações.

Baseado neste fluxo:
{json.dumps(fluxo, indent=2, ensure_ascii=False)}

Gere CÓDIGO PYTHON COMPLETO que:
1. Implemente cada step do fluxo
2. Tenha tratamento de erros robusto
3. Use requests/bibliotecas padrão
4. Tenha logging detalhado
5. Seja facilmente customizável

Retorne um JSON com:
{{
  "arquivo_principal": "nome.py",
  "imports": ["lista", "de", "imports"],
  "classes": {{
    "NomeClasse": "código da classe..."
  }},
  "funcoes": {{
    "nome_funcao": "código da função..."
  }},
  "configuracoes": {{
    "variavel": "valor padrão"
  }},
  "exemplo_uso": "Como executar",
  "dependencias": ["pip", "install", "pacotes"],
  "documentacao": "Documentação do código"
}}

Retorne APENAS o JSON com código."""
        
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": "Gere o código"}],
            api_key=groq_key
        )
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response.choices[0].message.content)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {}
    
    @staticmethod
    def gerar_dockerfile(codigo: dict, groq_key: str) -> str:
        """Gera Dockerfile para containerizar o agente"""
        
        system_prompt = """Crie um Dockerfile otimizado que:
1. Use imagem Python slim
2. Instale dependências
3. Configure variáveis de ambiente
4. Execute o agente
5. Seja seguro e eficiente

Retorne APENAS o conteúdo do Dockerfile."""
        
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            max_tokens=1500,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Dependências: {json.dumps(codigo.get('dependencias', []))}"}
            ],
            api_key=groq_key
        )
        
        return response.choices[0].message.content
    
    @staticmethod
    def gerar_documentacao_completa(
        analise: dict, 
        fluxo: dict, 
        codigo: dict, 
        prompt_original: str,
        groq_key: str
    ) -> str:
        """Gera documentação markdown completa"""
        
        system_prompt = """Crie uma documentação COMPLETA em Markdown que inclua:
1. Visão geral
2. Arquitetura
3. Setup instructions
4. API reference
5. Exemplos de uso
6. Troubleshooting
7. Contribuindo

Retorne APENAS markdown bem formatado."""
        
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            max_tokens=4000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"""
Prompt original: {prompt_original}
Fluxo: {json.dumps(fluxo, indent=2)[:1000]}...
Código: {json.dumps(codigo, indent=2)[:1000]}..."""}
            ],
            api_key=groq_key
        )
        
        return response.choices[0].message.content

# ==================== UI ====================

st.markdown("""
# 🧠 AgentAI - Engenharia de Prompts Avançada

**Crie agentes complexos do zero com UM prompt rápido**

Powered by Groq (100% grátis) + Engenharia de Prompts Avançada
""")

st.divider()

# ==================== SIDEBAR ====================

with st.sidebar:
    st.markdown("# ⚙️ Configuração")
    
    groq_key = st.text_input(
        "🔐 Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Grátis em console.groq.com"
    )
    
    st.divider()
    
    st.markdown("""
    **Como funciona:**
    
    1. ✍️ Escreva um prompt
    2. 🧠 IA analisa e expande
    3. 📊 Gera fluxo detalhado
    4. 💻 Produz código Python
    5. 🐳 Cria Dockerfile
    6. 📖 Gera documentação
    """)

# ==================== MAIN CONTENT ====================

tabs = st.tabs([
    "🚀 Criar Agente",
    "📊 Dashboard",
    "🎓 Guia",
    "📚 Exemplos"
])

# ==================== TAB 1: CRIAR AGENTE ====================

with tabs[0]:
    st.header("Descreva seu Agente")
    
    prompt = st.text_area(
        "Seu prompt (seja rápido e direto)",
        height=150,
        placeholder="""Ex: Monitore Bitcoin a cada 5 min. Se > $50k, alerta Discord + Google Sheets.

Ou: Leia emails Gmail, extrai dados, cria tarefas Asana automaticamente.

Ou: Sincronize Shopify → Google Analytics, gerando dashboard."""
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        velocidade_rapida = st.checkbox("⚡ Modo Rápido", value=True, help="Apenas análise básica")
    
    with col2:
        incluir_codigo = st.checkbox("💻 Gerar Código", value=True)
    
    with col3:
        incluir_docker = st.checkbox("🐳 Gerar Docker", value=False)
    
    st.divider()
    
    if st.button("🚀 Gerar Agente", type="primary", use_container_width=True):
        if not prompt.strip():
            st.error("❌ Escreva um prompt!")
        elif not groq_key:
            st.error("❌ Configure Groq API Key!")
        else:
            with st.spinner("🧠 Analisando seu prompt..."):
                
                # PASSO 1: Análise Inicial
                st.info("📍 Passo 1/4: Analisando prompt...")
                analise = EngenhariaPrompts.analisar_prompt_usuario(prompt, groq_key)
                
                if not analise:
                    st.error("Erro ao analisar prompt. Tente novamente.")
                else:
                    with st.expander("📊 Análise (clique para ver)"):
                        st.json(analise)
                    
                    # PASSO 2: Expandir para Fluxo
                    st.info("📍 Passo 2/4: Gerando fluxo detalhado...")
                    fluxo = EngenhariaPrompts.expandir_para_fluxo_detalhado(
                        analise, prompt, groq_key
                    )
                    
                    if fluxo:
                        with st.expander("🔄 Fluxo Detalhado (clique para ver)"):
                            if "diagrama" in fluxo:
                                st.code(fluxo["diagrama"], language="text")
                            st.json(fluxo)
                    
                    # PASSO 3: Gerar Código (opcional)
                    codigo = {}
                    if incluir_codigo:
                        st.info("📍 Passo 3/4: Gerando código Python...")
                        codigo = EngenhariaPrompts.gerar_codigo_executavel(
                            fluxo, prompt, groq_key
                        )
                        
                        if codigo:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                with st.expander("💻 Classes"):
                                    for classe, conteudo in codigo.get("classes", {}).items():
                                        st.code(conteudo, language="python")
                            
                            with col2:
                                with st.expander("⚙️ Funções"):
                                    for func, conteudo in codigo.get("funcoes", {}).items():
                                        st.code(conteudo, language="python")
                            
                            with st.expander("📦 Dependências"):
                                st.code("\n".join(codigo.get("dependencias", [])))
                            
                            with st.expander("🚀 Exemplo de Uso"):
                                st.code(codigo.get("exemplo_uso", ""), language="python")
                    
                    # PASSO 4: Gerar Dockerfile (opcional)
                    if incluir_docker and codigo:
                        st.info("📍 Passo 4/4: Gerando Dockerfile...")
                        dockerfile = EngenhariaPrompts.gerar_dockerfile(codigo, groq_key)
                        
                        with st.expander("🐳 Dockerfile"):
                            st.code(dockerfile, language="dockerfile")
                    
                    # DOCUMENTAÇÃO
                    st.info("📍 Gerando documentação...")
                    docs = EngenhariaPrompts.gerar_documentacao_completa(
                        analise, fluxo, codigo, prompt, groq_key
                    )
                    
                    with st.expander("📖 Documentação Completa"):
                        st.markdown(docs)
                    
                    # DOWNLOAD
                    st.divider()
                    st.success("✅ Agente criado com sucesso!")
                    
                    # Exportar como JSON
                    export_data = {
                        "prompt_original": prompt,
                        "analise": analise,
                        "fluxo": fluxo,
                        "codigo": codigo,
                        "documentacao": docs,
                        "criado_em": datetime.now().isoformat()
                    }
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.download_button(
                            "📥 Download JSON",
                            json.dumps(export_data, indent=2, ensure_ascii=False),
                            "agente.json",
                            "application/json",
                            use_container_width=True
                        )
                    
                    with col2:
                        if codigo:
                            main_code = f"""#!/usr/bin/env python3
'''
{analise.get('intenção_principal', 'Agente')}
Gerado automaticamente por AgentAI
'''

import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

{json.dumps(codigo.get('classes', {}), indent=2)}

{json.dumps(codigo.get('funcoes', {}), indent=2)}

if __name__ == "__main__":
    {codigo.get('exemplo_uso', 'pass')}
"""
                            st.download_button(
                                "💻 Download Python",
                                main_code,
                                "agente.py",
                                "text/plain",
                                use_container_width=True
                            )
                    
                    with col3:
                        st.download_button(
                            "📚 Download Docs",
                            docs,
                            "README.md",
                            "text/markdown",
                            use_container_width=True
                        )

# ==================== TAB 2: DASHBOARD ====================

with tabs[1]:
    st.header("📊 Dashboard de Agentes")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Agentes Criados", "0", help="Salve agentes para rastrear")
    with col2:
        st.metric("Prompts Processados", "0")
    with col3:
        st.metric("Código Gerado", "0 linhas")
    with col4:
        st.metric("Tempo Economizado", "0 horas")
    
    st.info("💡 Salve seus agentes para ver estatísticas aqui")

# ==================== TAB 3: GUIA ====================

with tabs[2]:
    st.header("🎓 Guia de Engenharia de Prompts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Prompts Bons")
        st.markdown("""
        **Específico:**
        "Monitore Bitcoin a cada 5 min, alerta Discord se > $50k"
        
        **Com contexto:**
        "Leia emails do Gmail, extrai dados, cria tarefas no Asana"
        
        **Com integrações:**
        "Sincronize Shopify → Google Sheets, crie dashboard"
        """)
    
    with col2:
        st.subheader("❌ Prompts Ruins")
        st.markdown("""
        **Vago:**
        "Faça algo com dados"
        
        **Sem integrações:**
        "Monitore algo"
        
        **Ambíguo:**
        "Crie um agente"
        """)
    
    st.divider()
    
    st.subheader("🎯 Tipos de Agentes Suportados")
    
    tipos = {
        "🔍 Monitoramento": "Verifica mudanças continuamente",
        "⚙️ Processamento": "Transforma dados",
        "🔄 Sincronização": "Copia dados entre plataformas",
        "📢 Notificação": "Envia alertas",
        "📊 Análise": "Analisa dados e gera insights",
        "🔗 Integração": "Conecta múltiplos serviços"
    }
    
    cols = st.columns(2)
    for i, (tipo, desc) in enumerate(tipos.items()):
        with cols[i % 2]:
            st.write(f"**{tipo}** - {desc}")

# ==================== TAB 4: EXEMPLOS ====================

with tabs[3]:
    st.header("📚 Exemplos de Prompts")
    
    exemplos = [
        {
            "titulo": "Bitcoin Monitor",
            "prompt": "Monitore o preço do Bitcoin a cada 5 minutos usando CoinGecko API. Se passar de $50.000, envie alerta para Discord e salve em Google Sheets.",
            "tipo": "Monitoramento + Notificação"
        },
        {
            "titulo": "Email to Tasks",
            "prompt": "Verifique novos emails no Gmail a cada 10 minutos. Para cada email, extraia o assunto e crie uma tarefa no Asana automaticamente.",
            "tipo": "Processamento + Sincronização"
        },
        {
            "titulo": "Shopify Dashboard",
            "prompt": "Sincronize novos pedidos do Shopify a cada 30 minutos para uma planilha Google Sheets. Crie colunas para: número, cliente, valor, status, data.",
            "tipo": "Sincronização"
        },
        {
            "titulo": "Stock Tracker",
            "prompt": "Monitore ações da Bolsa (PETR4, VALE3) a cada hora. Se cair >5%, envie SMS. Se subir >5%, envie email.",
            "tipo": "Monitoramento + Análise"
        },
        {
            "titulo": "GitHub Auto-Deploy",
            "prompt": "Monitore novo push no repo GitHub. Se houver changes em 'main', rode testes, se pass, deploy automático.",
            "tipo": "Processamento"
        },
        {
            "titulo": "Sentiment Analysis",
            "prompt": "Monitore tweets com #marca a cada 5 min. Analise sentimento. Se negativo, alerta Slack urgente.",
            "tipo": "Análise + Notificação"
        }
    ]
    
    for exemplo in exemplos:
        with st.expander(f"📌 {exemplo['titulo']} ({exemplo['tipo']})"):
            st.code(exemplo['prompt'])
            if st.button(f"▶️ Usar este exemplo", key=exemplo['titulo']):
                st.session_state.prompt = exemplo['prompt']
                st.rerun()

# ==================== FOOTER ====================

st.divider()
st.markdown("""
<div style="text-align: center; color: #888; margin-top: 40px;">
    <p>🧠 AgentAI v1.0 - Engenharia de Prompts Avançada</p>
    <p>Crie agentes profissionais com UM prompt | Powered by Groq</p>
    <p><strong>100% GRÁTIS</strong> | Sem limites | Open Source</p>
</div>
""", unsafe_allow_html=True)
