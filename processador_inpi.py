"""
Módulo auxiliar para processamento de arquivos da Revista do INPI
"""
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import re


class ProcessadorINPI:
    """Classe para processar arquivos da Revista do INPI"""
    
    # Classes de Nice - Produtos (1-34) e Serviços (35-45)
    CLASSES_NICE = {
        'produtos': list(range(1, 35)),
        'servicos': list(range(35, 46))
    }
    
    # Classes padrão para filtro (sem zeros à esquerda)
    CLASSES_PADRAO = ["3", "8", "9", "11", "12", "14", "16", "18", "20", "21", "24", "28", "35"]
    
    # Palavras-chave padrão para filtro
    PALAVRAS_CHAVE_PADRAO = [
        "telefone", "celular", "computador", "iluminação", "utensílios", "elétricos", 
        "jogos", "brinquedos", "imagem", "som", "eletricidade", "ferramentas", 
        "canecas", "garrafas", "elétricas", "ferramentas manuais", "cutelaria", "recipientes", "cosméticos", "Kits educacionais",
        "papelaria", "etiquetas", "embalagens", "papel", "artigos", "material", "sacolas", "preparações", "produtos", "substâncias",
        "cosméticas", "cosméticos", "máquinas", "amortecedor", "motor", "aparelho", "bobina",
        "bomba", "cabeçote", "veículo", "dispositivos", "Instrumentos", "bolsa", "bolsas", "malas", "couro",
        "mochilas", "nécessaires", "móveis", "almofadas", "apoio", "armários", "bancada", "bebê", "camas",
        "canis", "mobiliário", "animais", "animal", "metálicos", "metálicas", "mesas", "mobília", "metal",
        "têxtil", "tecido", "toalha", "cama", "malha", "mantas", "panos", "pano", "metais", "joias", "bijuterias",
        "relojoaria", "Caixas", "relógio", "Joia", "ouro", "pérolas", "pedras", "metal", "prata"
    ]
    
    def __init__(self):
        self.df_processos: Optional[pd.DataFrame] = None
    
    def processar_xml(self, caminho_arquivo) -> Tuple[pd.DataFrame, Optional[str]]:
        """
        Processa arquivo XML da Revista do INPI
        Identifica processos concedidos pelo despacho IPAS158 (Concessão de registro)
        
        Args:
            caminho_arquivo: Caminho ou objeto file do arquivo XML
            
        Returns:
            Tupla (DataFrame com processos concedidos, número da revista)
            Uma linha por classe deferida
        """
        try:
            tree = ET.parse(caminho_arquivo)
            root = tree.getroot()
            
            # Extrair número da revista
            numero_revista = None
            if root.tag.lower() == 'revista':
                numero_revista = root.get('numero', None)
            else:
                # Tentar encontrar elemento revista
                revista_elem = root.find('.//revista')
                if revista_elem is not None:
                    numero_revista = revista_elem.get('numero', None)
            
            processos = []
            
            # Buscar todos os processos na revista
            for processo in root.findall('.//processo'):
                # Verificar se tem despacho de concessão (IPAS158)
                despachos = processo.findall('.//despacho')
                tem_concessao = False
                
                for despacho in despachos:
                    codigo = despacho.get('codigo', '')
                    # Apenas IPAS158 - Concessão de registro
                    if codigo == 'IPAS158':
                        tem_concessao = True
                        break
                
                if tem_concessao:
                    # Extrair dados do processo concedido
                    dados_processo = self._extrair_dados_processo_inpi(processo)
                    
                    if dados_processo:
                        # Adicionar uma linha para cada classe deferida
                        processos.extend(dados_processo)
            
            if processos:
                return pd.DataFrame(processos), numero_revista
            else:
                return pd.DataFrame(), numero_revista
        
        except Exception as e:
            raise Exception(f"Erro ao processar XML: {str(e)}")
    
    def _extrair_dados_processo_inpi(self, processo) -> List[Dict]:
        """
        Extrai dados de um processo concedido do XML do INPI
        Retorna uma lista de dicionários, uma entrada por classe deferida
        
        Args:
            processo: Elemento XML do processo
            
        Returns:
            Lista de dicionários com dados do processo e classes deferidas
        """
        processos_classe = []
        
        # Extrair número do processo
        numero_processo = processo.get('numero', '')
        
        # Extrair data de concessão
        data_concessao = processo.get('data-concessao', processo.get('data_concessao', ''))
        
        # Extrair titular
        titular = None
        titulares = processo.findall('.//titular')
        if titulares:
            # Pegar o primeiro titular
            titular_elem = titulares[0]
            titular = titular_elem.get('nome-razao-social', '')
            if not titular:
                titular = titular_elem.text
        
        # Extrair marca
        marca = None
        marca_elem = processo.find('.//marca/nome')
        if marca_elem is not None:
            marca = marca_elem.text
        else:
            # Tentar buscar direto no elemento marca
            marca_elem = processo.find('.//marca')
            if marca_elem is not None:
                nome_elem = marca_elem.find('nome')
                if nome_elem is not None:
                    marca = nome_elem.text
        
        # Extrair procurador (opcional)
        procurador = None
        procurador_elem = processo.find('.//procurador')
        if procurador_elem is not None:
            procurador = procurador_elem.text
        
        # Processar classes Nice - apenas as que foram deferidas
        classes_nice = processo.findall('.//classe-nice')
        
        for classe_nice in classes_nice:
            status_classe = classe_nice.find('status')
            if status_classe is not None and status_classe.text:
                status_texto = status_classe.text.strip().lower()
                # Considerar apenas classes deferidas (aceita "Deferida" e "Deferido")
                if 'deferid' in status_texto:  # Funciona para "deferida" e "deferido"
                    codigo_classe = classe_nice.get('codigo', '')
                    # Manter formato original do XML - a normalização será feita na comparação
                    # O XML pode ter "03", "08", etc. e será normalizado no filtro
                    
                    # Extrair especificações
                    especificacao = None
                    espec_elem = classe_nice.find('especificacao')
                    if espec_elem is not None:
                        especificacao = espec_elem.text
                    
                    traducao = None
                    trad_elem = classe_nice.find('traducao-especificacao')
                    if trad_elem is not None:
                        traducao = trad_elem.text
                    
                    processo_dict = {
                        'numero_processo': numero_processo,
                        'marca': marca if marca else 'N/A',
                        'classe': codigo_classe if codigo_classe else 'N/A',
                        'titular': titular if titular else 'N/A',
                        'procurador': procurador if procurador else '',
                        'data_concessao': data_concessao if data_concessao else '',
                        'status_classe': status_classe.text if status_classe.text else 'Deferido',
                        'especificacao': especificacao if especificacao else '',
                        'traducao_especificacao': traducao if traducao else ''
                    }
                    
                    processos_classe.append(processo_dict)
        
        # Se não encontrou classes deferidas, mas o processo foi concedido, criar entrada sem classe
        if not processos_classe and numero_processo:
            processo_dict = {
                'numero_processo': numero_processo,
                'marca': marca if marca else 'N/A',
                'classe': 'N/A',
                'titular': titular if titular else 'N/A',
                'procurador': procurador if procurador else '',
                'data_concessao': data_concessao if data_concessao else '',
                'status_classe': 'Concedido',
                'especificacao': '',
                'traducao_especificacao': ''
            }
            processos_classe.append(processo_dict)
        
        return processos_classe
    
    def processar_csv(self, caminho_arquivo, separador=';', encoding='utf-8') -> pd.DataFrame:
        """
        Processa arquivo CSV da Revista do INPI
        
        Args:
            caminho_arquivo: Caminho ou objeto file do arquivo CSV
            separador: Separador usado no CSV (padrão: ;)
            encoding: Codificação do arquivo (padrão: utf-8)
            
        Returns:
            DataFrame com processos concedidos
        """
        try:
            # Tentar diferentes encodings
            encodings = [encoding, 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for enc in encodings:
                try:
                    df = pd.read_csv(caminho_arquivo, sep=separador, encoding=enc, on_bad_lines='skip', low_memory=False)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise Exception("Não foi possível ler o arquivo CSV com os encodings testados")
            
            # Identificar coluna de status
            coluna_status = self._encontrar_coluna(df, ['situacao', 'status', 'situacao_processo', 'estado'])
            
            if coluna_status:
                # Filtrar concedidos
                mask = df[coluna_status].astype(str).str.contains(
                    'concedido|concessao|deferido|registrado',
                    case=False,
                    na=False,
                    regex=True
                )
                df = df[mask]
            
            return df
        
        except Exception as e:
            raise Exception(f"Erro ao processar CSV: {str(e)}")
    
    def processar_excel(self, caminho_arquivo, planilha=0) -> pd.DataFrame:
        """
        Processa arquivo Excel da Revista do INPI
        
        Args:
            caminho_arquivo: Caminho ou objeto file do arquivo Excel
            planilha: Nome ou índice da planilha (padrão: 0)
            
        Returns:
            DataFrame com processos concedidos
        """
        try:
            df = pd.read_excel(caminho_arquivo, sheet_name=planilha, engine='openpyxl')
            
            # Identificar coluna de status
            coluna_status = self._encontrar_coluna(df, ['situacao', 'status', 'situacao_processo', 'estado'])
            
            if coluna_status:
                # Filtrar concedidos
                mask = df[coluna_status].astype(str).str.contains(
                    'concedido|concessao|deferido|registrado',
                    case=False,
                    na=False,
                    regex=True
                )
                df = df[mask]
            
            return df
        
        except Exception as e:
            raise Exception(f"Erro ao processar Excel: {str(e)}")
    
    def _encontrar_coluna(self, df: pd.DataFrame, possiveis_nomes: List[str]) -> Optional[str]:
        """
        Encontra uma coluna no DataFrame baseado em possíveis nomes
        """
        colunas_lower = [col.lower() for col in df.columns]
        
        for nome in possiveis_nomes:
            for idx, col_lower in enumerate(colunas_lower):
                if nome.lower() in col_lower:
                    return df.columns[idx]
        
        return None
    
    def normalizar_classes(self, df: pd.DataFrame, coluna_classe: str) -> pd.DataFrame:
        """
        Normaliza os valores da coluna de classe, extraindo apenas números
        Remove zeros à esquerda e converte para string sem zeros
        Ex: "03" -> "3", "08" -> "8"
        """
        df = df.copy()
        
        def extrair_classe(valor):
            if pd.isna(valor):
                return None
            valor_str = str(valor).strip()
            # Ignorar valores inválidos
            if valor_str.lower() in ['n/a', 'nan', 'none', '']:
                return None
            # Se for apenas dígitos, remover zeros à esquerda
            if valor_str.isdigit():
                return str(int(valor_str))  # Remove zeros à esquerda: "03" -> "3", "08" -> "8"
            # Extrair número da classe (ex: "Classe 5" -> "5", "Cl. 42" -> "42")
            match = re.search(r'\d+', valor_str)
            if match:
                num = int(match.group())
                if 1 <= num <= 45:
                    return str(num)  # Sem zeros à esquerda
            return valor_str
        
        df[coluna_classe] = df[coluna_classe].apply(extrair_classe)
        
        return df
    
    def agrupar_por_classe(self, df: pd.DataFrame, coluna_classe: str) -> Dict[str, pd.DataFrame]:
        """
        Agrupa processos por classe
        
        Returns:
            Dicionário com classe como chave e DataFrame como valor
        """
        grupos = {}
        
        for classe in df[coluna_classe].unique():
            if pd.notna(classe):
                grupos[str(classe)] = df[df[coluna_classe] == classe].copy()
        
        return grupos
    
    def obter_estatisticas_classe(self, df: pd.DataFrame, coluna_classe: str) -> pd.DataFrame:
        """
        Retorna estatísticas por classe
        """
        stats = df.groupby(coluna_classe).agg({
            coluna_classe: 'count'
        }).rename(columns={coluna_classe: 'quantidade'}).sort_index()
        
        return stats
    
    def filtrar_por_classes(self, df: pd.DataFrame, classes_desejadas: List[str], coluna_classe: str = 'classe') -> pd.DataFrame:
        """
        Filtra DataFrame por classes desejadas
        
        Args:
            df: DataFrame com processos
            classes_desejadas: Lista de classes para filtrar (ex: ["3", "8", "14"])
            coluna_classe: Nome da coluna de classe (padrão: 'classe')
            
        Returns:
            DataFrame filtrado
        """
        if not classes_desejadas or len(classes_desejadas) == 0 or coluna_classe not in df.columns:
            return df
        
        if df.empty:
            return df
        
        # Normalizar classes desejadas (remover zeros à esquerda e converter para string)
        classes_normalizadas = []
        for c in classes_desejadas:
            if c and str(c).strip():
                c_str = str(c).strip()
                # Tentar extrair número se for dígito
                if c_str.isdigit():
                    classes_normalizadas.append(str(int(c_str)))
                else:
                    # Tentar extrair número de strings como "Classe 5" ou "Cl. 42"
                    match = re.search(r'\d+', c_str)
                    if match:
                        num = int(match.group())
                        if 1 <= num <= 45:
                            classes_normalizadas.append(str(num))
                    else:
                        classes_normalizadas.append(c_str)
        
        if not classes_normalizadas:
            return df
        
        # Normalizar valores da coluna de classe no DataFrame
        df_filtrado = df.copy()
        
        def normalizar_valor_classe(valor):
            """Normaliza um valor de classe para comparação"""
            if pd.isna(valor):
                return None
            valor_str = str(valor).strip()
            # Ignorar valores como "N/A", "nan", etc.
            if valor_str.lower() in ['n/a', 'nan', 'none', '']:
                return None
            # Tentar extrair número
            if valor_str.isdigit():
                return str(int(valor_str))
            # Tentar extrair número de strings como "Classe 5"
            match = re.search(r'\d+', valor_str)
            if match:
                num = int(match.group())
                if 1 <= num <= 45:
                    return str(num)
            return valor_str
        
        df_filtrado[coluna_classe + '_normalizada'] = df_filtrado[coluna_classe].apply(normalizar_valor_classe)
        
        # Filtrar usando a coluna normalizada
        mask = df_filtrado[coluna_classe + '_normalizada'].isin(classes_normalizadas)
        df_resultado = df_filtrado[mask].copy()
        
        # Remover coluna temporária
        if coluna_classe + '_normalizada' in df_resultado.columns:
            df_resultado = df_resultado.drop(columns=[coluna_classe + '_normalizada'])
        
        return df_resultado
    
    def filtrar_por_palavras_chave(self, df: pd.DataFrame, palavras_chave: List[str], coluna_especificacao: str = 'especificacao') -> pd.DataFrame:
        """
        Filtra DataFrame por palavras-chave nas especificações
        
        Args:
            df: DataFrame com processos
            palavras_chave: Lista de palavras-chave para buscar
            coluna_especificacao: Nome da coluna de especificação (padrão: 'especificacao')
            
        Returns:
            DataFrame filtrado
        """
        if not palavras_chave or len(palavras_chave) == 0 or coluna_especificacao not in df.columns:
            return df
        
        if df.empty:
            return df
        
        # Converter palavras-chave para minúsculas e criar regex
        palavras_lower = [p.lower().strip() for p in palavras_chave if p and str(p).strip()]
        
        if not palavras_lower:
            return df
        
        # Criar padrão regex (qualquer uma das palavras)
        # Usar word boundaries para busca mais precisa
        padrao = '|'.join([re.escape(p) for p in palavras_lower])
        
        # Filtrar - tratar valores NaN e vazios
        df_filtrado = df.copy()
        
        # Preencher NaN com string vazia para evitar erros
        df_filtrado[coluna_especificacao] = df_filtrado[coluna_especificacao].fillna('')
        
        # Converter para string e buscar (case insensitive)
        mask = df_filtrado[coluna_especificacao].astype(str).str.lower().str.contains(
            padrao,
            case=False,
            na=False,
            regex=True
        )
        
        return df_filtrado[mask]
    
    def filtrar_processos(self, df: pd.DataFrame, classes_desejadas: List[str] = None, 
                         palavras_chave: List[str] = None, 
                         coluna_classe: str = 'classe',
                         coluna_especificacao: str = 'especificacao') -> pd.DataFrame:
        """
        Filtra processos por classes e/ou palavras-chave
        
        Args:
            df: DataFrame com processos
            classes_desejadas: Lista de classes para filtrar (opcional)
            palavras_chave: Lista de palavras-chave para filtrar (opcional)
            coluna_classe: Nome da coluna de classe (padrão: 'classe')
            coluna_especificacao: Nome da coluna de especificação (padrão: 'especificacao')
            
        Returns:
            DataFrame filtrado
        """
        if df.empty:
            return df
        
        df_filtrado = df.copy()
        
        # Filtrar por classes (apenas se a lista não estiver vazia)
        if classes_desejadas and len(classes_desejadas) > 0:
            df_filtrado = self.filtrar_por_classes(df_filtrado, classes_desejadas, coluna_classe)
            # Se após filtrar por classes não sobrou nada, retornar vazio
            if df_filtrado.empty:
                return df_filtrado
        
        # Filtrar por palavras-chave (apenas se a lista não estiver vazia)
        if palavras_chave and len(palavras_chave) > 0:
            df_filtrado = self.filtrar_por_palavras_chave(df_filtrado, palavras_chave, coluna_especificacao)
        
        return df_filtrado

