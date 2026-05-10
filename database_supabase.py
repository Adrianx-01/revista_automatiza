"""
Módulo para gerenciar conexão e operações com Supabase
"""
import os
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
import dotenv
import pandas as pd
from datetime import datetime
from io import BytesIO

# Carregar variáveis de ambiente com override para Streamlit
# Tenta múltiplos caminhos para encontrar o .env
env_paths = [
    Path(__file__).parent / '.env',  # Mesmo diretório do arquivo
    Path.cwd() / '.env',              # Diretório atual de trabalho
    Path.home() / '.env',             # Home do usuário (fallback)
]

env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        dotenv.load_dotenv(dotenv_path=str(env_path), override=True)
        env_loaded = True
        break

# Se não encontrou, tenta carregar do diretório atual sem caminho específico
if not env_loaded:
    dotenv.load_dotenv(override=True)

# Importar Supabase com tratamento de versão
def _detectar_versao_supabase():
    """Detecta qual versão do Supabase está instalada"""
    try:
        import supabase
        # Tentar acessar __version__ se disponível
        if hasattr(supabase, '__version__'):
            version_str = supabase.__version__
            major_version = int(version_str.split('.')[0])
            return major_version
        else:
            # Tentar importar métodos específicos da versão 2.x
            try:
                from supabase.client import Client
                return 2
            except ImportError:
                # Se conseguir importar create_client, provavelmente é 1.x ou 2.x
                from supabase import create_client
                # Testar se tem métodos da versão 2.x
                return 2  # Assumir 2.x por padrão (mais comum)
    except ImportError:
        raise ImportError(
            "Biblioteca supabase não encontrada.\n"
            "Instale com: pip install supabase>=2.0.0\n"
            "Ou para versão 1.x: pip install supabase-py==1.0.3"
        )

# Importar create_client
try:
    from supabase import create_client
    SUPABASE_VERSION = _detectar_versao_supabase()
    # Client é opcional na versão 2.x
    try:
        from supabase.client import Client
    except ImportError:
        Client = type(None)  # Tipo genérico se não disponível
except ImportError:
    # Fallback para versão 1.x (supabase-py)
    try:
        from supabase import create_client, Client
        SUPABASE_VERSION = 1
    except ImportError:
        raise ImportError(
            "Biblioteca supabase não encontrada.\n"
            "Instale com: pip install supabase>=2.0.0\n"
            "Ou para versão 1.x: pip install supabase-py==1.0.3"
        )


