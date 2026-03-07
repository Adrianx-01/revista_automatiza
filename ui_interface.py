"""
Módulo de Interface do Usuário (UI)
Contém toda a lógica de apresentação e interação com o usuário
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from io import BytesIO
from processador_inpi import ProcessadorINPI
from database_supabase import DatabaseSupabase
from gerenciador_revistas import GerenciadorRevistas


def aplicar_estilos_customizados():
    """Aplica estilos CSS customizados"""
    st.markdown("""
    <style>
    /* Sidebar branco */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
    }
    
    /* Fundo das páginas PRETO */
    .stApp, section[data-testid="stMain"], .main .block-container, 
    .main .element-container, .main div, .main section {
        background-color: #000000 !important;
    }
    
    /* TODOS OS TEXTOS EM BRANCO */
    .main *, section[data-testid="stMain"] * {
        color: #FFFFFF !important;
    }
    
    /* Inputs com fundo escuro e texto branco */
    .main input, .main textarea, .main select {
        background-color: #1a1a1a !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
    }
    
    /* Dataframes com fundo escuro */
    .main table, .main .stDataFrame, .main .stDataFrame *,
    .main [data-testid="stDataFrame"], .main [data-testid="stDataFrame"] * {
        background-color: #1a1a1a !important;
        color: #FFFFFF !important;
    }
    
    /* Sidebar texto preto */
    [data-testid="stSidebar"] * {
        color: #1f1f1f !important;
    }
    
    /* Botões de navegação na sidebar - PRIMARY (ativo) - AZUL */
    [data-testid="stSidebar"] button[kind="primary"],
    [data-testid="stSidebar"] button[data-baseweb="button"][kind="primary"],
    [data-testid="stSidebar"] button.stButton[kind="primary"],
    [data-testid="stSidebar"] .stButton button[kind="primary"] {
        background-color: #0066cc !important;
        color: #FFFFFF !important;
        border: 2px solid #0066cc !important;
    }
    
    /* Botões de navegação na sidebar - SECONDARY (inativo) - PRETO/CINZA */
    [data-testid="stSidebar"] button[kind="secondary"],
    [data-testid="stSidebar"] button[data-baseweb="button"][kind="secondary"],
    [data-testid="stSidebar"] button.stButton[kind="secondary"],
    [data-testid="stSidebar"] .stButton button[kind="secondary"] {
        background-color: #1f1f1f !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
    }
    
    /* Garantir que botões da sidebar não herdem estilos da área principal */
    [data-testid="stSidebar"] button {
        background-color: inherit !important;
    }
    
    /* Override para garantir que botões secondary não fiquem azuis */
    [data-testid="stSidebar"] button[kind="secondary"] * {
        color: #FFFFFF !important;
    }
    
    /* Botões azuis com texto branco - APENAS na área principal (depois das regras da sidebar) */
    /* NÃO afetar botões do header */
    section[data-testid="stMain"] button:not([data-testid*="baseButton-header"]),
    section[data-testid="stMain"] button:not([data-testid*="baseButton-header"]) *,
    .main button:not([data-testid*="baseButton-header"]),
    .main button:not([data-testid*="baseButton-header"]) * {
        background-color: #0066cc !important;
        color: #FFFFFF !important;
    }
    
    /* Garantir que o botão do header (toggle sidebar) não seja afetado */
    [data-testid="stHeader"] button,
    [data-testid="stHeader"] button *,
    button[data-testid*="baseButton-header"],
    button[data-testid*="baseButton-header"] * {
        background-color: transparent !important;
        color: inherit !important;
    }
    </style>
    """, unsafe_allow_html=True)


def inicializar_session_state():
    """Inicializa variáveis do session state"""
    if 'dados_processados' not in st.session_state:
        st.session_state.dados_processados = None
    if 'df_processos' not in st.session_state:
        st.session_state.df_processos = None
    if 'numero_revista' not in st.session_state:
        st.session_state.numero_revista = None
    if 'consultar_supabase' not in st.session_state:
        st.session_state.consultar_supabase = False
    if 'pagina_ativa' not in st.session_state:
        st.session_state.pagina_ativa = "gerenciar"
    if 'palavras_chave_personalizadas' not in st.session_state:
        st.session_state.palavras_chave_personalizadas = []


def renderizar_navegacao():
    """Renderiza a navegação na sidebar"""
    with st.sidebar:
        # Logo no header
        try:
            st.image("revist.png", use_container_width=True)
        except:
            st.title("📋 Sistema INPI")
        
        st.markdown("---")
        
        st.markdown("**Navegação**")
        
        if st.button("📚 Gerenciar Revistas", use_container_width=True, 
                    type="primary" if st.session_state.pagina_ativa == "gerenciar" else "secondary",
                    key="btn_gerenciar"):
            st.session_state.pagina_ativa = "gerenciar"
            st.rerun()
        
        if st.button("🔍 Consultar Dados", use_container_width=True,
                    type="primary" if st.session_state.pagina_ativa == "consultar" else "secondary",
                    key="btn_consultar"):
            st.session_state.pagina_ativa = "consultar"
            st.rerun()


def renderizar_pagina_login(db):
    """Renderiza a página de login"""
    # Aplicar estilos customizados apenas para a página de login (fundo branco)
    st.markdown("""
    <style>
    /* Fundo branco para a página de login */
    .stApp, section[data-testid="stMain"], .main .block-container, 
    .main .element-container, .main div, .main section {
        background-color: #FFFFFF !important;
    }
    
    /* Textos em preto na página de login */
    .main *, section[data-testid="stMain"] * {
        color: #1f1f1f !important;
    }
    
    /* Inputs com borda azul e texto azul - seletores mais específicos */
    .main input[type="text"],
    .main input[type="password"],
    .main input[type="email"],
    .main textarea,
    .main select,
    section[data-testid="stMain"] input[type="text"],
    section[data-testid="stMain"] input[type="password"],
    section[data-testid="stMain"] input[type="email"],
    input[data-baseweb="input"],
    input[data-baseweb="input"] input {
        background-color: #FFFFFF !important;
        color: #0066cc !important;
        border: 2px solid #0066cc !important;
        border-radius: 4px !important;
    }
    
    /* Labels dos inputs em azul - seletores mais específicos */
    .main label,
    section[data-testid="stMain"] label,
    label[data-baseweb="label"],
    .stTextInput label,
    .stTextInput > div > label {
        color: #0066cc !important;
    }
    
    /* Botões azuis - seletores mais específicos */
    .main button,
    .main button *,
    section[data-testid="stMain"] button,
    button[data-baseweb="button"],
    button[data-baseweb="button"] *,
    .stButton > button,
    .stButton > button * {
        background-color: #0066cc !important;
        color: #FFFFFF !important;
        border: 2px solid #0066cc !important;
        border-radius: 4px !important;
    }
    
    /* Hover do botão */
    .main button:hover,
    section[data-testid="stMain"] button:hover,
    button[data-baseweb="button"]:hover {
        background-color: #0052a3 !important;
        border-color: #0052a3 !important;
    }
    
    /* Placeholder dos inputs em azul claro */
    .main input::placeholder,
    section[data-testid="stMain"] input::placeholder {
        color: #66a3ff !important;
        opacity: 0.7 !important;
    }
    
    /* Foco nos inputs - manter azul */
    .main input:focus,
    section[data-testid="stMain"] input:focus,
    input[data-baseweb="input"]:focus {
        border-color: #0066cc !important;
        box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Centralizar o formulário de login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Logo no lugar do título - tamanho reduzido
        try:
            # Usar width para controlar o tamanho da logo
            st.image("revist.png", width=200)
        except:
            st.title("Login")
        
        st.markdown("---")
        
        if db is None:
            st.error("⚠️ Supabase não configurado. Configure SUPABASE_URL e SUPABASE_KEY no arquivo .env")
            return
        
        # Verificar se já está autenticado
        if db.verificar_sessao():
            usuario = db.obter_usuario_atual()
            if usuario:
                st.success(f"✅ Você já está autenticado como: {usuario.get('email', 'Usuário')}")
                if st.button("🔄 Continuar", use_container_width=True, type="primary"):
                    st.session_state.autenticado = True
                    st.rerun()
            return
        
        # Formulário de login
        with st.form("form_login"):
            # Usar st.markdown para aplicar estilos inline nos labels e remover botão de visibilidade da senha
            st.markdown("""
            <style>
            div[data-testid="stTextInput"] label,
            div[data-testid="stTextInput"] > div > label {
                color: #0066cc !important;
            }
            /* Inputs com fundo branco, borda azul e texto azul - TODOS os inputs */
            div[data-testid="stTextInput"] input,
            div[data-testid="stTextInput"] input[type="text"],
            div[data-testid="stTextInput"] input[type="password"],
            input[type="text"],
            input[type="password"],
            input[data-baseweb="input"] {
                background-color: #FFFFFF !important;
                border: 2px solid #0066cc !important;
                color: #0066cc !important;
            }
            /* Garantir que o input de senha especificamente tenha fundo branco */
            div[data-testid="stTextInput"]:has(input[type="password"]) input,
            div[data-testid="stTextInput"]:has(input[type="password"]) input[type="password"] {
                background-color: #FFFFFF !important;
                border: 2px solid #0066cc !important;
                color: #0066cc !important;
            }
            /* Remover apenas o botão de mostrar/ocultar senha - mais específico */
            div[data-testid="stTextInput"] button[data-baseweb="button"],
            div[data-testid="stTextInput"] button[title*="Show"],
            div[data-testid="stTextInput"] button[title*="Hide"],
            div[data-testid="stTextInput"] button[aria-label*="password"],
            div[data-testid="stTextInput"] > div > div:last-child button,
            div[data-testid="stTextInput"] > div > div > div:last-child button {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                width: 0 !important;
                height: 0 !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            /* Remover o container do botão, mas NÃO afetar o input */
            div[data-testid="stTextInput"] > div > div:last-child:has(button):not(:has(input)),
            div[data-testid="stTextInput"] > div > div > div:last-child:has(button):not(:has(input)) {
                display: none !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            email = st.text_input("📧 Email", placeholder="seu@email.com", key="input_email")
            senha = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha", key="input_senha")
            
            submit = st.form_submit_button("Entrar", use_container_width=True, type="primary")
            
            if submit:
                if not email or not senha:
                    st.error("⚠️ Por favor, preencha email e senha")
                else:
                    with st.spinner("Autenticando..."):
                        resultado = db.fazer_login(email, senha)
                        
                        if resultado['sucesso']:
                            st.session_state.autenticado = True
                            st.session_state.usuario = resultado.get('usuario', {})
                            st.success(f"✅ Login realizado com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"❌ {resultado.get('erro', 'Erro ao fazer login')}")


def renderizar_aplicacao(processador: ProcessadorINPI, db, init_supabase):
    """Função principal que renderiza toda a aplicação"""
    # Inicializar session state
    inicializar_session_state()
    
    # Verificar autenticação
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    
    # Se não estiver autenticado, mostrar página de login
    if not st.session_state.autenticado:
        if db is not None:
            # Verificar se há sessão ativa no Supabase
            if db.verificar_sessao():
                usuario = db.obter_usuario_atual()
                if usuario:
                    st.session_state.autenticado = True
                    st.session_state.usuario = usuario
                else:
                    renderizar_pagina_login(db)
                    return
            else:
                renderizar_pagina_login(db)
                return
        else:
            renderizar_pagina_login(db)
            return
    
    # Aplicar estilos customizados
    aplicar_estilos_customizados()
    
    # Renderizar navegação
    renderizar_navegacao()
    
    # Sidebar sem informações do usuário
    
    # Título principal
    st.title("📋 Sistema de Processos Concedidos da Revista INPI")
    st.markdown("---")
    
    # Renderizar página selecionada
    if st.session_state.pagina_ativa == "gerenciar":
        renderizar_aba_gerenciar_revistas(processador, db, init_supabase)
    else:
        renderizar_aba_consultar_dados(processador, db, init_supabase)


def definir_tipo_arquivo(arquivo):
    """Define o tipo do arquivo e retorna a extensão"""
    extensao = Path(arquivo.name).suffix.lower()
    return extensao


def renderizar_aba_gerenciar_revistas(processador: ProcessadorINPI, db, init_supabase):
    """Renderiza a aba de Gerenciar Revistas"""
    st.header("📚 Gerenciamento de Revistas")
    st.markdown("Upload, download e processamento de revistas do INPI no storage do Supabase")
    st.markdown("---")
    
    # Inicializar session state para filtros
    if 'classes_desejadas' not in st.session_state:
        st.session_state.classes_desejadas = processador.CLASSES_PADRAO.copy()
    if 'palavras_chave' not in st.session_state:
        st.session_state.palavras_chave = processador.PALAVRAS_CHAVE_PADRAO.copy()
    
    if db is None:
        st.error("⚠️ Supabase não configurado. Configure SUPABASE_URL e SUPABASE_KEY no arquivo .env")
        if st.button("🔄 Tentar Reconectar", key="reconnect_supabase"):
            init_supabase.clear()
            st.session_state.reconnect_attempted = True
            st.rerun()
    else:
        # Seção de Filtros
        st.subheader("🎯 Filtros de Importação")
        st.markdown("Configure as classes e palavras-chave que serão aplicadas ao processar as revistas")
        
        # Gerar opções de classes (1-45 como strings)
        opcoes_classes = [str(i) for i in range(1, 46)]
        
        # Garantir que os valores padrão estão nas opções (normalizar zeros à esquerda)
        classes_padrao_normalizadas = []
        for c in st.session_state.classes_desejadas:
            # Converter "03" para "3", "08" para "8", etc.
            c_normalizada = str(int(c)) if c.isdigit() else c
            if c_normalizada in opcoes_classes:
                classes_padrao_normalizadas.append(c_normalizada)
        
        # Se não encontrou nenhuma, usar o padrão do processador
        if not classes_padrao_normalizadas:
            classes_padrao_normalizadas = processador.CLASSES_PADRAO.copy()
        
        # Campo para selecionar classes
        classes_selecionadas = st.multiselect(
            "📋 Classes Desejadas:",
            options=opcoes_classes,
            default=classes_padrao_normalizadas,
            help="Selecione as classes Nice que deseja importar"
        )
        st.session_state.classes_desejadas = classes_selecionadas if classes_selecionadas else processador.CLASSES_PADRAO.copy()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Campo para palavras-chave - multiselect similar ao de classes
        # Obter todas as palavras-chave disponíveis (padrão + personalizadas)
        todas_palavras = list(set(processador.PALAVRAS_CHAVE_PADRAO + st.session_state.palavras_chave_personalizadas))
        todas_palavras = sorted([p for p in todas_palavras if p])  # Remover vazias e ordenar
        
        # Determinar palavras padrão selecionadas
        palavras_padrao_selecionadas = []
        for p in st.session_state.palavras_chave:
            if p in todas_palavras:
                palavras_padrao_selecionadas.append(p)
        
        # Se não houver selecionadas, usar padrão
        if not palavras_padrao_selecionadas:
            palavras_padrao_selecionadas = processador.PALAVRAS_CHAVE_PADRAO.copy()
        
        palavras_selecionadas = st.multiselect(
            "🔍 Palavras-chave:",
            options=todas_palavras,
            default=palavras_padrao_selecionadas,
            help="Selecione as palavras-chave que deseja usar para filtrar"
        )
        
        # Campo para adicionar novas palavras
        st.markdown("**Adicionar nova palavra-chave:**")
        col_add, col_btn = st.columns([3, 1])
        
        with col_add:
            nova_palavra = st.text_input(
                "Nova palavra:",
                key="nova_palavra_input",
                label_visibility="collapsed",
                placeholder="Digite uma nova palavra-chave"
            )
        
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Adicionar", key="adicionar_palavra", use_container_width=True):
                if nova_palavra and nova_palavra.strip():
                    palavra_limpa = nova_palavra.strip()
                    # Verificar se já existe (case insensitive)
                    palavras_lower = [p.lower() for p in todas_palavras]
                    if palavra_limpa.lower() not in palavras_lower:
                        # Adicionar à lista de personalizadas
                        st.session_state.palavras_chave_personalizadas.append(palavra_limpa)
                        # Adicionar às selecionadas
                        if palavra_limpa not in palavras_selecionadas:
                            palavras_selecionadas.append(palavra_limpa)
                        st.success(f"✅ Palavra '{palavra_limpa}' adicionada!")
                        st.rerun()
                    else:
                        st.warning(f"⚠️ A palavra '{palavra_limpa}' já existe na lista!")
        
        # Atualizar session state
        st.session_state.palavras_chave = palavras_selecionadas if palavras_selecionadas else processador.PALAVRAS_CHAVE_PADRAO.copy()
        
        st.markdown("---")
        
        gerenciador = GerenciadorRevistas(db)
        
        # Seção de Upload
        st.subheader("📤 Upload de Revista")
        gerenciador.renderizar_upload()
        
        st.markdown("---")
        
        # Seção de Download e Processamento Automático
        st.subheader("📥 Download e Processar Revistas")
        st.markdown("Baixe revistas do storage e processe automaticamente com os filtros configurados acima")
        
        if st.button("🔄 Atualizar Lista", key="refresh_revistas"):
            st.rerun()
        
        revistas = gerenciador.listar_revistas_disponiveis()
        
        if revistas:
            st.info(f"**{len(revistas)}** revista(s) disponível(eis)")
            
            # Mostrar revistas em uma lista selecionável (múltipla)
            revistas_selecionadas = st.multiselect(
                "Selecione uma ou mais revistas para baixar e processar:",
                options=revistas,
                key="select_revistas_multiple"
            )
            
            col_download, col_delete = st.columns(2)
            
            with col_download:
                if revistas_selecionadas:
                    if st.button("⬇️ Baixar e Processar", key="download_processar_revista", type="primary"):
                        total_processos = 0
                        sucessos = 0
                        erros = []
                        
                        with st.spinner(f"Processando {len(revistas_selecionadas)} revista(s)..."):
                            for revista_selecionada in revistas_selecionadas:
                                # Baixar revista
                                arquivo_bytes = gerenciador.download_revista(revista_selecionada)
                                if arquivo_bytes:
                                    # Processar revista com filtros
                                    arquivo_upload = BytesIO(arquivo_bytes)
                                    arquivo_upload.name = revista_selecionada
                                    
                                    # Mostrar informações dos filtros configurados (apenas na primeira)
                                    if revista_selecionada == revistas_selecionadas[0]:
                                        classes_info = f"Classes: {', '.join(st.session_state.classes_desejadas) if st.session_state.classes_desejadas else 'Nenhuma'}"
                                        palavras_info = f"Palavras-chave: {len(st.session_state.palavras_chave)} palavra(s)" if st.session_state.palavras_chave else "Palavras-chave: Nenhuma"
                                        st.info(f"🔧 Filtros configurados - {classes_info} | {palavras_info}")
                                    
                                    st.info(f"📄 Processando: {revista_selecionada}")
                                    df = processar_arquivo_upload(arquivo_upload, processador, db)
                                    
                                    if df is not None and not df.empty:
                                        total_processos += len(df)
                                        
                                        # Salvar no Supabase automaticamente
                                        # Salvar número da revista na tabela revista (opcional - não bloqueia se falhar)
                                        if st.session_state.numero_revista:
                                            try:
                                                resultado_revista = db.salvar_numero_revista(st.session_state.numero_revista)
                                                if not resultado_revista['sucesso']:
                                                    erro_revista = resultado_revista.get('erro', 'Erro desconhecido')
                                                    if 'row-level security' not in str(erro_revista).lower() and '42501' not in str(erro_revista):
                                                        erros.append(f"{revista_selecionada} - Erro ao salvar número: {erro_revista}")
                                            except Exception as e:
                                                erros.append(f"{revista_selecionada} - Erro ao salvar número: {str(e)}")
                                        
                                        # Salvar processos
                                        try:
                                            resultado = db.salvar_processos(df, st.session_state.numero_revista)
                                            
                                            if resultado['sucesso'] and resultado['processos_salvos'] > 0:
                                                sucessos += 1
                                                st.success(f"✅ {revista_selecionada}: {resultado['processos_salvos']} processo(s) salvo(s)")
                                            else:
                                                erros.append(f"{revista_selecionada}: {resultado.get('erro', 'Nenhum processo salvo')}")
                                        except Exception as e:
                                            erros.append(f"{revista_selecionada}: Erro ao salvar - {str(e)}")
                                    else:
                                        erros.append(f"{revista_selecionada}: Nenhum processo encontrado após aplicar filtros")
                                else:
                                    erros.append(f"{revista_selecionada}: Erro ao baixar arquivo")
                        
                        # Resumo final
                        st.markdown("---")
                        if sucessos > 0:
                            st.success(f"✅ **{sucessos}** revista(s) processada(s) com sucesso! Total de **{total_processos}** processo(s).")
                        if erros:
                            st.warning(f"⚠️ {len(erros)} erro(s) encontrado(s):")
                            for erro in erros[:10]:  # Mostrar até 10 erros
                                st.text(f"  - {erro}")
                        
                        if sucessos > 0:
                            st.rerun()
                else:
                    st.info("👈 Selecione pelo menos uma revista para processar.")
            
            with col_delete:
                if revistas_selecionadas:
                    if st.button("🗑️ Deletar do Storage", key="delete_revistas", type="secondary"):
                        deletados = 0
                        for revista in revistas_selecionadas:
                            if gerenciador.deletar_revista(revista):
                                deletados += 1
                        
                        if deletados > 0:
                            st.success(f"✅ {deletados} revista(s) deletada(s) do storage!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao deletar revistas")
                else:
                    st.info("👈 Selecione revistas para deletar.")
        else:
            st.info("Nenhuma revista encontrada no storage.")


def processar_arquivo_upload(arquivo_upload, processador: ProcessadorINPI, db):
    """Processa arquivo enviado pelo usuário"""
    extensao = definir_tipo_arquivo(arquivo_upload)
    
    try:
        if extensao == '.xml':
            df, numero_revista = processador.processar_xml(arquivo_upload)
            st.session_state.numero_revista = numero_revista
        elif extensao == '.csv':
            df = processador.processar_csv(arquivo_upload)
        elif extensao == '.xlsx':
            df = processador.processar_excel(arquivo_upload)
        else:
            st.error("Formato de arquivo não suportado")
            return None
        
        if df is not None and not df.empty:
            # Para arquivos XML, os dados já vêm padronizados do processador
            # Para CSV/Excel, padronizar nomes de colunas
            if extensao in ['.csv', '.xlsx']:
                # Padronizar nomes de colunas
                mapeamento_colunas = {}
                for col in df.columns:
                    col_lower = col.lower()
                    if 'numero' in col_lower or 'processo' in col_lower:
                        mapeamento_colunas[col] = 'numero_processo'
                    elif 'marca' in col_lower:
                        mapeamento_colunas[col] = 'marca'
                    elif 'classe' in col_lower or 'nice' in col_lower:
                        mapeamento_colunas[col] = 'classe'
                    elif 'titular' in col_lower or 'requerente' in col_lower or 'proprietario' in col_lower:
                        mapeamento_colunas[col] = 'titular'
                    elif 'data' in col_lower or 'concessao' in col_lower:
                        mapeamento_colunas[col] = 'data_concessao'
                
                df = df.rename(columns=mapeamento_colunas)
            
            # Normalizar classes (para garantir formato consistente)
            coluna_classe = processador._encontrar_coluna(df, ['classe', 'classe_nice', 'class'])
            if coluna_classe:
                df = processador.normalizar_classes(df, coluna_classe)
            
            # Aplicar filtros usando o método unificado do processador
            classes_desejadas = st.session_state.get('classes_desejadas', [])
            palavras_chave = st.session_state.get('palavras_chave', [])
            
            # Verificar se há filtros configurados
            tem_filtro_classes = classes_desejadas and len(classes_desejadas) > 0
            tem_filtro_palavras = palavras_chave and len(palavras_chave) > 0
            
            if tem_filtro_classes or tem_filtro_palavras:
                # Encontrar coluna de especificação se necessário
                coluna_espec = None
                if tem_filtro_palavras:
                    coluna_espec = processador._encontrar_coluna(df, ['especificacao', 'especificação', 'specification'])
                
                # Aplicar filtros usando método unificado
                df = processador.filtrar_processos(
                    df,
                    classes_desejadas=classes_desejadas if tem_filtro_classes else None,
                    palavras_chave=palavras_chave if tem_filtro_palavras and coluna_espec else None,
                    coluna_classe=coluna_classe if coluna_classe else 'classe',
                    coluna_especificacao=coluna_espec if coluna_espec else 'especificacao'
                )
            
            return df
        else:
            st.error("Nenhum processo concedido encontrado no arquivo.")
            return None
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {str(e)}")
        return None


def renderizar_visualizacao_dados(df, processador: ProcessadorINPI):
    """Renderiza a visualização dos dados processados"""
    st.subheader("📊 Visualização dos Dados")
    
    # Identificar coluna de classe automaticamente
    coluna_classe = processador._encontrar_coluna(df, ['classe', 'classe_nice', 'class'])
    
    # Se não encontrou com padrões específicos, buscar mais amplamente
    if not coluna_classe:
        for col in df.columns:
            if 'classe' in col.lower() or 'nice' in col.lower():
                coluna_classe = col
                break
    
    if coluna_classe:
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            classes_unicas = sorted([str(c) for c in df[coluna_classe].unique() if pd.notna(c)])
            classe_selecionada = st.selectbox(
                "Filtrar por Classe:",
                options=["Todas"] + classes_unicas
            )
        
        with col2:
            # Filtrar por marca se existir coluna de marca
            coluna_marca = processador._encontrar_coluna(df, ['marca', 'nome_marca', 'marca_nome'])
            
            # Se não encontrou, buscar mais amplamente
            if not coluna_marca:
                for col in df.columns:
                    if 'marca' in col.lower():
                        coluna_marca = col
                        break
            
            if coluna_marca:
                marcas_unicas = sorted([str(m) for m in df[coluna_marca].unique() if pd.notna(m)])
                marca_selecionada = st.selectbox(
                    "Filtrar por Marca:",
                    options=["Todas"] + marcas_unicas
                )
            else:
                marca_selecionada = "Todas"
        
        with col3:
            st.metric("Total de Processos", len(df))
        
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if classe_selecionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado[coluna_classe].astype(str) == classe_selecionada]
        
        if marca_selecionada != "Todas" and coluna_marca:
            df_filtrado = df_filtrado[df_filtrado[coluna_marca].astype(str) == marca_selecionada]
        
        st.markdown("---")
        
        # Estatísticas por classe
        st.subheader("📈 Estatísticas por Classe")
        
        if not df_filtrado.empty:
            contagem_classes = df_filtrado[coluna_classe].value_counts().sort_index()
            
            # Métricas resumidas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de Classes", len(contagem_classes))
            with col2:
                st.metric("Total de Registros", len(df_filtrado))
            with col3:
                # Contar processos únicos
                if 'numero_processo' in df_filtrado.columns:
                    processos_unicos = df_filtrado['numero_processo'].nunique()
                    st.metric("Processos Únicos", processos_unicos)
                else:
                    st.metric("Processos Únicos", "-")
            with col4:
                # Classe mais frequente
                classe_mais_freq = contagem_classes.index[0] if len(contagem_classes) > 0 else "-"
                st.metric("Classe Mais Frequente", classe_mais_freq)
            
            st.markdown("---")
            
            # Tabela detalhada por classe
            st.markdown("---")
            st.subheader("📋 Detalhamento por Classe")
            
            # Ordenar classes numericamente quando possível
            classes_ordenadas = sorted(
                df_filtrado[coluna_classe].unique(),
                key=lambda x: (int(x) if str(x).isdigit() else 999, str(x))
            )
            
            for classe in classes_ordenadas:
                if pd.notna(classe):
                    df_classe = df_filtrado[df_filtrado[coluna_classe] == classe].copy()
                    
                    # Determinar tipo de classe (Produto ou Serviço)
                    tipo_classe = ""
                    try:
                        num_classe = int(str(classe).strip())
                        if 1 <= num_classe <= 34:
                            tipo_classe = " (Produto)"
                        elif 35 <= num_classe <= 45:
                            tipo_classe = " (Serviço)"
                    except:
                        pass
                    
                    # Selecionar colunas principais para exibição
                    colunas_principais = ['numero_processo', 'marca', 'titular', 'data_concessao']
                    colunas_disponiveis = [col for col in colunas_principais if col in df_classe.columns]
                    
                    with st.expander(f"Classe {classe}{tipo_classe} - {len(df_classe)} registro(s)"):
                        st.dataframe(
                            df_classe[colunas_disponiveis] if colunas_disponiveis else df_classe,
                            use_container_width=True,
                            hide_index=True
                        )
            
            # Tabela geral
            st.markdown("---")
            st.subheader("📋 Dados Filtrados")
            st.dataframe(
                df_filtrado,
                use_container_width=True,
                hide_index=True
            )
            
        else:
            st.warning("Nenhum processo encontrado com os filtros selecionados.")
    
    else:
        st.warning("⚠️ Coluna de classe não encontrada no arquivo. Exibindo dados completos.")
        st.dataframe(df, use_container_width=True, hide_index=True)


def renderizar_aba_consultar_dados(processador: ProcessadorINPI, db, init_supabase):
    """Renderiza a aba de Consultar Dados"""
    st.header("🔍 Consultar Dados")
    st.markdown("Selecione as classes para carregar os processos do Supabase")
    st.markdown("---")
    
    if db is None:
        st.error("⚠️ Supabase não configurado. Configure SUPABASE_URL e SUPABASE_KEY no arquivo .env")
        if st.button("🔄 Tentar Reconectar", key="reconnect_supabase_aba2"):
            init_supabase.clear()
            st.rerun()
    else:
        # Inicializar df_processos_consultar se não existir (não carregar nada automaticamente)
        if 'df_processos_consultar' not in st.session_state:
            st.session_state.df_processos_consultar = None
        
        # Seção: Seleção de classes (OBRIGATÓRIA antes de carregar)
        st.subheader("🎯 Selecione as Classes")
        opcoes_classes = [str(i) for i in range(1, 46)]
        
        classes_selecionadas_consultar = st.multiselect(
            "Classes Nice (1-45):",
            options=opcoes_classes,
            default=st.session_state.get('classes_consultar_selecionadas', []),
            help="Selecione uma ou mais classes para carregar apenas esses processos do banco",
            key="multiselect_classes_consultar"
        )
        st.session_state.classes_consultar_selecionadas = classes_selecionadas_consultar
        
        col_btn_carregar, col_btn_limpar = st.columns([1, 1])
        with col_btn_carregar:
            carregar_clicado = st.button("📥 Carregar Dados", type="primary", key="btn_carregar_consultar", use_container_width=True)
        with col_btn_limpar:
            limpar_clicado = st.button("🔄 Limpar e Recarregar", key="btn_limpar_consultar", use_container_width=True)
        
        if limpar_clicado:
            st.session_state.df_processos_consultar = None
            st.session_state.verificacoes_dict = {}
            st.rerun()
        
        if carregar_clicado:
            if not classes_selecionadas_consultar:
                st.warning("⚠️ Selecione pelo menos uma classe para carregar os dados.")
            else:
                try:
                    with st.spinner(f"Carregando processos das classes {', '.join(classes_selecionadas_consultar)}..."):
                        df_todos = db.buscar_processos(classes=classes_selecionadas_consultar)
                        if not df_todos.empty:
                            if 'verificacao' not in df_todos.columns:
                                df_todos['verificacao'] = ''
                            st.session_state.df_processos_consultar = df_todos.copy()
                            st.success(f"✅ {len(df_todos):,} processo(s) carregado(s) das classes {', '.join(classes_selecionadas_consultar)}!")
                            st.rerun()
                        else:
                            st.session_state.df_processos_consultar = pd.DataFrame()
                            st.warning(f"⚠️ Nenhum processo encontrado para as classes {', '.join(classes_selecionadas_consultar)}.")
                            st.rerun()
                except Exception as e:
                    erro_msg = str(e)
                    st.error(f"❌ Erro ao carregar dados: {erro_msg}")
                    if 'timeout' in erro_msg.lower() or 'connection' in erro_msg.lower():
                        st.info("💡 Verifique sua conexão com a internet.")
                    elif 'rls' in erro_msg.lower() or 'row-level security' in erro_msg.lower():
                        st.info("💡 Verifique as políticas RLS do Supabase na tabela dados_marcas.")
        
        df = st.session_state.df_processos_consultar.copy() if st.session_state.df_processos_consultar is not None else pd.DataFrame()
        
        if not df.empty:
            # Garantir que a coluna verificacao existe
            if 'verificacao' not in df.columns:
                df['verificacao'] = ''
            
            # Inicializar verificações no session state se necessário
            if 'verificacoes_dict' not in st.session_state:
                st.session_state.verificacoes_dict = {}
                # Preencher com valores existentes
                for idx, row in df.iterrows():
                    processo = str(row.get('processo', f'row_{idx}'))
                    if pd.notna(row.get('verificacao')) and row.get('verificacao') != '':
                        st.session_state.verificacoes_dict[processo] = row['verificacao']
            
            # Identificar coluna de classe
            coluna_classe = processador._encontrar_coluna(df, ['classe', 'classe_nice', 'class'])
            if not coluna_classe:
                for col in df.columns:
                    if 'classe' in col.lower() or 'nice' in col.lower():
                        coluna_classe = col
                        break
            
            # Identificar coluna de marca
            coluna_marca = processador._encontrar_coluna(df, ['marca', 'nome_marca', 'marca_nome'])
            if not coluna_marca:
                for col in df.columns:
                    if 'marca' in col.lower():
                        coluna_marca = col
                        break
            
            # Identificar coluna de revista
            coluna_revista = processador._encontrar_coluna(df, ['n_revista', 'numero_revista', 'revista'])
            if not coluna_revista:
                for col in df.columns:
                    if 'revista' in col.lower() or col.lower() == 'n_revista':
                        coluna_revista = col
                        break
            
            st.info(f"📊 **{len(df)}** processo(s) encontrado(s)")
            st.markdown("---")
            
            # Filtros
            st.subheader("🔍 Filtros")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if coluna_classe:
                    classes_unicas = sorted([str(c) for c in df[coluna_classe].unique() if pd.notna(c)])
                    classe_selecionada = st.selectbox(
                        "Filtrar por Classe:",
                        options=["Todas"] + classes_unicas,
                        key="filtro_classe_consultar"
                    )
                else:
                    classe_selecionada = "Todas"
            
            with col2:
                if coluna_marca:
                    marcas_unicas = sorted([str(m) for m in df[coluna_marca].unique() if pd.notna(m)])
                    marca_selecionada = st.selectbox(
                        "Filtrar por Marca:",
                        options=["Todas"] + marcas_unicas,
                        key="filtro_marca_consultar"
                    )
                else:
                    marca_selecionada = "Todas"
            
            with col3:
                if coluna_revista:
                    revistas_unicas = sorted([str(r) for r in df[coluna_revista].unique() if pd.notna(r)], reverse=True)
                    revista_selecionada = st.selectbox(
                        "Filtrar por Revista:",
                        options=["Todas"] + revistas_unicas,
                        key="filtro_revista_consultar"
                    )
                else:
                    revista_selecionada = "Todas"
                    st.warning("⚠️ Coluna de revista não encontrada para filtro.")
            
            with col4:
                st.metric("Total de Processos", len(df))
            
            st.markdown("---")
            
            # Aplicar filtros
            df_filtrado = df.copy()
            
            if classe_selecionada != "Todas" and coluna_classe:
                df_filtrado = df_filtrado[df_filtrado[coluna_classe].astype(str) == classe_selecionada]
            
            if marca_selecionada != "Todas" and coluna_marca:
                df_filtrado = df_filtrado[df_filtrado[coluna_marca].astype(str) == marca_selecionada]
            
            if revista_selecionada != "Todas" and coluna_revista:
                df_filtrado = df_filtrado[df_filtrado[coluna_revista].astype(str) == revista_selecionada]
            
            if len(df_filtrado) < len(df):
                st.info(f"📋 **{len(df_filtrado)}** processo(s) após aplicar filtros (de {len(df)} total)")
            
            st.markdown("---")
            
            # Atualizar coluna verificacao com valores do session state
            for idx, row in df_filtrado.iterrows():
                processo = str(row.get('processo', f'row_{idx}'))
                if processo in st.session_state.verificacoes_dict:
                    df_filtrado.at[idx, 'verificacao'] = st.session_state.verificacoes_dict[processo]
            
            # Separar processos verificados e não verificados
            # Processos SEM verificação (vazios ou None)
            df_nao_verificados = df_filtrado[
                (df_filtrado['verificacao'].isna()) | 
                (df_filtrado['verificacao'] == '') | 
                (df_filtrado['verificacao'].astype(str).str.strip() == '')
            ].copy()
            
            # Processos COM verificação (preenchidos)
            df_verificados = df_filtrado[
                (df_filtrado['verificacao'].notna()) & 
                (df_filtrado['verificacao'] != '') & 
                (df_filtrado['verificacao'].astype(str).str.strip() != '')
            ].copy()
            
            # Remover colunas id, created_at e status se existirem
            colunas_para_remover = ['id', 'created_at', 'status']
            
            # ========== TABELA 1: PROCESSOS NÃO VERIFICADOS ==========
            st.subheader("📋 Processos Filtrados (Não Verificados)")
            st.markdown("Selecione os processos que deseja marcar como verificados")
            
            if not df_nao_verificados.empty:
                # Inicializar seleção de processos se não existir
                if 'processos_selecionados' not in st.session_state:
                    st.session_state.processos_selecionados = set()
                
                colunas_para_exibir_nao_ver = df_nao_verificados.columns.tolist()
                for col in colunas_para_remover:
                    if col in colunas_para_exibir_nao_ver:
                        colunas_para_exibir_nao_ver.remove(col)
                
                # Remover coluna verificacao da exibição (não precisamos mais dela aqui)
                if 'verificacao' in colunas_para_exibir_nao_ver:
                    colunas_para_exibir_nao_ver.remove('verificacao')
                
                df_exibicao_nao_ver = df_nao_verificados[colunas_para_exibir_nao_ver].copy()
                
                # Resetar índice para garantir mapeamento correto
                df_exibicao_nao_ver = df_exibicao_nao_ver.reset_index(drop=True)
                df_nao_verificados_reset = df_nao_verificados.reset_index(drop=True)
                
                # Adicionar coluna de seleção (checkbox)
                df_exibicao_nao_ver.insert(0, 'Selecionar', False)
                
                # Configurar coluna de checkbox
                column_config_nao_ver = {
                    'Selecionar': st.column_config.CheckboxColumn(
                        "Selecionar",
                        help="Marque os processos que deseja verificar",
                        width="small"
                    )
                }
                
                # Usar data_editor para permitir seleção
                df_editado_nao_ver = st.data_editor(
                    df_exibicao_nao_ver,
                    use_container_width=True,
                    hide_index=True,
                    column_config=column_config_nao_ver,
                    num_rows="fixed",
                    key="tabela_processos_nao_verificados"
                )
                
                # Botão para marcar como verificado
                processos_selecionados = df_editado_nao_ver[df_editado_nao_ver['Selecionar'] == True]
                num_selecionados = len(processos_selecionados)
                
                col_btn, col_info = st.columns([1, 2])
                
                with col_btn:
                    if st.button("✅ Marcar como Verificado", 
                                type="primary", 
                                disabled=(num_selecionados == 0),
                                key="btn_marcar_verificado",
                                use_container_width=True):
                        # Obter números dos processos selecionados
                        processos_para_verificar = []
                        # O df_editado tem a mesma ordem que df_nao_verificados_reset (índices resetados)
                        indices_selecionados = processos_selecionados.index.tolist()
                        
                        for idx_editado in indices_selecionados:
                            # O índice do df_editado corresponde ao índice do df_nao_verificados_reset
                            if idx_editado < len(df_nao_verificados_reset):
                                processo_num = df_nao_verificados_reset.iloc[idx_editado].get('processo', None)
                                if processo_num:
                                    processos_para_verificar.append(str(processo_num))
                        
                        if processos_para_verificar:
                            # Marcar como verificado (usar valor padrão "verificado")
                            verificacoes_para_salvar = {proc: "verificado" for proc in processos_para_verificar}
                            
                            with st.spinner(f"Marcando {len(verificacoes_para_salvar)} processo(s) como verificado(s)..."):
                                resultado = db.atualizar_verificacoes_lote(verificacoes_para_salvar)
                                if resultado['sucesso']:
                                    # Atualizar session state
                                    for proc in processos_para_verificar:
                                        st.session_state.verificacoes_dict[proc] = "verificado"
                                        # Atualizar no DataFrame completo
                                        mask = df['processo'] == proc
                                        if mask.any():
                                            df.loc[mask, 'verificacao'] = "verificado"
                                            st.session_state.df_processos_consultar.loc[mask, 'verificacao'] = "verificado"
                                    
                                    st.success(f"✅ {resultado['sucessos']} processo(s) marcado(s) como verificado(s)!")
                                    if resultado.get('erros'):
                                        st.warning(f"⚠️ {len(resultado['erros'])} erro(s) ao salvar algumas verificações.")
                                    # Recarregar dados para atualizar a separação
                                    st.rerun()
                                else:
                                    st.error(f"❌ Erro ao salvar verificações: {resultado.get('erro', 'Erro desconhecido')}")
                
                with col_info:
                    st.info(f"📊 **{len(df_nao_verificados)}** processo(s) não verificado(s) | **{num_selecionados}** selecionado(s)")
            else:
                st.info("✅ Todos os processos já foram verificados!")
                df_editado_nao_ver = pd.DataFrame()
            
            st.markdown("---")
            
            # ========== TABELA 2: PROCESSOS VERIFICADOS ==========
            st.subheader("✅ Processos Verificados")
            st.markdown("Processos que já receberam verificação")
            
            if not df_verificados.empty:
                colunas_para_exibir_ver = df_verificados.columns.tolist()
                for col in colunas_para_remover:
                    if col in colunas_para_exibir_ver:
                        colunas_para_exibir_ver.remove(col)
                
                # Remover coluna verificacao da exibição (apenas para visualização)
                if 'verificacao' in colunas_para_exibir_ver:
                    colunas_para_exibir_ver.remove('verificacao')
                
                df_exibicao_ver = df_verificados[colunas_para_exibir_ver].copy()
                
                # Apenas exibir (sem edição)
                st.dataframe(
                    df_exibicao_ver,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.info(f"📊 **{len(df_verificados)}** processo(s) verificado(s)")
            else:
                st.info("ℹ️ Nenhum processo verificado ainda.")
        else:
            st.info("👆 Selecione as classes acima e clique em **Carregar Dados** para buscar os processos.")



