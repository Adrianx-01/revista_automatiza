# Sistema de Processos Concedidos da Revista INPI

Sistema desenvolvido em Python e Streamlit para processar e visualizar processos concedidos da Revista da Propriedade Industrial (RPI) do INPI, organizados por classes de marcas.

## 🚀 Funcionalidades

- 📥 Upload de arquivos da Revista do INPI (XML, CSV, XLSX)
- 🔍 Filtro automático de processos concedidos (despacho IPAS158)
- 💾 Integração com Supabase para armazenamento de dados
- 📊 Visualização por classes de marcas
- 📈 Gráficos e estatísticas interativas
- 🔍 Consulta de dados salvos no Supabase
- 📥 Exportação de dados filtrados

## 📋 Requisitos

- Python 3.8 ou superior
- pip
- Conta no Supabase (opcional, mas recomendado)

## 🔧 Instalação

1. Clone ou baixe este repositório

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Configure o Supabase (opcional):
   - Crie um projeto no [Supabase](https://supabase.com)
   - Copie o arquivo `.env.example` para `.env`
   - Preencha `SUPABASE_URL` e `SUPABASE_KEY` no arquivo `.env`
   - Execute o SQL em `supabase_setup.sql` no SQL Editor do Supabase para criar a tabela

## ▶️ Como Executar

Execute o seguinte comando:
```bash
streamlit run app.py
```

O sistema abrirá automaticamente no navegador em `http://localhost:8501`

## 📖 Como Usar

1. Faça o download da Revista do INPI no [site oficial](https://www.gov.br/inpi/pt-br/servicos/marcas/revista-da-propriedade-industrial)
2. Faça upload do arquivo na barra lateral (XML, CSV ou XLSX)
3. Clique em "Processar Arquivo"
4. Visualize os dados filtrados por classe e marca
5. Exporte os resultados em CSV ou Excel

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

- O sistema filtra automaticamente processos com status "concedido"
- As classes seguem a Classificação Internacional de Nice (1-45)
- O formato XML pode variar - pode ser necessário ajustar o código de parsing conforme a estrutura do XML fornecido pelo INPI

## 🔗 Links Úteis

- [INPI - Revista da Propriedade Industrial](https://www.gov.br/inpi/pt-br/servicos/marcas/revista-da-propriedade-industrial)
- [Classificação Internacional de Nice](https://www.gov.br/inpi/pt-br/assuntos/marcas/classificacao)
- [Documentação Streamlit](https://docs.streamlit.io/)

## 📄 Licença

Este projeto é de uso educacional e para fins de automação de processos internos.