class DatabaseSupabase:
    """Classe para gerenciar operações com Supabase"""
    
    def __init__(self):
        """Inicializa conexão com Supabase"""
        # Recarregar .env para garantir que está atualizado (importante no Streamlit)
        for env_path in env_paths:
            if env_path.exists():
                dotenv.load_dotenv(dotenv_path=str(env_path), override=True)
                break
        else:
            dotenv.load_dotenv(override=True)
        
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            # Verificar se algum arquivo .env existe
            env_found = any(Path(p).exists() for p in env_paths)
            
            mensagem = "SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env\n\n"
            if not env_found:
                mensagem += "⚠️ O arquivo .env não foi encontrado nos seguintes locais:\n"
                for p in env_paths:
                    mensagem += f"   - {p}\n"
                mensagem += "\nCrie um arquivo .env na raiz do projeto com o seguinte formato:\n\n"
            else:
                mensagem += "⚠️ As variáveis SUPABASE_URL e SUPABASE_KEY estão vazias ou não foram encontradas.\n"
                mensagem += "Verifique se o arquivo .env contém:\n\n"
            
            mensagem += "SUPABASE_URL=https://seu-projeto.supabase.co\n"
            mensagem += "SUPABASE_KEY=sua-chave-api-aqui\n\n"
            mensagem += "Para obter essas credenciais:\n"
            mensagem += "1. Acesse https://supabase.com e faça login\n"
            mensagem += "2. Selecione seu projeto\n"
            mensagem += "3. Vá em Settings > API\n"
            mensagem += "4. Copie a URL do projeto (Project URL) para SUPABASE_URL\n"
            mensagem += "5. Copie a anon/public key para SUPABASE_KEY"
            
            raise ValueError(mensagem)
        
        # Criar cliente Supabase (compatível com versão 1.x e 2.x)
        try:
            self.supabase = create_client(self.url, self.key)
        except Exception as e:
            raise ValueError(
                f"Erro ao criar cliente Supabase: {str(e)}\n\n"
                f"Verifique se está usando a versão correta:\n"
                f"- Versão 2.x: pip install supabase>=2.0.0\n"
                f"- Versão 1.x: pip install supabase-py==1.0.3"
            )
        
        # Configurar bucket de revistas
        self.bucket_revistas = "revista"
    
    def fazer_login(self, email: str, senha: str) -> Dict:
        """
        Faz login do usuário no Supabase
        
        Args:
            email: Email do usuário
            senha: Senha do usuário
            
        Returns:
            Dicionário com resultado da operação
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": senha
            })
            
            if hasattr(response, 'user') and response.user:
                return {
                    'sucesso': True,
                    'usuario': {
                        'id': response.user.id,
                        'email': response.user.email
                    },
                    'session': response.session
                }
            else:
                return {
                    'sucesso': False,
                    'erro': 'Credenciais inválidas'
                }
        except Exception as e:
            erro_str = str(e).lower()
            if 'invalid' in erro_str or 'credentials' in erro_str:
                return {
                    'sucesso': False,
                    'erro': 'Email ou senha incorretos'
                }
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def fazer_logout(self) -> Dict:
        """
        Faz logout do usuário
        
        Returns:
            Dicionário com resultado da operação
        """
        try:
            self.supabase.auth.sign_out()
            return {
                'sucesso': True,
                'mensagem': 'Logout realizado com sucesso'
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def obter_usuario_atual(self) -> Optional[Dict]:
        """
        Obtém o usuário atual autenticado
        
        Returns:
            Dicionário com dados do usuário ou None se não autenticado
        """
        try:
            user = self.supabase.auth.get_user()
            if user and hasattr(user, 'user') and user.user:
                return {
                    'id': user.user.id,
                    'email': user.user.email
                }
            return None
        except Exception as e:
            return None
    
    def verificar_sessao(self) -> bool:
        """
        Verifica se há uma sessão ativa
        
        Returns:
            True se há sessão ativa, False caso contrário
        """
        try:
            user = self.supabase.auth.get_user()
            return user is not None and hasattr(user, 'user') and user.user is not None
        except Exception:
            return False
    
    def salvar_processos(self, df: pd.DataFrame, numero_revista: Optional[str] = None) -> Dict:
        """
        Salva processos concedidos na tabela dados_marcas do Supabase
        
        Args:
            df: DataFrame com processos concedidos
            numero_revista: Número da revista (opcional)
            
        Returns:
            Dicionário com informações sobre a operação
        """
        try:
            processos_salvos = 0
            erros = []
            
            # Preparar dados para inserção na tabela dados_marcas
            registros = []
            for _, row in df.iterrows():
                registro = {
                    'marca': str(row.get('marca', 'N/A')) if pd.notna(row.get('marca')) else None,
                    'classe': str(row.get('classe', 'N/A')) if pd.notna(row.get('classe')) else None,
                    'especificacao': str(row.get('especificacao', '')) if pd.notna(row.get('especificacao')) else None,
                    'empresa': str(row.get('titular', 'N/A')) if pd.notna(row.get('titular')) else None,
                    'status': str(row.get('status_classe', 'Deferido')) if pd.notna(row.get('status_classe')) else 'Deferido',
                    'processo': str(row.get('numero_processo', '')) if pd.notna(row.get('numero_processo')) else None,
                    'n_revista': numero_revista if numero_revista else None
                }
                registros.append(registro)
            
            # Inserir dados na tabela dados_marcas
            if registros:
                # Dividir em lotes para evitar limite de requisição
                tamanho_lote = 100
                
                for i in range(0, len(registros), tamanho_lote):
                    lote = registros[i:i + tamanho_lote]
                    lote_num = (i // tamanho_lote) + 1
                    
                    try:
                        resultado = self.supabase.table('dados_marcas').insert(lote).execute()
                        
                        if hasattr(resultado, 'data') and resultado.data:
                            processos_salvos += len(resultado.data)
                        elif hasattr(resultado, 'data') and resultado.data is None:
                            processos_salvos += len(lote)
                        else:
                            processos_salvos += len(lote)
                            
                    except Exception as e:
                        erro_lote = str(e)
                        erro_msg_completo = str(e)
                        
                        # Verificar se é erro de RLS
                        is_rls_error = 'row-level security' in erro_lote.lower() or '42501' in erro_msg_completo or 'rls' in erro_lote.lower()
                        
                        if is_rls_error:
                            erros.append(f"RLS bloqueado no lote {lote_num}: A política de segurança do Supabase está bloqueando a inserção. IMPORTANTE: Verifique se a política permite INSERT (não apenas SELECT). As políticas RLS precisam ter uma política específica para INSERT.")
                        
                        for reg in lote:
                            try:
                                resultado_individual = self.supabase.table('dados_marcas').insert(reg).execute()
                                
                                if hasattr(resultado_individual, 'data') and resultado_individual.data:
                                    processos_salvos += len(resultado_individual.data)
                                else:
                                    processos_salvos += 1
                                    
                            except Exception as e2:
                                erro_str = str(e2).lower()
                                erro_msg = str(e2)
                                
                                if 'row-level security' in erro_str or '42501' in erro_msg or 'rls' in erro_str:
                                    erros.append(f"RLS bloqueado: Processo {reg.get('processo', 'N/A')} - A política de segurança do Supabase está bloqueando a inserção")
                                elif 'duplicate' not in erro_str and 'unique' not in erro_str:
                                    erros.append(f"Erro ao inserir processo {reg.get('processo', 'N/A')}: {erro_msg}")
                                    
                        if len(erros) == 0 and ('duplicate' in erro_lote.lower() or 'unique' in erro_lote.lower()):
                            pass  # Duplicatas são ignoradas
                        else:
                            erros.append(f"Aviso no lote {lote_num}: {erro_lote}")
            
            return {
                'sucesso': True,
                'processos_salvos': processos_salvos,
                'total_registros': len(registros),
                'erros': erros
            }
        
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'processos_salvos': 0
            }
    
    def buscar_processos(
        self,
        classes: Optional[List[str]] = None,
        marca: Optional[str] = None,
        numero_revista: Optional[str] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Busca processos da tabela dados_marcas do Supabase
        
        Args:
            classes: Filtrar por lista de classes Nice (opcional). Ex: ['3', '8', '9']
            marca: Filtrar por marca (opcional)
            numero_revista: Filtrar por número da revista (opcional)
            limit: Limite de registros (None para buscar todos)
            
        Returns:
            DataFrame com processos encontrados
        """
        try:
            todos_registros = []
            pagina = 0
            tamanho_pagina = 1000
            limite_maximo = limit
            
            colunas_timestamp = ['updated_at', 'created_at', 'id']
            coluna_timestamp_funcional = None
            
            for col_timestamp in colunas_timestamp:
                try:
                    query_teste = self.supabase.table('dados_marcas').select('id').order(col_timestamp, desc=True).limit(1)
                    query_teste.execute()
                    coluna_timestamp_funcional = col_timestamp
                    break
                except:
                    continue
            
            if not coluna_timestamp_funcional:
                coluna_timestamp_funcional = 'id'
            
            while True:
                query = self.supabase.table('dados_marcas').select('*')
                
                if classes and len(classes) > 0:
                    query = query.in_('classe', classes)
                
                if marca:
                    query = query.ilike('marca', f'%{marca}%')
                
                if numero_revista:
                    query = query.eq('n_revista', numero_revista)
                
                # Aplicar paginação com a coluna que funciona
                query = query.order(coluna_timestamp_funcional, desc=True).range(
                    pagina * tamanho_pagina,
                    (pagina + 1) * tamanho_pagina - 1
                )
                
                resultado = query.execute()
                
                if resultado.data and len(resultado.data) > 0:
                    todos_registros.extend(resultado.data)
                    
                    # Se retornou menos que o tamanho da página, chegou ao fim
                    if len(resultado.data) < tamanho_pagina:
                        break
                    
                    # Se já atingimos o limite máximo (apenas se limite foi definido)
                    if limite_maximo is not None and len(todos_registros) >= limite_maximo:
                        todos_registros = todos_registros[:limite_maximo]
                        break
                    
                    pagina += 1
                else:
                    break
            
            if todos_registros:
                df = pd.DataFrame(todos_registros)
                # Mapear campos para compatibilidade com o resto do sistema
                if 'processo' in df.columns:
                    df['numero_processo'] = df['processo']
                if 'empresa' in df.columns:
                    df['titular'] = df['empresa']
                if 'n_revista' in df.columns:
                    df['numero_revista'] = df['n_revista']
                if 'status' in df.columns:
                    df['status_classe'] = df['status']
                return df
            else:
                return pd.DataFrame()
        
        except Exception as e:
            # Re-raise para que o erro seja tratado no Streamlit
            erro_msg = f"Erro ao buscar processos: {str(e)}"
            print(erro_msg)
            raise Exception(erro_msg)
    
    def contar_processos(
        self,
        classes: Optional[List[str]] = None,
        marca: Optional[str] = None,
        numero_revista: Optional[str] = None
    ) -> int:
        """
        Conta o número total de processos sem carregar todos os dados
        
        Args:
            classes: Filtrar por lista de classes (opcional)
            marca: Filtrar por marca (opcional)
            numero_revista: Filtrar por número da revista (opcional)
            
        Returns:
            Número total de processos (ou 0 se não conseguir contar)
        """
        try:
            try:
                query = self.supabase.table('dados_marcas').select('id', count='exact')
                
                if classes and len(classes) > 0:
                    query = query.in_('classe', classes)
                
                if marca:
                    query = query.ilike('marca', f'%{marca}%')
                
                if numero_revista:
                    query = query.eq('n_revista', numero_revista)
                
                resultado = query.execute()
                
                # O count pode vir no header HTTP ou no objeto
                if hasattr(resultado, 'count') and resultado.count is not None:
                    return resultado.count
                
                # Tentar acessar via headers ou outros atributos
                if hasattr(resultado, 'headers'):
                    count_header = resultado.headers.get('content-range', '')
                    if count_header:
                        # Formato: "0-999/1000" ou "*/1000"
                        parts = count_header.split('/')
                        if len(parts) == 2:
                            try:
                                return int(parts[1])
                            except:
                                pass
                
                # Se não conseguir, retornar None para indicar que não foi possível contar
                return 0
            except:
                # Se count='exact' não funcionar, fazer uma busca limitada para estimar
                # Mas isso não é ideal para grandes volumes
                return 0
        except Exception as e:
            print(f"Erro ao contar processos: {str(e)}")
            return 0
    
    def obter_estatisticas(self) -> Dict:
        """
        Obtém estatísticas dos processos salvos na tabela dados_marcas
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            # Buscar todos os registros (limitado para não sobrecarregar)
            todos_registros = self.supabase.table('dados_marcas').select('*').limit(10000).execute()
            
            if todos_registros.data and len(todos_registros.data) > 0:
                df = pd.DataFrame(todos_registros.data)
                
                total_registros = len(df)
                processos_unicos = df['processo'].nunique() if 'processo' in df.columns else 0
                classes_unicas = df['classe'].nunique() if 'classe' in df.columns else 0
            else:
                total_registros = 0
                processos_unicos = 0
                classes_unicas = 0
            
            return {
                'total_registros': total_registros,
                'processos_unicos': processos_unicos,
                'classes_unicas': classes_unicas
            }
        
        except Exception as e:
            print(f"Erro ao obter estatísticas: {str(e)}")
            return {
                'total_registros': 0,
                'processos_unicos': 0,
                'classes_unicas': 0,
                'erro': str(e)
            }
    
    def deletar_processos_revista(self, numero_revista: str) -> bool:
        """
        Deleta todos os processos de uma revista específica
        
        Args:
            numero_revista: Número da revista
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            resultado = self.supabase.table('dados_marcas').delete().eq('n_revista', numero_revista).execute()
            return True
        except Exception as e:
            print(f"Erro ao deletar processos: {str(e)}")
            return False
    
    @staticmethod
    def _normalizar_numero_revista(val) -> Optional[str]:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        s = str(val).strip()
        if not s or s.lower() in ('nan', 'none'):
            return None
        if s.isdigit():
            return str(int(s))
        return s

    def obter_revistas_processadas(self) -> List[str]:
        """
        Retorna lista de números de revistas já processadas (pagina a tabela inteira).
        """
        unicos: set = set()
        pagina = 0
        tamanho_pagina = 1000
        try:
            while True:
                try:
                    query = (
                        self.supabase.table('dados_marcas')
                        .select('n_revista')
                        .order('id', desc=False)
                        .range(
                            pagina * tamanho_pagina,
                            (pagina + 1) * tamanho_pagina - 1,
                        )
                    )
                    resultado = query.execute()
                except Exception:
                    query = (
                        self.supabase.table('dados_marcas')
                        .select('n_revista')
                        .range(
                            pagina * tamanho_pagina,
                            (pagina + 1) * tamanho_pagina - 1,
                        )
                    )
                    resultado = query.execute()
                if not resultado.data:
                    break
                for row in resultado.data:
                    n = self._normalizar_numero_revista(row.get('n_revista'))
                    if n:
                        unicos.add(n)
                if len(resultado.data) < tamanho_pagina:
                    break
                pagina += 1
            return sorted(
                unicos,
                key=lambda x: int(str(x)) if str(x).isdigit() else 0,
                reverse=True,
            )
        except Exception as e:
            print(f"Erro ao obter revistas: {str(e)}")
            return []
    
    def obter_pares_processo_classe_revista(self, n_revista: str) -> Set[Tuple[str, str]]:
        """
        Retorna conjunto (numero_processo, classe_normalizada) já gravados para a revista.
        Usado para evitar duplicar linhas ao complementar classes.
        """
        if not n_revista or not str(n_revista).strip():
            return set()
        n_rev = str(n_revista).strip()
        pares: Set[Tuple[str, str]] = set()
        pagina = 0
        tamanho_pagina = 1000
        
        def _norm_classe(val) -> str:
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return ''
            s = str(val).strip()
            if s.lower() in ('n/a', 'nan', 'none', ''):
                return ''
            if s.isdigit():
                return str(int(s))
            return s
        
        while True:
            try:
                query = (
                    self.supabase.table('dados_marcas')
                    .select('processo,classe')
                    .eq('n_revista', n_rev)
                    .order('id')
                    .range(pagina * tamanho_pagina, (pagina + 1) * tamanho_pagina - 1)
                )
                resultado = query.execute()
            except Exception:
                try:
                    query = (
                        self.supabase.table('dados_marcas')
                        .select('processo,classe')
                        .eq('n_revista', n_rev)
                        .range(pagina * tamanho_pagina, (pagina + 1) * tamanho_pagina - 1)
                    )
                    resultado = query.execute()
                except Exception as e:
                    print(f"Erro ao obter pares processo/classe: {str(e)}")
                    break
            
            if not resultado.data or len(resultado.data) == 0:
                break
            
            for row in resultado.data:
                proc = row.get('processo')
                if proc is None or (isinstance(proc, float) and pd.isna(proc)):
                    continue
                proc_s = str(proc).strip()
                cls = _norm_classe(row.get('classe'))
                if proc_s and cls:
                    pares.add((proc_s, cls))
            
            if len(resultado.data) < tamanho_pagina:
                break
            pagina += 1
        
        return pares
    
    def listar_classes_distintas_revista(self, n_revista: str) -> List[str]:
        """Classes Nice já presentes em dados_marcas para a revista (normalizadas)."""
        pares = self.obter_pares_processo_classe_revista(n_revista)
        classes = sorted({c for (_, c) in pares if c}, key=lambda x: (int(x) if str(x).isdigit() else 999, str(x)))
        return classes
    
    # Métodos para gerenciar storage de revistas
    def upload_revista(self, arquivo_bytes: bytes, nome_arquivo: str) -> Dict:
        """
        Faz upload de uma revista para o storage do Supabase
        
        Args:
            arquivo_bytes: Bytes do arquivo
            nome_arquivo: Nome do arquivo
            
        Returns:
            Dicionário com resultado da operação
        """
        try:
            resultado = self.supabase.storage.from_(self.bucket_revistas).upload(
                nome_arquivo,
                arquivo_bytes,
                file_options={"content-type": "application/xml"}
            )
            return {
                'sucesso': True,
                'mensagem': f'Arquivo {nome_arquivo} enviado com sucesso!'
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def listar_revistas(self) -> List[str]:
        """
        Lista todas as revistas no storage.
        A API do Storage pagina (padrão limit=100); percorre todas as páginas.
        """
        try:
            nomes: List[str] = []
            offset = 0
            limit = 100
            bucket = self.supabase.storage.from_(self.bucket_revistas)
            while True:
                arquivos = bucket.list(
                    "",
                    {
                        "limit": limit,
                        "offset": offset,
                        "sortBy": {"column": "name", "order": "desc"},
                    },
                )
                if not arquivos:
                    break
                for arquivo in arquivos:
                    n = arquivo.get('name')
                    if n:
                        nomes.append(n)
                if len(arquivos) < limit:
                    break
                offset += limit
            return sorted(set(nomes), reverse=True)
        except Exception as e:
            print(f"Erro ao listar revistas: {str(e)}")
            return []
    
    def download_revista(self, nome_arquivo: str) -> Optional[bytes]:
        """
        Faz download de uma revista do storage
        
        Args:
            nome_arquivo: Nome do arquivo para baixar
            
        Returns:
            Bytes do arquivo ou None em caso de erro
        """
        try:
            resultado = self.supabase.storage.from_(self.bucket_revistas).download(nome_arquivo)
            return resultado
        except Exception as e:
            print(f"Erro ao baixar revista: {str(e)}")
            return None
    
    def deletar_revista(self, nome_arquivo: str) -> bool:
        """
        Deleta uma revista do storage
        
        Args:
            nome_arquivo: Nome do arquivo para deletar
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            self.supabase.storage.from_(self.bucket_revistas).remove([nome_arquivo])
            return True
        except Exception as e:
            print(f"Erro ao deletar revista: {str(e)}")
            return False
    
    def salvar_numero_revista(self, numero_revista: str) -> Dict:
        """
        Salva o número da revista na tabela revista
        
        Args:
            numero_revista: Número da revista
            
        Returns:
            Dicionário com resultado da operação
        """
        try:
            # Validar que o número da revista não está vazio
            if not numero_revista or not str(numero_revista).strip():
                return {
                    'sucesso': False,
                    'erro': 'Número da revista não pode estar vazio'
                }
            
            resultado = self.supabase.table('revista').insert({
                'numero_revista': str(numero_revista).strip()
            }).execute()
            
            # Verificar se realmente foi inserido
            if resultado.data and len(resultado.data) > 0:
                return {
                    'sucesso': True,
                    'mensagem': f'Revista {numero_revista} registrada com sucesso!',
                    'data': resultado.data
                }
            else:
                return {
                    'sucesso': False,
                    'erro': 'Nenhum registro foi inserido (possível duplicata ou erro silencioso)'
                }
        except Exception as e:
            erro_str = str(e).lower()
            erro_completo = str(e)
            
            # Se for erro de duplicata, considerar sucesso
            if 'duplicate' in erro_str or 'unique' in erro_str or 'duplicate key' in erro_str:
                return {
                    'sucesso': True,
                    'mensagem': f'Revista {numero_revista} já estava registrada.'
                }
            
            # Verificar se é erro de RLS
            if 'row-level security' in erro_str or '42501' in erro_completo:
                return {
                    'sucesso': False,
                    'erro': f'Erro de Row Level Security (RLS) na tabela revista. É necessário criar uma política INSERT. Erro: {erro_completo}'
                }
            
            return {
                'sucesso': False,
                'erro': erro_completo
            }
    
    def listar_revistas_registradas(self) -> List[str]:
        """
        Lista todas as revistas registradas na tabela revista (paginado).
        """
        vistos: set = set()
        pagina = 0
        tamanho = 1000
        try:
            while True:
                try:
                    q = (
                        self.supabase.table('revista')
                        .select('numero_revista')
                        .order('numero_revista', desc=False)
                        .range(pagina * tamanho, (pagina + 1) * tamanho - 1)
                    )
                    resultado = q.execute()
                except Exception:
                    resultado = (
                        self.supabase.table('revista')
                        .select('numero_revista')
                        .range(pagina * tamanho, (pagina + 1) * tamanho - 1)
                        .execute()
                    )
                if not resultado.data:
                    break
                for r in resultado.data:
                    n = self._normalizar_numero_revista(r.get('numero_revista'))
                    if n:
                        vistos.add(n)
                if len(resultado.data) < tamanho:
                    break
                pagina += 1
            return sorted(
                vistos,
                key=lambda x: int(str(x)) if str(x).isdigit() else 0,
                reverse=True,
            )
        except Exception as e:
            print(f"Erro ao listar revistas registradas: {str(e)}")
            return []
    
    def atualizar_verificacao(self, processo: str, verificacao: str) -> Dict:
        """
        Atualiza a verificação de um processo na tabela dados_marcas
        
        Args:
            processo: Número do processo
            verificacao: Valor da verificação ('', 'marca não sendo utilizada', 'marca sendo utilizada')
            
        Returns:
            Dicionário com resultado da operação
        """
        try:
            resultado = self.supabase.table('dados_marcas').update({
                'verificacao': verificacao if verificacao else None
            }).eq('processo', processo).execute()
            
            return {
                'sucesso': True,
                'mensagem': f'Verificação atualizada para o processo {processo}'
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }
    
    def atualizar_verificacoes_lote(self, verificacoes: Dict[str, str]) -> Dict:
        """
        Atualiza múltiplas verificações de uma vez
        
        Args:
            verificacoes: Dicionário com {processo: verificacao}
            
        Returns:
            Dicionário com resultado da operação
        """
        try:
            sucessos = 0
            erros = []
            
            for processo, verificacao in verificacoes.items():
                resultado = self.atualizar_verificacao(processo, verificacao)
                if resultado['sucesso']:
                    sucessos += 1
                else:
                    erros.append(f"Processo {processo}: {resultado.get('erro', 'Erro desconhecido')}")
            
            return {
                'sucesso': sucessos > 0,
                'sucessos': sucessos,
                'total': len(verificacoes),
                'erros': erros
            }
        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e)
            }

