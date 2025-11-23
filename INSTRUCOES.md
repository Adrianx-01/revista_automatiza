# Instruções de Uso - Sistema de Processos Concedidos da Revista INPI

## 🚀 Como Iniciar

1. **Ative o ambiente virtual** (se estiver usando):
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. **Instale as dependências** (se ainda não instalou):
```bash
pip install -r requirements.txt
```

3. **Execute o aplicativo Streamlit**:
```bash
streamlit run app.py
```

O sistema abrirá automaticamente no navegador em `http://localhost:8501`

## 📥 Como Usar

### 1. Upload de Arquivo XML

- Clique em **"Selecione o arquivo"** na barra lateral
- Selecione um arquivo XML da Revista do INPI (ex: `2617.xml`)
- Clique em **"🔄 Processar Arquivo"**

### 2. Identificação de Processos Concedidos

O sistema identifica automaticamente processos concedidos procurando pelo despacho:
```xml
<despacho codigo="IPAS158" nome="Concessão de registro"/>
```

### 3. Extração de Dados

Para cada processo concedido, o sistema extrai:
- **Número do processo**
- **Marca**
- **Classe(s) Nice** (apenas as classes com status "Deferido")
- **Titular**
- **Procurador** (se disponível)
- **Data de concessão** (se disponível)
- **Especificação e tradução** de cada classe

### 4. Visualização dos Dados

Após o processamento, você pode:
- **Filtrar por classe**: Selecione uma classe específica ou "Todas"
- **Filtrar por marca**: Selecione uma marca específica ou "Todas"
- **Ver estatísticas**: Total de processos, classes, etc.
- **Visualizar gráficos**: Gráficos de barras e pizza por classe
- **Explorar detalhes**: Expanda cada classe para ver os processos

### 5. Exportação

- **Download CSV**: Baixe os dados filtrados em formato CSV
- **Download Excel**: Baixe os dados filtrados em formato Excel

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
2. Para cada processo, são extraídas **todas as classes com status "Deferido"**
3. Um mesmo processo pode aparecer em múltiplas linhas (uma por classe deferida)
4. O sistema normaliza automaticamente os códigos de classe (remove texto, mantém apenas o número)

## 🐛 Solução de Problemas

### Nenhum processo encontrado
- Verifique se o arquivo XML contém processos com despacho `IPAS158`
- Confirme que o arquivo não está corrompido

### Erro ao processar XML
- Verifique se o arquivo segue a estrutura esperada
- Confirme que o encoding do arquivo é UTF-8

### Classes não aparecem corretamente
- O sistema normaliza automaticamente os códigos de classe
- Apenas classes com status "Deferido" são incluídas

## 📝 Notas Técnicas

- O processamento de XML é otimizado para a estrutura oficial da Revista do INPI
- Classes indefinidas, excluídas ou em outros status são ignoradas
- O sistema agrupa processos por classe para facilitar a análise

