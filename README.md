# 💎 Barzinho – Sistema de Controle de Clientes e Produtos 💎

Este projeto é uma aplicação GUI em Python (Tkinter) que gerencia clientes, produtos, depósitos, retiradas e transações em um ambiente simples, pensado para uso em uma lanchonete ou eventos similares.

O sistema permite cadastrar clientes, associar valores a eles, registrar compras de produtos e manter um histórico de todas as transações em arquivos .csv.

⸻

## 🚀 Funcionalidades

• Cadastro de Clientes

• Adição de novos clientes ao sistema.

•	Armazenamento automático em names.csv e client_data.csv.

•	Gerenciamento de Valores

•	Depósito de saldo para um cliente.

•	Retirada de valores.

•	Compra de produtos (desconto automático no saldo).

•	Prevenção contra saldo negativo.

•	Histórico de Transações

•	Registro automático de todas as movimentações em transacoes.csv (inclui hora e tipo da operação).

•	Busca de Clientes

•	Pesquisa por nomes (com suporte a nomes com acentos).

•	Interface Gráfica (Tkinter)

•	Tela inicial com lista de clientes.

•	Tela individual de cliente mostrando saldo e opções de depósito, retirada e produtos.

•	Botões de produtos gerados dinamicamente a partir de products.csv.



## 📂 Estrutura de Arquivos

O sistema utiliza alguns arquivos .csv para persistência de dados:

•	names.csv → Lista de clientes.

•	products.csv → Lista de produtos e seus valores. (Formato: Produto,Preço)

•	client_data.csv → Valores atuais de cada cliente.

•	transacoes.csv → Histórico de todas as transações.

Exemplo de products.csv:
```
Refrigerante,5.00
Água,3.00
```

## 🛠️ Tecnologias Utilizadas

•	Python 3.x

•	Tkinter → Interface gráfica.

•	CSV → Persistência de dados.

•	OS / Datetime / Unicodedata → Utilitários para manipulação de arquivos, datas e acentos.



▶️ Como Executar
1.	Clone o repositório:

`git clone https://github.com/seu-usuario/barzinho.git
cd barzinho`

2.	Certifique-se de que possui o Python 3 instalado.
	
3.	Prepare os arquivos iniciais:
	•	Crie um arquivo products.csv com os produtos e valores.
	•	Crie um arquivo names.csv com a lista de clientes (um por linha).
	
4.	Execute o programa:

`python main.py`

## 📸 Interface
•	Tela inicial:
	
    •	Lista de clientes.

	   •	Botões de busca, adicionar pessoa e sair.

•	Tela do cliente:

	  •	Saldo atual.

  	•	Campo para depósito e retirada.

  	•	Botões para cada produto (com nome e preço).


## 🔮 Possíveis Melhorias Futuras

•	Exportar relatórios em PDF/Excel.

•	Criar um painel administrativo para editar/remover produtos.

• Adicionar autenticação para maior segurança.

•	Migrar dados para um banco de dados (SQLite ou PostgreSQL).

Criar um exe: `pyinstaller --onefile --noconsole arquivo.py`


