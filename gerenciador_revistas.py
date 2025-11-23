"""
Módulo para gerenciar upload e download de revistas no Supabase
"""
import streamlit as st
import xml.etree.ElementTree as ET
from database_supabase import DatabaseSupabase
from typing import Dict, Optional, List


class GerenciadorRevistas:
    """Classe para gerenciar operações com revistas no Supabase"""
    
    def __init__(self, db: DatabaseSupabase):
        """
        Inicializa o gerenciador de revistas
        
        Args:
            db: Instância de DatabaseSupabase
        """
        self.db = db
    
    def upload_revista(self, arquivo_revista) -> Dict:
        """
        Faz upload de uma revista para o storage e registra o número na tabela revista
        
        Args:
            arquivo_revista: Arquivo uploader do Streamlit
            
        Returns:
            Dicionário com resultado da operação
        """
        if arquivo_revista is None:
            return {'sucesso': False, 'erro': 'Nenhum arquivo selecionado'}
        
        try:
            # Extrair número da revista do nome do arquivo ou do conteúdo
            nome_arquivo = arquivo_revista.name
            numero_revista = None
            
            # Tentar extrair número da revista do XML
            try:
                arquivo_revista.seek(0)
                tree = ET.parse(arquivo_revista)
                root = tree.getroot()
                if root.tag.lower() == 'revista':
                    numero_revista = root.get('numero', '')
                    if numero_revista:
                        nome_arquivo = f"revista_{numero_revista}.xml"
                arquivo_revista.seek(0)
            except:
                pass
            
            # Fazer upload para o storage
            arquivo_bytes = arquivo_revista.read()
            resultado = self.db.upload_revista(arquivo_bytes, nome_arquivo)
            
            # Se o upload foi bem-sucedido e temos o número da revista, salvar na tabela revista
            if resultado.get('sucesso') and numero_revista:
                try:
                    resultado_revista = self.db.salvar_numero_revista(numero_revista)
                    # Não falhar o upload se o registro na tabela falhar (pode ser duplicata ou RLS)
                    if not resultado_revista.get('sucesso'):
                        # Adicionar aviso ao resultado
                        erro_revista = resultado_revista.get('erro', 'Erro desconhecido')
                        resultado['aviso'] = f"Número da revista {numero_revista} não foi registrado na tabela: {erro_revista}"
                        # Log do erro
                        print(f"Aviso: Não foi possível registrar número da revista {numero_revista}: {erro_revista}")
                    else:
                        resultado['mensagem_revista'] = resultado_revista.get('mensagem', f'Revista {numero_revista} registrada')
                except Exception as e:
                    # Não falhar o upload se houver erro ao salvar número
                    erro_msg = str(e)
                    resultado['aviso'] = f"Erro ao salvar número da revista {numero_revista}: {erro_msg}"
                    print(f"Aviso: Erro ao salvar número da revista {numero_revista}: {erro_msg}")
            
            return resultado
        
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}
    
    def listar_revistas_disponiveis(self) -> List[str]:
        """
        Lista todas as revistas disponíveis (storage + registradas)
        
        Returns:
            Lista de nomes de arquivos de revistas
        """
        try:
            # Listar revistas do storage
            revistas_storage = self.db.listar_revistas()
            # Listar revistas registradas na tabela
            revistas_registradas = self.db.listar_revistas_registradas()
            
            # Combinar e ordenar revistas
            todas_revistas = []
            if revistas_storage:
                todas_revistas.extend(revistas_storage)
            if revistas_registradas:
                # Adicionar revistas registradas que não estão no storage
                for r in revistas_registradas:
                    nome_arquivo = f"revista_{r}.xml"
                    if nome_arquivo not in todas_revistas and r not in todas_revistas:
                        todas_revistas.append(nome_arquivo)
            
            return sorted(todas_revistas, reverse=True)
        
        except Exception as e:
            st.error(f"Erro ao listar revistas: {str(e)}")
            return []
    
    def download_revista(self, nome_arquivo: str) -> Optional[bytes]:
        """
        Faz download de uma revista
        
        Args:
            nome_arquivo: Nome do arquivo para baixar
            
        Returns:
            Bytes do arquivo ou None em caso de erro
        """
        try:
            return self.db.download_revista(nome_arquivo)
        except Exception as e:
            st.error(f"Erro ao baixar revista: {str(e)}")
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
            return self.db.deletar_revista(nome_arquivo)
        except Exception as e:
            st.error(f"Erro ao deletar revista: {str(e)}")
            return False
    
    def renderizar_upload(self):
        """Renderiza a interface de upload de revista"""
        arquivos_revista = st.file_uploader(
            "Selecione um ou mais arquivos XML da revista",
            type=['xml'],
            accept_multiple_files=True,
            key="upload_revista"
        )
        
        if arquivos_revista is not None and len(arquivos_revista) > 0:
            if st.button("📤 Enviar para Storage", type="primary", key="upload_storage"):
                sucessos = 0
                erros = []
                avisos = []
                
                with st.spinner(f"Enviando {len(arquivos_revista)} revista(s) para o storage..."):
                    for arquivo_revista in arquivos_revista:
                        resultado = self.upload_revista(arquivo_revista)
                        
                        if resultado['sucesso']:
                            sucessos += 1
                            # Verificar se há avisos sobre registro do número da revista
                            if 'aviso' in resultado:
                                avisos.append(f"{arquivo_revista.name}: {resultado['aviso']}")
                        else:
                            erros.append(f"{arquivo_revista.name}: {resultado.get('erro', 'Erro desconhecido')}")
                
                if sucessos > 0:
                    st.success(f"✅ {sucessos} revista(s) enviada(s) para o storage com sucesso!")
                if avisos:
                    st.warning(f"⚠️ {len(avisos)} aviso(s):")
                    for aviso in avisos:
                        st.text(f"  - {aviso}")
                if erros:
                    st.error(f"❌ {len(erros)} erro(s) ao enviar:")
                    for erro in erros:
                        st.text(f"  - {erro}")
                
                if sucessos > 0:
                    st.rerun()
    
    def renderizar_download(self):
        """Renderiza a interface de download de revista"""
        st.subheader("📥 Download de Revistas")
        
        if st.button("🔄 Atualizar Lista", key="refresh_revistas"):
            st.rerun()
        
        revistas = self.listar_revistas_disponiveis()
        
        if revistas:
            st.info(f"**{len(revistas)}** revista(s) disponível(eis)")
            
            # Mostrar revistas em uma lista selecionável
            revista_selecionada = st.selectbox(
                "Selecione uma revista para baixar:",
                options=revistas,
                key="select_revista"
            )
            
            col_download, col_delete = st.columns(2)
            
            with col_download:
                if st.button("⬇️ Download", key="download_revista", type="primary"):
                    with st.spinner("Baixando revista..."):
                        arquivo_bytes = self.download_revista(revista_selecionada)
                        if arquivo_bytes:
                            st.download_button(
                                label="💾 Baixar Arquivo XML",
                                data=arquivo_bytes,
                                file_name=revista_selecionada,
                                mime="application/xml",
                                key="download_file"
                            )
                            st.success("✅ Arquivo pronto para download!")
                        else:
                            st.error("❌ Erro ao baixar arquivo")
            
            with col_delete:
                if st.button("🗑️ Deletar do Storage", key="delete_revista", type="secondary"):
                    if self.deletar_revista(revista_selecionada):
                        st.success(f"✅ Revista {revista_selecionada} deletada do storage!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao deletar revista")
        else:
            st.info("Nenhuma revista encontrada no storage.")

