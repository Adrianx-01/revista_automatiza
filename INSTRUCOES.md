# Instruções de Uso - Sistema de Processos Concedidos da Revista INPI

## 🚀 Como Iniciar

1. **Ative o ambiente virtual**:
```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Execute o aplicativo**:
```bash
streamlit run app.py
```

O sistema abrirá em `http://localhost:8501`

---

## 🔐 Login

O sistema exige autenticação via Supabase. Use o email e senha da sua conta no Supabase para acessar.

---

## 📚 Gerenciar Revistas

### 1. Configurar Filtros

- **Classes desejadas**: Selecione as classes Nice (1-45) que deseja importar
- **Palavras-chave**: Selecione ou adicione palavras para filtrar nas especificações
- Esses filtros serão aplicados ao processar as revistas

### 2. Upload de Revistas

- Selecione um ou mais arquivos XML da Revista do INPI
- Clique em **"📤 Enviar para Storage"** para enviar ao Supabase
- Os arquivos ficam disponíveis no bucket para download e processamento

### 3. Download e Processar

- Na lista de revistas, selecione uma ou mais para processar
- Clique em **"⬇️ Baixar e Processar"**
- O sistema baixa do storage, aplica os filtros (classes + palavras-chave) e salva os processos na tabela `dados_marcas`

---

## 🔍 Consultar Dados

### 1. Selecionar Classes

- **Selecione as classes Nice** (1-45) das quais deseja carregar os processos
- Nenhum dado é carregado automaticamente

### 2. Carregar Dados

- Clique em **"📥 Carregar Dados"** para buscar apenas os processos das classes selecionadas
- O sistema busca diretamente no Supabase com filtro por classes

### 3. Filtrar e Visualizar

- **Filtrar por classe, marca ou revista** nos resultados
- Os processos são separados em "Não Verificados" e "Verificados"

### 4. Marcar como Verificado

- Marque os checkboxes dos processos desejados na tabela de não verificados
- Clique em **"✅ Marcar como Verificado"**
- Os processos passam para a seção de verificados e a alteração é salva no banco

### 5. Limpar

- Use **"🔄 Limpar e Recarregar"** para zerar os dados carregados e começar uma nova consulta

---

## 📄 Processamento de Arquivos

O sistema identifica processos concedidos pelo despacho:
```xml
<despacho codigo="IPAS158" nome="Concessão de registro"/>
```

Para cada processo, extrai: número, marca, classe(s) Nice (apenas deferidas), titular, procurador, data de concessão, especificação.

## 📊 Estrutura dos Dados XML do INPI

O sistema processa arquivos XML com a seguinte estrutura:

```xml
<revista numero="2617" data="02/03/2021">
  <processo numero="826530010" data-concessao="02/03/2021">
    <despachos>
      <despacho codigo="IPAS158" nome="Concessão de registro"/>
    </despachos>
    <titulares>
      <titular nome-razao-social="NOME DA EMPRESA" pais="BR"/>
    </titulares>
    <marca apresentacao="Nominativa">
      <nome>NOME DA MARCA</nome>
    </marca>
    <lista-classe-nice>
      <classe-nice codigo="43">
        <especificacao>...</especificacao>
        <traducao-especificacao>...</traducao-especificacao>
        <status>Deferido</status>
      </classe-nice>
    </lista-classe-nice>
  </processo>
</revista>
```

## 🔍 Classificação de Nice

- **Classes 1-34**: Produtos
- **Classes 35-45**: Serviços

## ⚠️ Observações Importantes

1. O sistema processa **apenas processos com despacho IPAS158** (Concessão de registro)
2. Na consulta, **nenhum dado é carregado automaticamente** – é obrigatório selecionar classes e clicar em "Carregar Dados"
3. Os dados são buscados diretamente do Supabase, filtrados pelas classes escolhidas
4. Um mesmo processo pode aparecer em múltiplas linhas (uma por classe deferida)

## 🐛 Solução de Problemas

### Supabase não configurado
- Verifique se o arquivo `.env` existe na raiz com `SUPABASE_URL` e `SUPABASE_KEY`
- Confira as credenciais em Settings > API do projeto Supabase

### Erro ao processar XML
- Verifique se o arquivo segue a estrutura esperada da Revista do INPI
- Confirme que o encoding é UTF-8

### Erro de RLS (Row Level Security)
- Crie políticas de INSERT e SELECT para as tabelas `dados_marcas` e `revista`
- Verifique se o usuário autenticado tem permissão

### Nenhum processo encontrado na consulta
- Selecione pelo menos uma classe
- Confirme que há dados salvos para as classes escolhidas

