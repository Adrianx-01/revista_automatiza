# Sistema de Processos Concedidos da Revista INPI

Sistema desenvolvido em Python e Streamlit para processar e visualizar processos concedidos da Revista da Propriedade Industrial (RPI) do INPI, organizados por classes de marcas. Utiliza autenticação via Supabase e armazenamento em nuvem.

## 🚀 Funcionalidades

- 🔐 Autenticação via Supabase (login com email e senha)
- 📥 Upload de revistas XML para o storage do Supabase
- 🔍 Filtro automático de processos concedidos (despacho IPAS158)
- 🎯 Filtros por classes Nice e palavras-chave na importação
- 💾 Integração com Supabase (banco de dados + storage)
- 📊 Consulta de dados por classes selecionadas (carregamento sob demanda)
- ✅ Marcação de processos como verificados
- 📋 Visualização e filtros por classe, marca e revista

## 📋 Requisitos

- Python 3.8 ou superior
- pip
- Conta no Supabase (obrigatório)

## 🔧 Instalação

1. Clone ou baixe este repositório

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
   - **Windows (PowerShell)**: `.\venv\Scripts\Activate.ps1`
   - **Windows (CMD)**: `venv\Scripts\activate.bat`
   - **Linux/Mac**: `source venv/bin/activate`

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Configure o Supabase:
   - Crie um projeto no [Supabase](https://supabase.com)
   - Crie um arquivo `.env` na raiz do projeto
   - Adicione: `SUPABASE_URL` e `SUPABASE_KEY` (obtidos em Settings > API)
   - Crie as tabelas `dados_marcas` e `revista`, o bucket de storage `revista` e configure as políticas RLS

## ▶️ Como Executar

```bash
streamlit run app.py
```

O sistema abrirá em `http://localhost:8501`

## 📖 Como Usar

1. **Login**: Acesse o sistema e faça login com suas credenciais Supabase
2. **Gerenciar Revistas**:
   - Configure classes Nice e palavras-chave para filtro
   - Faça upload de arquivos XML para o storage
   - Baixe revistas do storage e processe com os filtros configurados (os dados são salvos no banco)
3. **Consultar Dados**:
   - Selecione as classes Nice desejadas
   - Clique em "Carregar Dados" para buscar apenas os processos dessas classes
   - Aplique filtros por marca e revista
   - Marque processos como verificados

## 📊 Estrutura de Dados

O sistema espera arquivos da Revista do INPI que contenham pelo menos:
- Número do processo
- Marca
- Classe (Classificação de Nice)
- Status/Situação
- Titular/Requerente (opcional)
- Data de concessão (opcional)

## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Interface web interativa
- **Pandas**: Manipulação e análise de dados
- **Plotly**: Gráficos interativos
- **lxml**: Processamento de XML
- **openpyxl**: Leitura de arquivos Excel
- **Supabase**: Banco de dados PostgreSQL em nuvem
- **python-dotenv**: Gerenciamento de variáveis de ambiente

## 📝 Notas

- O sistema filtra automaticamente processos com status "concedido" (IPAS158)
- As classes seguem a Classificação Internacional de Nice (1-45)
- Na consulta, **nenhum dado é carregado automaticamente** – selecione as classes e clique em "Carregar Dados"

## 🔗 Links Úteis

- [INPI - Revista da Propriedade Industrial](https://www.gov.br/inpi/pt-br/servicos/marcas/revista-da-propriedade-industrial)
- [Classificação Internacional de Nice](https://www.gov.br/inpi/pt-br/assuntos/marcas/classificacao)
- [Documentação Streamlit](https://docs.streamlit.io/)

## 📄 Licença

Este projeto é de uso educacional e para fins de automação de processos internos.

