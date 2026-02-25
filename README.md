# 💎 Barzinho – Sistema de Controle de Clientes e Produtos 💎

Este projeto é uma aplicação GUI em Python (Tkinter) que gerencia clientes, produtos, depósitos, retiradas e transações em um ambiente simples, pensado para uso em uma lanchonete ou eventos similares.

O sistema permite cadastrar clientes, associar valores a eles, registrar compras de produtos, manter um histórico de todas as transações em arquivos .csv e **gerar relatórios completos em Excel (.xlsx)**.

⸻

## 🚀 Funcionalidades

• **Cadastro de Clientes**

  • Adição de novos clientes ao sistema.

  • Armazenamento automático em names.csv e client_data.csv.

• **Gerenciamento de Produtos**

  • Adicionar, editar e remover produtos.

  • Definição de preços personalizados.

  • Armazenamento em products.csv.

• **Sistema de Promoções**

  • Criação de promoções com período de validade (data início e fim).

  • Dois tipos de promoção:
    - **Desconto**: Define um preço promocional para o produto.
    - **Leve X Pague Y**: Ex: Leve 3 Pague 2 (o 3º produto sai grátis).

  • Gerenciamento completo: adicionar, visualizar e remover promoções.

  • Aplicação automática durante as compras (dentro do período válido).

• **Gerenciamento de Valores**

  • Depósito de saldo para um cliente.

  • Retirada de valores.

  • Compra de produtos (desconto automático no saldo).

  • Indicação visual de produtos em promoção durante a compra.

• **Histórico de Transações**

  • Registro automático de todas as movimentações em transacoes.csv (inclui hora e tipo da operação).

  • Visualização de histórico por cliente.

• **Busca de Clientes**

  • Pesquisa por nomes (com suporte a nomes com acentos).

• **Geração de Relatórios Excel**

  • Relatório completo exportado em formato .xlsx com múltiplas abas:
    - **Relatório Geral**: Resumo financeiro (depósitos, vendas, retiradas, saldo final) e tabela de saldo por cliente
    - **Análise Dinâmica**: Tabela filtrada de vendas por data e produto com gráfico interativo
    - **Todas as Transações**: Histórico completo de transações com filtros automáticos
  
  • Formatação profissional com cores, fontes, alinhamentos e filtros interativos.
  
  • Gráficos de barras para visualização de dados de vendas.

• **Reset do Sistema**

  • Função de reset completo que apaga todos os dados.

  • Confirmação de segurança (necessário digitar frase específica).

  • Recria automaticamente os arquivos names.csv e products.csv vazios.

  • Interface visual com botão vermelho de destaque.

• **Interface Gráfica (Tkinter)**

  • Tela inicial com lista de clientes e menu dropdown otimizado.

  • Menu com acesso rápido a todas as funcionalidades.

  • Tela individual de cliente mostrando saldo e opções de depósito, retirada e produtos.

  • Botões de produtos gerados dinamicamente a partir de products.csv.

  • Saldo em vermelho quando negativo para melhor visualização.



## 📂 Estrutura de Arquivos

O sistema utiliza alguns arquivos .csv para persistência de dados:

• **names.csv** → Lista de clientes.

• **products.csv** → Lista de produtos e seus valores. (Formato: Produto,Preço)

• **promotions.csv** → Promoções ativas com período de validade. (Formato: Produto,Tipo,Valor1,Valor2,DataInicio,DataFim)

• **client_data.csv** → Valores atuais de cada cliente.

• **transacoes.csv** → Histórico de todas as transações.

• **error_log.txt** → Log de erros do sistema (gerado automaticamente em caso de falhas).

• **relatorio do barzinho.xlsx** → Relatório Excel gerado pelo sistema (criado ao clicar em "Emitir Relatório").

Exemplo de products.csv:
```
Refrigerante,5.00
Água,3.00
```

Exemplo de promotions.csv:
```
Produto,Tipo,Valor1,Valor2,DataInicio,DataFim
Refrigerante,desconto,4.00,,2026-02-01,2026-02-28
Cerveja,compre_leve,3,2,2026-02-15,2026-02-29
```

## 🛠️ Tecnologias Utilizadas

• **Python 3.x**

• **Tkinter** → Interface gráfica.

• **CSV** → Persistência de dados.

• **openpyxl** → Geração de relatórios Excel com formatação e gráficos.

• **OS / Datetime / Unicodedata** → Utilitários para manipulação de arquivos, datas e acentos.

• **Traceback** → Sistema de log de erros.



## ▶️ Como Executar

1. Clone o repositório:

```bash
git clone https://github.com/Luis0922/Sistema-Vendas-Barzinho.git
cd Sistema-Vendas-Barzinho
```

2. Certifique-se de que possui o Python 3 instalado.

3. Entrar na venv
```bash
.\venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Prepare os arquivos iniciais:
   • Crie um arquivo products.csv com os produtos e valores.
   • Crie um arquivo names.csv com a lista de clientes (um por linha).

5. Execute o programa:

```bash
python main.py
```

## 📸 Interface

• **Tela inicial:**

  • Lista de clientes.

  • Botões de busca e sair.
  
  • Menu dropdown (☰) no canto superior direito com acesso a:
    - Emitir Relatório
    - Adicionar Pessoa
    - Gerenciar Produtos
    - Adicionar Promoção
    - Gerenciar Promoções
    - Resetar Aplicativo (com confirmação de segurança)

• **Tela do cliente:**

  • Saldo atual (vermelho se negativo).

  • Campo para depósito e retirada.

  • Botões para cada produto (com nome e preço).
  
  • Indicação visual de promoções aplicadas.
  
  • Botão de histórico para visualizar transações passadas.

• **Gerenciamento de Produtos:**

  • Interface para adicionar novos produtos com preço.
  
  • Editar preços de produtos existentes.
  
  • Remover produtos do sistema.

• **Sistema de Promoções:**

  • Adicionar promoções com tipo (desconto ou compre/leve).
  
  • Definir período de validade (datas de início e fim).
  
  • Visualizar e remover promoções ativas.

• **Reset do Sistema:**

  • Janela de confirmação com campo de texto.
  
  • Requer digitação da frase exata: "ESTOU CIENTE QUE IREI APAGAR TUDO".
  
  • Botão vermelho de destaque "APAGAR TUDO".
  
  • Recria arquivos essenciais automaticamente após reset.


## 📊 Relatórios

O sistema gera relatórios completos em Excel com as seguintes características:

• **Aba "Relatório Geral":**
  - Resumo financeiro com totais de depósitos, vendas e retiradas
  - Cálculo automático do saldo final
  - Tabela detalhada de saldo por cliente (depositou, gastou, retirou, saldo atual)
  - Destaque visual para saldos negativos em vermelho

• **Aba "Análise Dinâmica":**
  - Tabela de vendas organizada por data e produto
  - Filtros interativos para análise personalizada
  - Gráfico de barras mostrando vendas por data e produto

• **Aba "Todas as Transações":**
  - Histórico completo de todas as movimentações
  - Filtros automáticos por cliente, produto/tipo, valor e data
  - Cores alternadas para melhor leitura

## 🔮 Possíveis Melhorias Futuras

• Adicionar mais tipos de gráficos nos relatórios (pizza, linha).

• Adicionar autenticação para maior segurança.

• Migrar dados para um banco de dados (SQLite ou PostgreSQL).

• Exportar relatórios em PDF.

• Sistema de backup automático dos dados.

• Histórico de alterações de preços de produtos.

• Relatório específico de promoções (efetividade, economia gerada).

Criar um exe: 
```bash
pyinstaller --onefile --noconsole main.py
```


