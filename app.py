"""
Aplicação principal - Orquestração
Apenas inicializa e chama as funções de UI
"""
import streamlit as st
from pathlib import Path
import dotenv

# Carregar variáveis de ambiente com override para garantir recarregamento no Streamlit
env_paths = [
    Path.cwd() / '.env',
    Path(__file__).parent / '.env',
]

env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        dotenv.load_dotenv(dotenv_path=str(env_path), override=True)
        env_loaded = True
        break

if not env_loaded:
    dotenv.load_dotenv(dotenv_path=".env", override=True)

from processador_inpi import ProcessadorINPI
from database_supabase import DatabaseSupabase
from ui_interface import renderizar_aplicacao

# Configuração da página
st.set_page_config(
    page_title="Revista INPI - Processos Concedidos",
    page_icon="📋",
    layout="wide"
)

# Inicializar processador
processador = ProcessadorINPI()

# Inicializar conexão com Supabase
@st.cache_resource
def init_supabase():
    """
    Inicializa conexão com Supabase - cacheado para melhor performance.
    """
    try:
        return DatabaseSupabase()
    except Exception as e:
        raise e

# Tentar inicializar conexão
try:
    db = init_supabase()
except Exception as e:
    db = None

# Renderizar aplicação
renderizar_aplicacao(processador, db, init_supabase)
