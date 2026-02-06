import streamlit as st
import requests
import json
import time
from datetime import datetime
from anthropic import Anthropic
import re

# Configuração da página
st.set_page_config(
    page_title="Agent Factory",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa cliente Claude
client = Anthropic()

# CSS customizado
st.markdown("""
    <style>
    .agent-card {
        padding: 15px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
        border-left: 5px solid #1f77b4;
    }
    .success-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .error-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== CARREGAR SECRETS ====================
# Tenta carregar do Streamlit Secrets (Cloud) ou entrada manual (Development)
try:
    claude_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    n8n_url = st.secrets.get("N8N_URL", "")
    n8n_api_key = st.secrets.get("N8N_API_KEY", "")
    modo_cloud = True
except:
    claude_key = ""
    n8n_url = ""
    n8n_api_key = ""
    modo_cloud = False

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("# ⚙️ Configurações")
    st.divider()
    
    if modo_cloud:
        st.success("✅ Usando Streamlit Secrets")
        if st.button("🔄 Recarregar Secrets", use_container_width=True):
            st.rerun()
    else:
        st.info("💻 Modo Development - Configure suas chaves")
    
    # Configuração do n8n
    st.subheader("N8N")
    n8n_url = st.text_input(
        "🔗 URL do n8n",
        value=n8n_url or "https://seu-n8n.com",
        placeholder="https://seu-n8n.com",
        help="URL base do seu servidor n8n"
    )
    
    n8n_api_key = st.text_input(
        "🔑 API Key do n8n",
        type="password",
        value=n8n_api_key or "",
        placeholder="Sua API key aqui",
        help="Obtenha em Settings > API > Generate API Key"
    )
    
    st.divider()
    
    # Configuração do Claude
    st.subheader("Claude API")
    claude_key = st.text_input(
        "🔐 Claude API Key",
        type="password",
        value=claude_key or "",
        placeholder="sk-ant-...",
        help="Obtenha em console.anthropic.com"
    )
    
    st.divider()
    
    # Informações úteis
    st.subheader("ℹ️ Informações")
    st.markdown("""
    **Como começar:**
    1. Configure suas chaves de API
    2. Descreva o agente que quer criar
    3. IA gera a estrutura
    4. Crie no n8n com um clique
    
    **Exemplos de agentes:**
    - Monitorar preços de criptos
    - Responder emails automaticamente
    - Sincronizar planilhas
    - Postar em redes sociais
    - Enviar alertas por Telegram
    """)

# ==================== INICIALIZAR SESSION STATE ====================
if "agentes" not in st.session_state:
    st.session_state.agentes = []

if "workflow_gerado" not in st.session_state:
    st.session_state.workflow_gerado = None

if "prompt_atual" not in st.session_state:
    st.session_state.prompt_atual = ""

# ==================== HEADER ====================
st.markdown("""
# 🤖 Agent Factory
**Crie agentes IA em segundos, sem programação**

Descreva o que você quer que um agente faça e deixe a IA criar automaticamente um workflow completo no n8n.
""")

st.divider()

# ==================== MAIN CONTENT ====================
tab1, tab2, tab3 = st.tabs(["🚀 Criar Agente", "📊 Meus Agentes", "📖 Guia"])

# ==================== TAB 1: CRIAR AGENTE ====================
with tab1:
    st.header("Descreva seu Agente")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        prompt_usuario = st.text_area(
            "📝 O que você quer que o agente faça?",
            value=st.session_state.prompt_atual,
            placeholder="""Ex: Monitore o preço do Bitcoin a cada 5 minutos e mande um alerta no Discord quando passar de $50k

Ou: Verifique novos emails e responda automaticamente com um template padrão

Ou: Sincronize dados do Shopify com uma planilha Google Sheets""",
            height=150,
            key="prompt_input"
        )
    
    with col2:
        st.markdown("""
        **💡 Dicas:**
        - Seja específico
        - Mencione fontes de dados
        - Inclua ações desejadas
        - Defina frequência
        """)
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        gerar_btn = st.button(
            "🚀 Gerar Agente",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        st.button(
            "🔄 Limpar",
            use_container_width=True,
            key="limpar_btn"
        )
    
    with col3:
        st.info("Etapa 1/2")
    
    # ==================== GERAÇÃO DA IA ====================
    if gerar_btn:
        if not prompt_usuario.strip():
            st.error("❌ Por favor, descreva o agente que quer criar!")
        elif not claude_key:
            st.error("❌ Configure a Claude API Key na sidebar!")
        elif not n8n_url or n8n_url == "https://seu-n8n.com":
            st.error("❌ Configure a URL do n8n na sidebar!")
        else:
            st.session_state.prompt_atual = prompt_usuario
            
            with st.spinner("🧠 IA gerando estrutura do agente..."):
                try:
                    # System prompt para gerar workflow
                    system_prompt = """Você é um expert em n8n (automação workflow).
Um usuário descreveu um agente que precisa ser criado.
Sua tarefa é gerar um JSON válido com a estrutura de workflow do n8n.

IMPORTANTE:
- Gere nós realistas que existem no n8n
- Use os tipos de nó corretos (n8n-nodes-base.*)
- Conecte os nós de forma lógica
- Inclua triggers (Schedule, Webhook, etc)
- Adicione ações (HTTP, Discord, Telegram, Google Sheets, etc)

Formato do JSON:
{
  "name": "Nome descritivo do agente",
  "active": true,
  "nodes": [
    {
      "name": "Nome do nó",
      "type": "n8n-nodes-base.tipoDono",
      "typeVersion": 1,
      "position": [x, y],
      "parameters": { ... configurações ... }
    }
  ],
  "connections": {
    "nó-origem": ["nó-destino"],
    "outro-nó": ["próximo-nó"]
  }
}

Retorne APENAS o JSON válido, sem markdown, sem explicações."""

                    response = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=3000,
                        system=system_prompt,
                        messages=[
                            {"role": "user", "content": f"Crie um agente para: {prompt_usuario}"}
                        ],
                        api_key=claude_key
                    )
                    
                    workflow_text = response.content[0].text
                    
                    # Extrai JSON da resposta
                    json_match = re.search(r'\{[\s\S]*\}', workflow_text)
                    if json_match:
                        workflow_json = json_match.group()
                    else:
                        workflow_json = workflow_text
                    
                    workflow_data = json.loads(workflow_json)
                    st.session_state.workflow_gerado = workflow_data
                    
                    st.success("✅ Workflow gerado com sucesso!")
                    
                except json.JSONDecodeError as e:
                    st.error(f"❌ Erro ao processar JSON: {str(e)}")
                    with st.expander("Ver resposta bruta"):
                        st.code(workflow_text)
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
    
    # ==================== EXIBIÇÃO DO WORKFLOW ====================
    if st.session_state.workflow_gerado:
        st.divider()
        st.subheader("📋 Estrutura do Agente Gerada")
        
        workflow = st.session_state.workflow_gerado
        
        # Resumo do workflow
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nós", len(workflow.get("nodes", [])))
        with col2:
            connections = workflow.get("connections", {})
            total_conexoes = sum(len(v) for v in connections.values())
            st.metric("Conexões", total_conexoes)
        with col3:
            st.metric("Status", "✅ Ativo" if workflow.get("active") else "⏸️ Inativo")
        
        # Exibe JSON com abas
        tab_json, tab_nodes, tab_preview = st.tabs(["📄 JSON Completo", "🔗 Nós", "👁️ Preview"])
        
        with tab_json:
            st.json(workflow)
        
        with tab_nodes:
            for node in workflow.get("nodes", []):
                with st.expander(f"🔧 {node.get('name', 'Sem nome')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Tipo:** {node.get('type', 'N/A')}")
                        st.write(f"**Versão:** {node.get('typeVersion', 1)}")
                    with col2:
                        pos = node.get('position', [0, 0])
                        st.write(f"**Posição:** X={pos[0]}, Y={pos[1]}")
                    st.write("**Parâmetros:**")
                    st.json(node.get('parameters', {}))
        
        with tab_preview:
            st.info("Preview visual do workflow (representação simplificada)")
            preview_text = f"""
            **Nome do Agente:** {workflow.get('name', 'Sem nome')}
            
            **Fluxo:**
            """
            
            connections = workflow.get("connections", {})
            for origem, destinos in connections.items():
                for destino in destinos:
                    preview_text += f"\n{origem} → {destino}"
            
            st.markdown(preview_text)
        
        st.divider()
        
        # ==================== BOTÃO CRIAR NO N8N ====================
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            criar_btn = st.button(
                "✨ Criar no N8N",
                use_container_width=True,
                type="primary",
                key="criar_n8n"
            )
        
        with col2:
            st.button(
                "🗑️ Descartar",
                use_container_width=True,
                key="descartar_btn"
            )
        
        with col3:
            st.info("Etapa 2/2")
        
        if criar_btn:
            if not n8n_api_key:
                st.error("❌ Configure a API Key do n8n na sidebar!")
            else:
                with st.spinner("📤 Criando agente no n8n..."):
                    try:
                        headers = {
                            "X-N8N-API-KEY": n8n_api_key,
                            "Content-Type": "application/json"
                        }
                        
                        # Cria o workflow
                        response = requests.post(
                            f"{n8n_url.rstrip('/')}/api/v1/workflows",
                            json=workflow,
                            headers=headers,
                            timeout=30
                        )
                        
                        if response.status_code == 201:
                            agente_info = response.json()
                            agente_id = agente_info.get("id")
                            
                            # Ativa o workflow
                            activate_response = requests.patch(
                                f"{n8n_url.rstrip('/')}/api/v1/workflows/{agente_id}",
                                json={"active": True},
                                headers=headers,
                                timeout=30
                            )
                            
                            if activate_response.status_code == 200:
                                # Salva no histórico
                                novo_agente = {
                                    "id": agente_id,
                                    "nome": workflow.get("name", "Agente sem nome"),
                                    "prompt": prompt_usuario,
                                    "status": "✅ Rodando",
                                    "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                    "workflow": workflow,
                                    "n8n_url": f"{n8n_url.rstrip('/')}/workflow/{agente_id}"
                                }
                                
                                st.session_state.agentes.insert(0, novo_agente)
                                
                                st.success("🎉 Agente criado e ativado com sucesso!")
                                st.markdown(f"""
                                ✅ **Agente {novo_agente['nome']} está rodando!**
                                
                                [🔗 Abrir no n8n]({novo_agente['n8n_url']})
                                """)
                                st.balloons()
                                
                                # Limpa o workflow gerado
                                st.session_state.workflow_gerado = None
                                st.session_state.prompt_atual = ""
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"❌ Erro ao ativar: {activate_response.text}")
                        else:
                            st.error(f"❌ Erro ao criar: {response.text}")
                    
                    except requests.exceptions.Timeout:
                        st.error("❌ Timeout: N8n levou muito tempo para responder")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Erro de conexão: Verifique a URL do n8n")
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")

# ==================== TAB 2: MEUS AGENTES ====================
with tab2:
    st.header("Seus Agentes Criados")
    
    if st.session_state.agentes:
        # Filtro
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Atualizar", use_container_width=True):
                st.rerun()
        
        # Lista de agentes
        for idx, agente in enumerate(st.session_state.agentes):
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.markdown(f"### {agente['nome']}")
                    st.caption(f"Criado em: {agente['criado_em']}")
                
                with col2:
                    st.markdown(f"**Status:** {agente['status']}")
                    st.caption(f"ID: {agente['id'][:8]}...")
                
                with col3:
                    if st.button("👁️ Ver", key=f"ver_{idx}", use_container_width=True):
                        st.session_state[f"expand_{idx}"] = not st.session_state.get(f"expand_{idx}", False)
                
                with col4:
                    if st.button("🔗 Abrir", key=f"abrir_{idx}", use_container_width=True):
                        st.markdown(f"[Clique aqui]({agente['n8n_url']})")
                
                # Expandir detalhes
                if st.session_state.get(f"expand_{idx}", False):
                    st.divider()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Prompt Original")
                        st.write(agente['prompt'])
                    
                    with col2:
                        st.subheader("Estatísticas")
                        workflow = agente['workflow']
                        st.metric("Nós", len(workflow.get('nodes', [])))
                        connections = workflow.get('connections', {})
                        total_conexoes = sum(len(v) for v in connections.values())
                        st.metric("Conexões", total_conexoes)
                    
                    st.subheader("Estrutura JSON")
                    with st.expander("Ver JSON completo"):
                        st.json(agente['workflow'])
                    
                    st.divider()
    else:
        st.info("Você ainda não criou nenhum agente. Vá para a aba 'Criar Agente' para começar!")

# ==================== TAB 3: GUIA ====================
with tab3:
    st.header("📖 Guia de Uso")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Como Começar")
        st.markdown("""
        1. **Configure as chaves de API** na sidebar
        2. **Descreva seu agente** na aba "Criar Agente"
        3. **Clique em "Gerar Agente"** para IA criar a estrutura
        4. **Revise o workflow** gerado
        5. **Clique em "Criar no N8N"** para ativar
        
        ✅ Seu agente está rodando!
        """)
    
    with col2:
        st.subheader("Exemplos de Agentes")
        st.markdown("""
        **Monitoramento:**
        - Verificar preços de criptomoedas
        - Monitorar status de sites
        - Alertar sobre mudanças em preços
        
        **Automação:**
        - Responder emails automaticamente
        - Postar em redes sociais em horários
        - Sincronizar dados entre plataformas
        
        **Processamento:**
        - Processar PDFs e extrair dados
        - Gerar relatórios automáticos
        - Converter formatos de arquivo
        """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Nós Disponíveis")
        st.markdown("""
        **Triggers (Iniciam o workflow):**
        - Schedule (tempo/horário)
        - Webhook (chamadas HTTP)
        - Cron (agendamentos complexos)
        
        **Integrações:**
        - Discord, Telegram, Slack
        - Google Sheets, Gmail
        - Shopify, WooCommerce
        - APIs genéricas (HTTP)
        
        **Processamento:**
        - If/Else (condições)
        - Function (código customizado)
        - Set (definir dados)
        """)
    
    with col2:
        st.subheader("💡 Dicas")
        st.markdown("""
        ✅ **Faça prompts específicos:**
        - Inclua frequência (cada 5 min, diariamente)
        - Mencione ações esperadas
        - Descreva condições (se preço > $50k)
        
        ✅ **Estruture bem:**
        - Trigger → Processamento → Ação
        - Uma tarefa por agente
        - Use nomes descritivos
        
        ✅ **Teste antes:**
        - Verifique credenciais
        - Teste com dados reais
        - Monitore primeira execução
        """)
    
    st.divider()
    
    st.subheader("❓ Dúvidas Frequentes")
    
    with st.expander("Como obtenho as chaves de API?"):
        st.markdown("""
        **Claude API Key:**
        1. Vá para https://console.anthropic.com
        2. Faça login/criar conta
        3. Vá em API Keys
        4. Clique em "Create Key"
        
        **N8N API Key:**
        1. Acesse seu n8n
        2. Vá em Settings (engrenagem)
        3. Clique em "API"
        4. Clique em "Generate API Key"
        """)
    
    with st.expander("Posso editar agentes após criação?"):
        st.markdown("""
        Sim! Depois que o agente é criado, você pode:
        1. Abrir no n8n pelo link
        2. Editar nós e conexões
        3. Adicionar/remover nós
        4. Salvar e ativar novamente
        """)
    
    with st.expander("Quanto custa?"):
        st.markdown("""
        - **Claude API:** Pago por uso (tokens)
        - **N8N:** Dependente da hospedagem
        - **Streamlit Cloud:** Gratuito
        
        Consulte as tabelas de preço oficiais.
        """)

# ==================== FOOTER ====================
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; margin-top: 40px;">
    <p>🤖 Agent Factory v1.0 | Powered by Claude + N8N</p>
    <p>Crie agentes incríveis sem escrever uma linha de código</p>
</div>
""", unsafe_allow_html=True)
