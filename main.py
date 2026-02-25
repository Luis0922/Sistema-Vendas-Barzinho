from tkinter import *
from tkinter import messagebox
import csv
import os
import datetime
from tkinter import ttk
import unicodedata
import math
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font, Alignment, PatternFill
import traceback

login = Tk()
monitor_width = login.winfo_screenwidth()/2
monitor_height = login.winfo_screenheight()/2
form_width = 500
form_height = 500

def log_error(error_message, exception=None):
    """Registra erros em um arquivo de log"""
    with open("error_log.txt", "a", encoding='utf-8') as log_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"\n{'='*80}\n")
        log_file.write(f"[{timestamp}] ERRO: {error_message}\n")
        if exception:
            log_file.write(f"Tipo: {type(exception).__name__}\n")
            log_file.write(f"Mensagem: {str(exception)}\n")
            log_file.write(f"Traceback:\n{traceback.format_exc()}\n")
        log_file.write(f"{'='*80}\n")

def get_transactions():
    transactions = []
    if os.path.exists("transacoes.csv"):
        with open("transacoes.csv", "r", encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                transactions.append(row)
    return transactions

def get_names():
    names = []
    with open("names.csv", "r", encoding='UTF-8') as file:
        for name in file:
            names.append(name)
    return names

def get_products():
    products = {}
    with open("products.csv", "r", encoding='UTF-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                products[row[0]] = float(row[1])
    return products

def get_promotions():
    """Carrega promoções do arquivo promotions.csv"""
    promotions = {}
    if os.path.exists("promotions.csv"):
        with open("promotions.csv", "r", encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # Pular cabeçalho
            for row in reader:
                if row and len(row) >= 6:
                    produto = row[0]
                    tipo = row[1]  # 'compre_leve' ou 'desconto'
                    valor1 = row[2]  # quantidade leve OU desconto
                    valor2 = row[3]  # quantidade pague (ou vazio para desconto)
                    data_inicio = row[4]  # Data de início (YYYY-MM-DD)
                    data_fim = row[5]  # Data de fim (YYYY-MM-DD)
                    promotions[produto] = {
                        'tipo': tipo,
                        'valor1': valor1,
                        'valor2': valor2,
                        'data_inicio': data_inicio,
                        'data_fim': data_fim
                    }
    return promotions

def save_promotions(promotions):
    """Salva promoções no arquivo promotions.csv"""
    with open("promotions.csv", "w", newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Produto", "Tipo", "Valor1", "Valor2", "DataInicio", "DataFim"])
        for produto, promo in promotions.items():
            writer.writerow([produto, promo['tipo'], promo['valor1'], promo['valor2'], 
                           promo.get('data_inicio', ''), promo.get('data_fim', '')])

names = get_names()

def init_client_data():
    if os.path.exists("client_data.csv") == False:
        with open("client_data.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Nome", "Valor"])  # Cabeçalho
            for name in names:
                writer.writerow([name.replace('"', '').strip(), 0])

products = get_products()

client_values = {}

def save_client_data_csv():
    with open("client_data.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Nome", "Valor"]) 
        for name, value in client_values.items():
            writer.writerow([name.replace('"', '').strip(), value])

def open_product_screen(selected_client_name):
    product_screen = Toplevel(login)
    product_screen.title(f"{selected_client_name}")
    product_screen_width = form_width+(math.ceil(len(products) / 6)*100)
    product_screen.geometry(f"{product_screen_width}x{form_height+40}+{int(monitor_width-form_width/2)-200}+{int(monitor_height-form_height/2)-20}")

    # Label com o nome do cliente
    Label(product_screen, text=f"Cliente: {selected_client_name}", font=("Helvetica", 16)).pack(pady=10)

    exit_button = Button(product_screen, text="Voltar", bd='3', command=product_screen.destroy)
    exit_x = product_screen_width - exit_button.winfo_reqwidth() - 10
    exit_button.place(x=exit_x, y=10)

    historic_button = Button(product_screen, text="Historico", bd='3', command=lambda: client_historic(selected_client_name))
    historic_button.place(x=10, y=10)

    def add_value():
        try:
            added_value = float(valor_add_entry.get().replace(",", "."))
            if added_value <= 0:
                messagebox.showerror("Erro", "Digite um número maior que 0.")
                return
            if selected_client_name in client_values:
                client_values[selected_client_name] += added_value
            else:
                client_values[selected_client_name] = added_value
            
            agora = datetime.datetime.now()
            formated_hour = agora.strftime("%Y-%m-%d %H:%M:%S")
            with open("transacoes.csv", "a", newline="", encoding='utf-8') as file:
                writer = csv.writer(file)
                if os.stat("transacoes.csv").st_size == 0:
                    writer.writerow(["Pessoa", "Produto", "Valor", "Hora"])
                writer.writerow([selected_client_name.strip(), "DEPOSITOU", added_value, formated_hour])
            
            save_client_data_csv()
            saldo = client_values.get(selected_client_name, 0.0)
            if saldo < 0:
                valor_label.config(text=f"Valor total: R${saldo:.2f}", fg="red")
            else:
                valor_label.config(text=f"Valor total: R${saldo:.2f}", fg="black")
            valor_add_entry.delete(0, END)
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor numérico válido.")

    def sub_value():
        try:
            subbed_value = float(valor_sub_entry.get().replace(",", "."))
            if subbed_value <= 0:
                messagebox.showerror("Erro", "Digite um número maior que 0.")
                return
            if selected_client_name in client_values:
                client_values[selected_client_name] -= subbed_value
            else:
                client_values[selected_client_name] = -subbed_value
            
            agora = datetime.datetime.now()
            formated_hour = agora.strftime("%Y-%m-%d %H:%M:%S")
            with open("transacoes.csv", "a", newline="", encoding='utf-8') as file:
                writer = csv.writer(file)
                if os.stat("transacoes.csv").st_size == 0:
                    writer.writerow(["Pessoa", "Produto", "Valor", "Hora"])
                writer.writerow([selected_client_name.strip(), "RETIRAR", subbed_value, formated_hour])
            
            save_client_data_csv()
            saldo = client_values.get(selected_client_name, 0.0)
            if saldo < 0:
                valor_label.config(text=f"Valor total: R${saldo:.2f}", fg="red")
            else:
                valor_label.config(text=f"Valor total: R${saldo:.2f}", fg="black")
            valor_sub_entry.delete(0, END)
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor numérico válido.")

    status_message_label = Label(product_screen, text="", fg="red")
    status_message_label.pack()
    
    def deduct_product_amount(produto, valor_original):
        if selected_client_name not in client_values:
            client_values[selected_client_name] = 0
        
        # Verificar se há promoção ativa para este produto
        promotions = get_promotions()
        valor_final = valor_original
        mensagem_promo = ""
        
        if produto in promotions:
            promo = promotions[produto]
            
            # Verificar se a promoção está dentro do período válido
            hoje = datetime.datetime.now().date()
            promo_valida = True
            
            if promo.get('data_inicio'):
                try:
                    data_inicio = datetime.datetime.strptime(promo['data_inicio'], "%Y-%m-%d").date()
                    if hoje < data_inicio:
                        promo_valida = False
                except:
                    pass
            
            if promo.get('data_fim'):
                try:
                    data_fim = datetime.datetime.strptime(promo['data_fim'], "%Y-%m-%d").date()
                    if hoje > data_fim:
                        promo_valida = False
                except:
                    pass
            
            if promo_valida:
                if promo['tipo'] == 'desconto':
                    # Aplicar desconto no preço
                    valor_final = float(promo['valor1'])
                    desconto = valor_original - valor_final
                    mensagem_promo = f" (Promoção: R$ {desconto:.2f} de desconto)"
                
                elif promo['tipo'] == 'compre_leve':
                    # Promoção Leve X Pague Y (ex: Leve 3 Pague 2)
                    leve = int(promo['valor1'])  # Quantidade total que leva
                    pague = int(promo['valor2'])  # Quantidade que paga
                    
                    # Contar quantas vezes comprou este produto hoje
                    hoje_str = datetime.datetime.now().strftime("%Y-%m-%d")
                    transactions = get_transactions()
                    count_hoje = 0
                    
                    for transaction in transactions:
                        if len(transaction) >= 4:
                            if (transaction[0].strip() == selected_client_name.strip() and 
                                transaction[1].strip() == produto and 
                                transaction[3].startswith(hoje_str)):
                                count_hoje += 1
                    
                    # A cada 'leve' produtos, cobra apenas 'pague'
                    # Ex: Leve 3 Pague 2 = produtos 1 e 2 pagam, produto 3 é grátis
                    posicao_no_ciclo = (count_hoje % leve) + 1
                    
                    if posicao_no_ciclo <= pague:
                        # Cobra normalmente (ainda está dentro da quantidade que paga)
                        valor_final = valor_original
                        mensagem_promo = f" ({posicao_no_ciclo}/{leve} - Leve {leve} Pague {pague})"
                    else:
                        # Produto grátis! (já pagou os 'pague' e agora leva de graça)
                        valor_final = 0
                        mensagem_promo = f" (GRÁTIS! Leve {leve} Pague {pague})"
        
        client_values[selected_client_name] -= valor_final

        agora = datetime.datetime.now()
        hora_formatada = agora.strftime("%Y-%m-%d %H:%M:%S")

        with open("transacoes.csv", "a", newline="", encoding='utf-8') as file:
            writer = csv.writer(file)
            if os.stat("transacoes.csv").st_size == 0:
                writer.writerow(["Pessoa", "Produto", "Valor", "Hora"])
            writer.writerow([selected_client_name.strip(), produto, valor_final, hora_formatada])

        save_client_data_csv()
        saldo = client_values.get(selected_client_name, 0.0)
        if saldo < 0:
            valor_label.config(text=f"Valor total: R${saldo:.2f}", fg="red")
        else:
            valor_label.config(text=f"Valor total: R${saldo:.2f}", fg="black")
        
        # Mostrar mensagem de promoção se houver
        if mensagem_promo:
            status_message_label.config(text=f"{produto}{mensagem_promo}", fg="green")
            product_screen.after(3000, lambda: status_message_label.config(text=""))

    # Frame para o botão e entrada de valor
    input_frame = Frame(product_screen)
    input_frame.pack(pady=10)

    Label(input_frame, text="Valor para depositar:").pack(side=LEFT)
    valor_add_entry = Entry(input_frame)
    valor_add_entry.pack(side=LEFT, padx=5)
    valor_add_entry.bind("<Return>", lambda event: add_value())

    add_value_button = Button(input_frame, text="Depositar", command=add_value)
    add_value_button.pack(side=LEFT)

    # Label para exibir o valor total do cliente
    saldo_inicial = client_values.get(selected_client_name, 0.0)
    if saldo_inicial < 0:
        valor_label = Label(product_screen, text=f"Valor total: R${saldo_inicial:.2f}", font=("Helvetica", 14), fg="red")
    else:
        valor_label = Label(product_screen, text=f"Valor total: R${saldo_inicial:.2f}", font=("Helvetica", 14))
    valor_label.pack(pady=10)

    # Frame para organizar os botões dos produtos
    button_frame = Frame(product_screen)
    button_frame.pack()

    # Carregar promoções
    promotions = get_promotions()

    column = 0
    row = 0
    cont = 0
    for product_name, valor in products.items():
        if (cont % 6 == 0):
            column = column + 1
            row = 0
        
        # Verificar se há promoção ativa para este produto
        button_text = f"{product_name}\nR${valor:.2f}"
        button_bg = "SystemButtonFace"  # Cor padrão
        
        if product_name in promotions:
            promo = promotions[product_name]
            
            # Verificar se a promoção está dentro do período válido
            hoje = datetime.datetime.now().date()
            promo_valida = True
            
            if promo.get('data_inicio'):
                try:
                    data_inicio = datetime.datetime.strptime(promo['data_inicio'], "%Y-%m-%d").date()
                    if hoje < data_inicio:
                        promo_valida = False
                except:
                    pass
            
            if promo.get('data_fim'):
                try:
                    data_fim = datetime.datetime.strptime(promo['data_fim'], "%Y-%m-%d").date()
                    if hoje > data_fim:
                        promo_valida = False
                except:
                    pass
            
            if promo_valida:
                if promo['tipo'] == 'desconto':
                    valor_promo = float(promo['valor1'])
                    button_text = f"{product_name}\nDe: R${valor:.2f}\nPor: R${valor_promo:.2f}"
                    button_bg = "#90EE90"  # Verde claro
                
                elif promo['tipo'] == 'compre_leve':
                    leve = promo['valor1']
                    pague = promo['valor2']
                    button_text = f"{product_name}\nR${valor:.2f}\n(Leve {leve} Pague {pague})"
                    button_bg = "#FFD700"  # Dourado
        
        product_button = Button(button_frame, text=button_text, width=25, bg=button_bg,
                            command=lambda p=product_name, v=valor: deduct_product_amount(p, v))
        product_button.grid(row=row, column=column, padx=5, pady=5)
        row = row + 1
        cont = cont + 1

    withdraw_frame = Frame(product_screen)
    withdraw_frame.pack(pady=10)

    Label(withdraw_frame, text="Valor para retirar:").pack(side=LEFT)
    valor_sub_entry = Entry(withdraw_frame)
    valor_sub_entry.pack(side=LEFT, padx=5)
    valor_sub_entry.bind("<Return>", lambda event: sub_value())

    sub_value_button = Button(withdraw_frame, text="Retirar", command=sub_value)
    sub_value_button.pack(side=LEFT)


def search_names():
    search_value = search_query.get().lower()
    search_value = unicodedata.normalize('NFD', search_value).encode('ascii', 'ignore').decode('ascii') # Remove acentos

    filtered_names = []
    for nome in names:
        nome_normalizado = unicodedata.normalize('NFD', nome).encode('ascii', 'ignore').decode('ascii').lower() # Remove acentos e converte para minúsculo
        if search_value in nome_normalizado:
            filtered_names.append(nome)

    listbox.delete(0, END)  

    if filtered_names:
        for nome in filtered_names:
            listbox.insert(END, nome)
    else:
        listbox.insert(END, "Nenhum nome encontrado.")

def select_name(event):
    selection = listbox.curselection()
    if not selection:
        return
    selected_name = listbox.get(selection)
    if selected_name and selected_name != "Nenhum nome encontrado.":
        open_product_screen(selected_name.strip())

def add_person():
    add_person_screen = Toplevel(login)
    add_person_screen.title("Adicionar Pessoa")
    add_person_screen.geometry("400x75")

    name_label = Label(add_person_screen, text="Nome:")
    name_label.grid(row=0, column=0, padx=10, sticky="w") 

    name_entry = Entry(add_person_screen)
    name_entry.grid(row=1, column=0, padx=10)
    name_entry.bind("<Return>", lambda event: add_name_to_list())

    def name_exists(name):
        try:
            with open("names.csv", "r", encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None) 
                for row in reader:
                    if row and row[0].lower() == name.lower():
                        return True
        except FileNotFoundError:
            return False
        return False

    def add_name_to_list():
        global names
        new_name = name_entry.get()
        if not new_name:
            messagebox.showwarning("Nome Vazio", "Por favor, insira um nome.")
            return

        new_name_normalized = unicodedata.normalize('NFD', new_name).encode('ascii', 'ignore').decode('ascii').lower().strip()

        if name_exists(new_name):
            messagebox.showwarning("Nome Existente", "Esse nome já existe.")
            return

        if any(unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('ascii').lower().strip() == new_name_normalized for name in names):
            messagebox.showwarning("Nome duplicado", "Este nome já existe na lista.")
            return

        names.append(new_name)
        with open("names.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for name in names:
                writer.writerow([name.replace('"', '').strip()])

        client_values[new_name] = 0
        save_client_data_csv()

        names = get_names()
        add_person_screen.destroy()
        home()     

    add_button = Button(add_person_screen, text="Adicionar", command=add_name_to_list)
    add_button.grid(row=1, column=1, padx=10)

def add_product(parent_callback=None):
    add_product_screen = Toplevel(login)
    add_product_screen.title("Adicionar Produto")
    add_product_screen.geometry("400x120")

    name_label = Label(add_product_screen, text="Nome do Produto:")
    name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    name_entry = Entry(add_product_screen)
    name_entry.grid(row=0, column=1, padx=10, pady=5)

    price_label = Label(add_product_screen, text="Preço (R$):")
    price_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    price_entry = Entry(add_product_screen)
    price_entry.grid(row=1, column=1, padx=10, pady=5)
    price_entry.bind("<Return>", lambda event: add_product_to_list())

    def product_exists(product_name):
        products = get_products()
        product_name_normalized = unicodedata.normalize('NFD', product_name).encode('ascii', 'ignore').decode('ascii').lower().strip()
        for prod in products.keys():
            prod_normalized = unicodedata.normalize('NFD', prod).encode('ascii', 'ignore').decode('ascii').lower().strip()
            if prod_normalized == product_name_normalized:
                return True
        return False

    def add_product_to_list():
        global products
        new_product_name = name_entry.get().strip()
        new_product_price = price_entry.get().strip()
        
        if not new_product_name:
            messagebox.showwarning("Nome Vazio", "Por favor, insira o nome do produto.")
            return
        
        if not new_product_price:
            messagebox.showwarning("Preço Vazio", "Por favor, insira o preço do produto.")
            return
        
        try:
            price_value = float(new_product_price.replace(",", "."))
            if price_value <= 0:
                messagebox.showwarning("Preço Inválido", "O preço deve ser maior que zero.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor numérico válido para o preço.")
            return
        
        if product_exists(new_product_name):
            messagebox.showwarning("Produto Existente", "Esse produto já existe.")
            return
        
        # Adicionar o produto ao dicionário
        products[new_product_name] = price_value
        
        # Salvar no arquivo products.csv
        with open("products.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for prod_name, prod_price in products.items():
                writer.writerow([prod_name, prod_price])
        
        messagebox.showinfo("Sucesso", f"Produto '{new_product_name}' adicionado com sucesso!")
        add_product_screen.destroy()
        if parent_callback:
            parent_callback()
    
    add_button = Button(add_product_screen, text="Adicionar", command=add_product_to_list)
    add_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")

def manage_products():
    manage_screen = Toplevel(login)
    manage_screen.title("Gerenciar Produtos")
    manage_screen.geometry("700x500")
    manage_screen.resizable(True, True)

    # Frame principal
    main_frame = Frame(manage_screen)
    main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Label de título
    title_label = Label(main_frame, text="Produtos Cadastrados", font=("Helvetica", 14, "bold"))
    title_label.pack(pady=(0, 10))

    # Frame para o Treeview
    tree_frame = Frame(main_frame)
    tree_frame.pack(fill=BOTH, expand=True)

    # Configuração do Treeview
    columns = ('Produto', 'Preço')
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

    # Definir cabeçalhos
    tree.heading('Produto', text='Produto', anchor='w')
    tree.heading('Preço', text='Preço (R$)', anchor='e')

    # Definir larguras das colunas
    tree.column('Produto', width=400, anchor='w')
    tree.column('Preço', width=150, anchor='e')

    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Função para carregar produtos no Treeview
    def load_products():
        global products
        # Limpar treeview
        for item in tree.get_children():
            tree.delete(item)
        
        products = get_products()
        
        # Ordenar produtos por nome
        sorted_products = sorted(products.items())
        
        for produto, preco in sorted_products:
            tree.insert('', 'end', values=(produto, f"R$ {preco:.2f}"))
    
    # Função para adicionar produto
    def add_new_product():
        add_product(parent_callback=load_products)
    
    # Função para editar produto selecionado
    def edit_selected():
        selected_items = tree.selection()
        
        if not selected_items:
            messagebox.showwarning("Nenhuma seleção", "Por favor, selecione um produto para editar.")
            return
        
        if len(selected_items) > 1:
            messagebox.showwarning("Múltipla seleção", "Por favor, selecione apenas um produto por vez.")
            return
        
        # Obter dados do produto selecionado
        item = selected_items[0]
        values = tree.item(item)['values']
        old_name = values[0]
        old_price = float(values[1].replace('R$ ', '').replace(',', '.'))
        
        # Criar janela de edição
        edit_screen = Toplevel(manage_screen)
        edit_screen.title("Editar Produto")
        edit_screen.geometry("400x120")
        
        Label(edit_screen, text="Nome do Produto:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        name_entry = Entry(edit_screen)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        name_entry.insert(0, old_name)
        
        Label(edit_screen, text="Preço (R$):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        price_entry = Entry(edit_screen)
        price_entry.grid(row=1, column=1, padx=10, pady=5)
        price_entry.insert(0, str(old_price))
        
        def save_changes():
            global products
            new_name = name_entry.get().strip()
            new_price = price_entry.get().strip()
            
            if not new_name:
                messagebox.showwarning("Nome Vazio", "Por favor, insira o nome do produto.")
                return
            
            if not new_price:
                messagebox.showwarning("Preço Vazio", "Por favor, insira o preço do produto.")
                return
            
            try:
                price_value = float(new_price.replace(",", "."))
                if price_value <= 0:
                    messagebox.showwarning("Preço Inválido", "O preço deve ser maior que zero.")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Digite um valor numérico válido para o preço.")
                return
            
            # Verificar se o nome mudou e se o novo nome já existe
            if new_name != old_name:
                if new_name in products:
                    messagebox.showwarning("Produto Existente", "Já existe um produto com esse nome.")
                    return
                # Remover o produto antigo
                del products[old_name]
            
            # Atualizar produto
            products[new_name] = price_value
            
            # Salvar no arquivo
            with open("products.csv", "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                for prod_name, prod_price in products.items():
                    writer.writerow([prod_name, prod_price])
            
            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            edit_screen.destroy()
            load_products()
        
        price_entry.bind("<Return>", lambda event: save_changes())
        Button(edit_screen, text="Salvar", command=save_changes).grid(row=2, column=1, padx=10, pady=10, sticky="e")
    
    # Função para excluir produto selecionado
    def delete_selected():
        global products
        selected_items = tree.selection()
        
        if not selected_items:
            messagebox.showwarning("Nenhuma seleção", "Por favor, selecione um produto para excluir.")
            return
        
        # Confirmar exclusão
        produtos_para_excluir = []
        for item in selected_items:
            values = tree.item(item)['values']
            produtos_para_excluir.append(values[0])
        
        if len(produtos_para_excluir) == 1:
            mensagem = f"Tem certeza que deseja excluir o produto '{produtos_para_excluir[0]}'?"
        else:
            mensagem = f"Tem certeza que deseja excluir {len(produtos_para_excluir)} produtos?"
        
        if messagebox.askyesno("Confirmar Exclusão", mensagem):
            for produto in produtos_para_excluir:
                if produto in products:
                    del products[produto]
            
            # Salvar no arquivo
            with open("products.csv", "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                for prod_name, prod_price in products.items():
                    writer.writerow([prod_name, prod_price])
            
            load_products()
            messagebox.showinfo("Sucesso", f"{len(produtos_para_excluir)} produto(s) excluído(s) com sucesso!")
    
    # Carregar produtos ao abrir
    load_products()
    
    # Frame para botões
    button_frame = Frame(main_frame)
    button_frame.pack(pady=(10, 0))
    
    Button(button_frame, text="Adicionar Produto", command=add_new_product, bg="#4CAF50", fg="white", width=18).pack(side=LEFT, padx=5)
    Button(button_frame, text="Editar Selecionado", command=edit_selected, bg="#2196F3", fg="white", width=18).pack(side=LEFT, padx=5)
    Button(button_frame, text="Excluir Selecionado", command=delete_selected, bg="#FF6B6B", fg="white", width=18).pack(side=LEFT, padx=5)
    Button(button_frame, text="Atualizar Lista", command=load_products, width=15).pack(side=LEFT, padx=5)
    Button(button_frame, text="Fechar", command=manage_screen.destroy, width=10).pack(side=LEFT, padx=5)

def add_promotion():
    add_promotion_screen = Toplevel(login)
    add_promotion_screen.title("Adicionar Promoção")
    add_promotion_screen.geometry("450x380")

    # Label e Combobox para selecionar produto
    Label(add_promotion_screen, text="Produto:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    
    produto_var = StringVar()
    products_list = list(get_products().keys())
    produto_combo = ttk.Combobox(add_promotion_screen, textvariable=produto_var, values=products_list, state="readonly", width=27)
    produto_combo.grid(row=0, column=1, padx=10, pady=10)
    
    if products_list:
        produto_combo.current(0)

    # Label e Combobox para tipo de promoção
    Label(add_promotion_screen, text="Tipo de Promoção:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    
    tipo_var = StringVar()
    tipo_combo = ttk.Combobox(add_promotion_screen, textvariable=tipo_var, 
                              values=["Compre X Leve Y", "Desconto no Preço"], 
                              state="readonly", width=27)
    tipo_combo.grid(row=1, column=1, padx=10, pady=10)
    tipo_combo.current(0)

    # Frames para diferentes tipos de promoção
    compre_leve_frame = Frame(add_promotion_screen)
    compre_leve_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    Label(compre_leve_frame, text="Leve:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    compre_entry = Entry(compre_leve_frame, width=10)
    compre_entry.grid(row=0, column=1, padx=5, pady=5)
    compre_entry.insert(0, "3")

    Label(compre_leve_frame, text="Pague:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
    leve_entry = Entry(compre_leve_frame, width=10)
    leve_entry.grid(row=0, column=3, padx=5, pady=5)
    leve_entry.insert(0, "2")

    desconto_frame = Frame(add_promotion_screen)
    desconto_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    desconto_frame.grid_remove()  # Ocultar inicialmente

    Label(desconto_frame, text="Novo Preço (R$):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    desconto_entry = Entry(desconto_frame, width=15)
    desconto_entry.grid(row=0, column=1, padx=5, pady=5)

    # Função para alternar entre frames
    def toggle_promo_type(event=None):
        if tipo_var.get() == "Compre X Leve Y":
            desconto_frame.grid_remove()
            compre_leve_frame.grid()
        else:
            compre_leve_frame.grid_remove()
            desconto_frame.grid()

    tipo_combo.bind("<<ComboboxSelected>>", toggle_promo_type)

    # Campos de data
    data_frame = Frame(add_promotion_screen)
    data_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
    
    Label(data_frame, text="Data Início (AAAA-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    data_inicio_entry = Entry(data_frame, width=15)
    data_inicio_entry.grid(row=0, column=1, padx=5, pady=5)
    data_inicio_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
    
    Label(data_frame, text="Data Fim (AAAA-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    data_fim_entry = Entry(data_frame, width=15)
    data_fim_entry.grid(row=1, column=1, padx=5, pady=5)
    # Data fim padrão: 7 dias a partir de hoje
    data_fim_padrao = datetime.datetime.now() + datetime.timedelta(days=7)
    data_fim_entry.insert(0, data_fim_padrao.strftime("%Y-%m-%d"))

    # Label de informação
    info_label = Label(add_promotion_screen, text="", fg="blue", font=("Helvetica", 9, "italic"))
    info_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    def update_info(event=None):
        produto_selecionado = produto_var.get()
        if produto_selecionado and produto_selecionado in products:
            preco_original = products[produto_selecionado]
            info_label.config(text=f"Preço original: R$ {preco_original:.2f}")

    produto_combo.bind("<<ComboboxSelected>>", update_info)
    update_info()  # Atualizar ao abrir

    def add_promotion_to_list():
        produto = produto_var.get()
        tipo = tipo_var.get()
        data_inicio = data_inicio_entry.get().strip()
        data_fim = data_fim_entry.get().strip()
        
        if not produto:
            messagebox.showwarning("Produto não selecionado", "Por favor, selecione um produto.")
            return
        
        # Validar datas
        if not data_inicio or not data_fim:
            messagebox.showwarning("Datas Vazias", "Por favor, preencha as datas de início e fim.")
            return
        
        try:
            dt_inicio = datetime.datetime.strptime(data_inicio, "%Y-%m-%d").date()
            dt_fim = datetime.datetime.strptime(data_fim, "%Y-%m-%d").date()
            
            if dt_fim < dt_inicio:
                messagebox.showwarning("Datas Inválidas", "A data de fim deve ser posterior à data de início.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use AAAA-MM-DD (ex: 2026-02-24)")
            return
        
        promotions = get_promotions()
        
        try:
            if tipo == "Compre X Leve Y":
                leve = int(compre_entry.get())  # Quantidade total que leva
                pague = int(leve_entry.get())   # Quantidade que paga
                
                if leve <= 0 or pague <= 0:
                    messagebox.showwarning("Valores Inválidos", "Os valores devem ser maiores que zero.")
                    return
                
                if pague >= leve:
                    messagebox.showwarning("Valores Inválidos", "A quantidade 'Pague' deve ser menor que 'Leve'.")
                    return
                
                promotions[produto] = {
                    'tipo': 'compre_leve',
                    'valor1': str(leve),
                    'valor2': str(pague),
                    'data_inicio': data_inicio,
                    'data_fim': data_fim
                }
                mensagem = f"Promoção adicionada: Leve {leve} Pague {pague} em {produto}\nVálida de {data_inicio} até {data_fim}"
                
            else:  # Desconto no Preço
                novo_preco = float(desconto_entry.get().replace(",", "."))
                preco_original = products[produto]
                
                if novo_preco <= 0:
                    messagebox.showwarning("Preço Inválido", "O preço deve ser maior que zero.")
                    return
                
                if novo_preco >= preco_original:
                    messagebox.showwarning("Preço Inválido", "O novo preço deve ser menor que o preço original.")
                    return
                
                promotions[produto] = {
                    'tipo': 'desconto',
                    'valor1': str(novo_preco),
                    'valor2': '',
                    'data_inicio': data_inicio,
                    'data_fim': data_fim
                }
                mensagem = f"Promoção adicionada: {produto} de R$ {preco_original:.2f} por R$ {novo_preco:.2f}\nVálida de {data_inicio} até {data_fim}"
            
            save_promotions(promotions)
            messagebox.showinfo("Sucesso", mensagem)
            add_promotion_screen.destroy()
            
        except ValueError:
            messagebox.showerror("Erro", "Digite valores numéricos válidos.")
    
    # Botões
    button_frame = Frame(add_promotion_screen)
    button_frame.grid(row=5, column=0, columnspan=2, pady=15)
    
    Button(button_frame, text="Adicionar", command=add_promotion_to_list, width=12).pack(side=LEFT, padx=5)
    Button(button_frame, text="Cancelar", command=add_promotion_screen.destroy, width=12).pack(side=LEFT, padx=5)

def manage_promotions():
    manage_screen = Toplevel(login)
    manage_screen.title("Gerenciar Promoções")
    manage_screen.geometry("900x500")
    manage_screen.resizable(True, True)

    # Frame principal
    main_frame = Frame(manage_screen)
    main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Label de título
    title_label = Label(main_frame, text="Promoções Ativas", font=("Helvetica", 14, "bold"))
    title_label.pack(pady=(0, 10))

    # Frame para o Treeview
    tree_frame = Frame(main_frame)
    tree_frame.pack(fill=BOTH, expand=True)

    # Configuração do Treeview
    columns = ('Produto', 'Tipo', 'Detalhes', 'Início', 'Fim', 'Status')
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

    # Definir cabeçalhos
    tree.heading('Produto', text='Produto', anchor='w')
    tree.heading('Tipo', text='Tipo', anchor='w')
    tree.heading('Detalhes', text='Detalhes', anchor='w')
    tree.heading('Início', text='Data Início', anchor='center')
    tree.heading('Fim', text='Data Fim', anchor='center')
    tree.heading('Status', text='Status', anchor='center')

    # Definir larguras das colunas
    tree.column('Produto', width=150, anchor='w')
    tree.column('Tipo', width=120, anchor='w')
    tree.column('Detalhes', width=200, anchor='w')
    tree.column('Início', width=100, anchor='center')
    tree.column('Fim', width=100, anchor='center')
    tree.column('Status', width=100, anchor='center')

    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Função para carregar promoções no Treeview
    def load_promotions():
        # Limpar treeview
        for item in tree.get_children():
            tree.delete(item)
        
        promotions = get_promotions()
        hoje = datetime.datetime.now().date()
        
        for produto, promo in promotions.items():
            tipo = promo['tipo']
            
            # Formatar detalhes
            if tipo == 'desconto':
                valor_promo = float(promo['valor1'])
                preco_original = products.get(produto, 0)
                detalhes = f"De R$ {preco_original:.2f} por R$ {valor_promo:.2f}"
                tipo_texto = "Desconto"
            else:  # compre_leve
                leve = promo['valor1']
                pague = promo['valor2']
                detalhes = f"Leve {leve} Pague {pague}"
                tipo_texto = "Leve/Pague"
            
            # Formatar datas
            data_inicio = promo.get('data_inicio', '')
            data_fim = promo.get('data_fim', '')
            
            # Verificar status
            status = "Ativa"
            status_tag = "ativa"
            
            if data_inicio and data_fim:
                try:
                    dt_inicio = datetime.datetime.strptime(data_inicio, "%Y-%m-%d").date()
                    dt_fim = datetime.datetime.strptime(data_fim, "%Y-%m-%d").date()
                    
                    if hoje < dt_inicio:
                        status = "Futura"
                        status_tag = "futura"
                    elif hoje > dt_fim:
                        status = "Expirada"
                        status_tag = "expirada"
                except:
                    pass
            
            # Formatar datas para exibição
            data_inicio_fmt = datetime.datetime.strptime(data_inicio, "%Y-%m-%d").strftime("%d/%m/%Y") if data_inicio else "-"
            data_fim_fmt = datetime.datetime.strptime(data_fim, "%Y-%m-%d").strftime("%d/%m/%Y") if data_fim else "-"
            
            # Inserir no treeview
            item_id = tree.insert('', 'end', values=(produto, tipo_texto, detalhes, data_inicio_fmt, data_fim_fmt, status),
                                 tags=(status_tag,))
        
        # Configurar cores para os status
        tree.tag_configure('ativa', foreground='green')
        tree.tag_configure('expirada', foreground='red')
        tree.tag_configure('futura', foreground='blue')
    
    # Função para excluir promoção selecionada
    def delete_selected():
        selected_items = tree.selection()
        
        if not selected_items:
            messagebox.showwarning("Nenhuma seleção", "Por favor, selecione uma promoção para excluir.")
            return
        
        # Confirmar exclusão
        produtos_para_excluir = []
        for item in selected_items:
            values = tree.item(item)['values']
            produtos_para_excluir.append(values[0])
        
        if len(produtos_para_excluir) == 1:
            mensagem = f"Tem certeza que deseja excluir a promoção do produto '{produtos_para_excluir[0]}'?"
        else:
            mensagem = f"Tem certeza que deseja excluir {len(produtos_para_excluir)} promoções?"
        
        if messagebox.askyesno("Confirmar Exclusão", mensagem):
            promotions = get_promotions()
            
            for produto in produtos_para_excluir:
                if produto in promotions:
                    del promotions[produto]
            
            save_promotions(promotions)
            load_promotions()
            messagebox.showinfo("Sucesso", f"{len(produtos_para_excluir)} promoção(s) excluída(s) com sucesso!")
    
    # Carregar promoções ao abrir
    load_promotions()
    
    # Frame para botões
    button_frame = Frame(main_frame)
    button_frame.pack(pady=(10, 0))
    
    Button(button_frame, text="Excluir Selecionada", command=delete_selected, bg="#FF6B6B", fg="white", width=18).pack(side=LEFT, padx=5)
    Button(button_frame, text="Atualizar Lista", command=load_promotions, width=15).pack(side=LEFT, padx=5)
    Button(button_frame, text="Fechar", command=manage_screen.destroy, width=15).pack(side=LEFT, padx=5)

def treeview_sort_column(tree, col, initial_sort=False):
    global current_sort_column, sort_direction

    l = [(tree.set(k, col), k) for k in tree.get_children('')]

    if initial_sort:
        if current_sort_column == col:
            sort_direction = not sort_direction
        else:
            sort_direction = False
        current_sort_column = col
    else:
        sort_direction = not sort_direction

    if col == 'Preço':
        l.sort(key=lambda t: float(t[0].replace('R$ ', '').replace(',', '.')), reverse=sort_direction)
    elif col == 'Data':
        l.sort(key=lambda t: t[0], reverse=sort_direction)
    else:
        l.sort(key=lambda t: t[0].lower(), reverse=sort_direction)

    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)
        tag = 'oddrow' if index % 2 == 0 else 'evenrow'
        tree.item(k, tags=(tag,))

    # Atualiza os indicadores nos cabeçalhos
    columns = tree["columns"]
    for c in columns:
        original_text = c
        if c == 'Preço': original_text = 'Preço'
        elif c == 'Produto': original_text = 'Produto'
        elif c == 'Data': original_text = 'Data'

        if c == current_sort_column:
            indicator = ' ▲' if not sort_direction else ' ▼'
            tree.heading(c, text=original_text + indicator, command=lambda c=c: treeview_sort_column(tree, c, True))
        else:
            tree.heading(c, text=original_text + ' -', command=lambda c=c: treeview_sort_column(tree, c, True))

def client_historic(selected_client_name):
    global current_sort_column, sort_direction
    current_sort_column = None
    sort_direction = False

    client_historic_screen = Toplevel(login)
    client_historic_screen.title(f"Histórico de {selected_client_name}")
    client_historic_screen.geometry("800x600+20+0")
    client_historic_screen.resizable(True, True)

    columns = ('Produto', 'Preço', 'Data')

    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Treeview.Heading",
                    font=("Arial", 10, "bold"),
                    background="#D3D3D3",
                    foreground="black",
                    relief="raised")
    style.map("Treeview.Heading",
            background=[('active', '#C0C0C0')])

    style.configure("Treeview",
                    font=("Arial", 10),
                    rowheight=25,
                    fieldbackground="#F0F0F0")
    style.map("Treeview",
            background=[('selected', '#347083')],
            foreground=[('selected', 'white')])

    tree = ttk.Treeview(client_historic_screen, columns=columns, show='headings', style="Treeview")

    tree.heading('Produto', text='Produto -', anchor='w', command=lambda: treeview_sort_column(tree, 'Produto', True))
    tree.column('Produto', width=250, anchor='w', stretch=YES)

    tree.heading('Preço', text='Preço -', anchor='e', command=lambda: treeview_sort_column(tree, 'Preço', True))
    tree.column('Preço', width=100, anchor='e', stretch=NO)

    tree.heading('Data', text='Data -', anchor='center', command=lambda: treeview_sort_column(tree, 'Data', True))
    tree.column('Data', width=180, anchor='center', stretch=NO)

    scrollbar = ttk.Scrollbar(client_historic_screen, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
    scrollbar.grid(row=0, column=1, sticky='ns', pady=10)

    client_historic_screen.grid_rowconfigure(0, weight=1)
    client_historic_screen.grid_columnconfigure(0, weight=1)

    transactions = get_transactions()

    index = 0
    for i, transaction in enumerate(transactions):
        if transaction and transaction[0].strip() == selected_client_name.strip():
            product = transaction[1]
            price_str = transaction[2]
            date = transaction[3]

            try:
                price_value = float(price_str.replace(',', '.'))
                formatted_price = f"R$ {price_value:.2f}".replace('.', ',')
            except (ValueError, IndexError):
                formatted_price = price_str

            display_values = (product, formatted_price, date)

            tag = 'oddrow' if index % 2 == 0 else 'evenrow'
            tree.insert('', END, values=display_values, tags=(tag,))
            index += 1

    style.configure("oddrow", background="#F5F5F5")
    style.configure("evenrow", background="white")


def gerar_relatorio():
    try:
        # Criar um novo workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Relatório Geral"
        
        # Ler todas as transações
        transactions = get_transactions()
        
        # Dicionários e variáveis para análise
        produtos_vendidos = {}
        produtos_valor_total = {}
        clientes_gastos = {}
        clientes_depositos = {}
        clientes_retiradas = {}
        total_depositado = 0.0
        total_retirado = 0.0
        total_vendas = 0.0
        
        # Processar transações
        for transaction in transactions:
            if len(transaction) >= 4:
                cliente = transaction[0].strip()
                produto = transaction[1].strip()
                try:
                    valor = float(transaction[2].replace(',', '.'))
                except ValueError:
                    continue
                
                if produto == "DEPOSITOU":
                    total_depositado += valor
                    clientes_depositos[cliente] = clientes_depositos.get(cliente, 0.0) + valor
                elif produto == "RETIRAR":
                    total_retirado += valor
                    clientes_retiradas[cliente] = clientes_retiradas.get(cliente, 0.0) + valor
                else:
                    # É um produto vendido
                    total_vendas += valor
                    produtos_vendidos[produto] = produtos_vendidos.get(produto, 0) + 1
                    produtos_valor_total[produto] = produtos_valor_total.get(produto, 0.0) + valor
                    clientes_gastos[cliente] = clientes_gastos.get(cliente, 0.0) + valor
        
        # ===== CABEÇALHO DO RELATÓRIO =====
        ws['A1'] = "RELATÓRIO DO BARZINHO"
        ws['A1'].font = Font(size=16, bold=True)
        ws['A1'].fill = PatternFill(start_color="203864", end_color="203864", fill_type="solid")
        ws['A1'].font = Font(size=16, bold=True, color="FFFFFF")
        ws.merge_cells('A1:D1')
        ws['A1'].alignment = Alignment(horizontal='center')
        
        data_relatorio = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ws['A2'] = f"Data de Emissão: {data_relatorio}"
        ws['A2'].font = Font(size=10, italic=True)
        ws.merge_cells('A2:D2')
        
        # ===== SEÇÃO 1: RESUMO FINANCEIRO =====
        current_row = 4
        ws[f'A{current_row}'] = "RESUMO FINANCEIRO"
        ws[f'A{current_row}'].font = Font(size=14, bold=True, color="FFFFFF")
        ws[f'A{current_row}'].fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        ws.merge_cells(f'A{current_row}:D{current_row}')
        ws[f'A{current_row}'].alignment = Alignment(horizontal='center')
        
        current_row += 2
        ws[f'A{current_row}'] = "Categoria"
        ws[f'B{current_row}'] = "Valor (R$)"
        ws[f'A{current_row}'].font = Font(bold=True)
        ws[f'B{current_row}'].font = Font(bold=True)
        ws[f'A{current_row}'].fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
        ws[f'B{current_row}'].fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
        
        current_row += 1
        ws[f'A{current_row}'] = "Total Depositado"
        ws[f'B{current_row}'] = total_depositado
        ws[f'B{current_row}'].number_format = 'R$ #,##0.00'
        
        current_row += 1
        ws[f'A{current_row}'] = "Total em Vendas"
        ws[f'B{current_row}'] = total_vendas
        ws[f'B{current_row}'].number_format = 'R$ #,##0.00'
        ws[f'B{current_row}'].fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
        
        current_row += 1
        ws[f'A{current_row}'] = "Total Retirado"
        ws[f'B{current_row}'] = total_retirado
        ws[f'B{current_row}'].number_format = 'R$ #,##0.00'
        
        current_row += 1
        caixa_fisico = total_depositado - total_retirado
        ws[f'A{current_row}'] = "Dinheiro em Caixa"
        ws[f'B{current_row}'] = caixa_fisico
        ws[f'B{current_row}'].number_format = 'R$ #,##0.00'
        ws[f'B{current_row}'].fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
        
        current_row += 1
        a_receber = total_vendas - caixa_fisico
        ws[f'A{current_row}'] = "A Receber dos Clientes"
        ws[f'B{current_row}'] = a_receber
        ws[f'B{current_row}'].number_format = 'R$ #,##0.00'
        if a_receber > 0:
            ws[f'B{current_row}'].fill = PatternFill(start_color="FFF4C3", end_color="FFF4C3", fill_type="solid")
        
        current_row += 1
        # Cálculo inteligente do lucro:
        # Se depósitos > vendas: lucro = dinheiro em caixa (vendas + crédito não retirado)
        # Se vendas > depósitos: lucro = total vendas (vendas que serão cobradas)
        lucro_total = max(total_vendas, caixa_fisico)
        ws[f'A{current_row}'] = "Lucro Total do Barzinho"
        ws[f'A{current_row}'].font = Font(bold=True)
        ws[f'B{current_row}'] = lucro_total
        ws[f'B{current_row}'].number_format = 'R$ #,##0.00'
        ws[f'B{current_row}'].font = Font(bold=True)
        ws[f'B{current_row}'].fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
        
        # Calcular valor médio gasto pelos acampantes
        current_row += 1
        total_acampantes_com_gastos = len(clientes_gastos)
        valor_medio_gasto = total_vendas / total_acampantes_com_gastos if total_acampantes_com_gastos > 0 else 0.0
        ws[f'A{current_row}'] = "Valor Médio Gasto por Acampante"
        ws[f'B{current_row}'] = valor_medio_gasto
        ws[f'B{current_row}'].number_format = 'R$ #,##0.00'
        ws[f'B{current_row}'].fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
        
        ws.column_dimensions['A'].width = 35
        ws.column_dimensions['B'].width = 18
        
        # ===== SEÇÃO 2: SALDO POR CLIENTE =====
        current_row += 3
        
        ws[f'A{current_row}'] = "SALDO POR CLIENTE"
        ws[f'A{current_row}'].font = Font(size=14, bold=True, color="FFFFFF")
        ws[f'A{current_row}'].fill = PatternFill(start_color="C65911", end_color="C65911", fill_type="solid")
        ws.merge_cells(f'A{current_row}:E{current_row}')
        ws[f'A{current_row}'].alignment = Alignment(horizontal='center')
        
        current_row += 2
        ws[f'A{current_row}'] = "Cliente"
        ws[f'B{current_row}'] = "Depositou"
        ws[f'C{current_row}'] = "Gastou"
        ws[f'D{current_row}'] = "Retirou"
        ws[f'E{current_row}'] = "Saldo Atual"
        for col in ['A', 'B', 'C', 'D', 'E']:
            ws[f'{col}{current_row}'].font = Font(bold=True)
            ws[f'{col}{current_row}'].fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
        
        ws.column_dimensions['C'].width = 18
        ws.column_dimensions['D'].width = 18
        ws.column_dimensions['E'].width = 18
        
        current_row += 1
        saldo_start_row = current_row
        
        # Obter todos os clientes únicos
        todos_clientes = set()
        todos_clientes.update(clientes_depositos.keys())
        todos_clientes.update(clientes_gastos.keys())
        todos_clientes.update(clientes_retiradas.keys())
        
        clientes_ordenados = sorted(todos_clientes)
        for cliente in clientes_ordenados:
            deposito = clientes_depositos.get(cliente, 0.0)
            gasto = clientes_gastos.get(cliente, 0.0)
            retirada = clientes_retiradas.get(cliente, 0.0)
            saldo = deposito - gasto - retirada
            
            ws[f'A{current_row}'] = cliente
            ws[f'B{current_row}'] = deposito
            ws[f'B{current_row}'].number_format = 'R$ #,##0.00'
            ws[f'C{current_row}'] = gasto
            ws[f'C{current_row}'].number_format = 'R$ #,##0.00'
            ws[f'D{current_row}'] = retirada
            ws[f'D{current_row}'].number_format = 'R$ #,##0.00'
            ws[f'E{current_row}'] = saldo
            ws[f'E{current_row}'].number_format = 'R$ #,##0.00'
            
            # Destacar saldos negativos em vermelho
            if saldo < 0:
                ws[f'E{current_row}'].font = Font(color="FF0000", bold=True)
            
            current_row += 1
        
        # ===== CRIAR ABA DE ANÁLISE DINÂMICA =====
        ws_analise = wb.create_sheet(title="Análise Dinâmica")
        
        # Organizar produtos vendidos por dia para análise dinâmica
        vendas_por_dia_analise = {}
        for transaction in transactions:
            if len(transaction) >= 4:
                produto = transaction[1].strip()
                data_hora_str = transaction[3].strip()
                
                if produto in ["DEPOSITOU", "RETIRAR"]:
                    continue
                
                try:
                    data_obj = datetime.datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M:%S")
                    data = data_obj.strftime("%d/%m/%Y")
                    
                    if data not in vendas_por_dia_analise:
                        vendas_por_dia_analise[data] = {}
                    
                    if produto not in vendas_por_dia_analise[data]:
                        vendas_por_dia_analise[data][produto] = 0
                    
                    vendas_por_dia_analise[data][produto] += 1
                except:
                    continue
        
        todos_produtos_vendidos_analise = set()
        for dia_vendas in vendas_por_dia_analise.values():
            todos_produtos_vendidos_analise.update(dia_vendas.keys())
        
        produtos_lista_analise = sorted(todos_produtos_vendidos_analise)
        datas_lista_analise = sorted(vendas_por_dia_analise.keys(), key=lambda d: datetime.datetime.strptime(d, "%d/%m/%Y"))
        
        if vendas_por_dia_analise:
            current_row = 1
            ws_analise[f'A{current_row}'] = "ANÁLISE DINÂMICA DE VENDAS"
            ws_analise[f'A{current_row}'].font = Font(size=14, bold=True, color="FFFFFF")
            ws_analise[f'A{current_row}'].fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
            ws_analise.merge_cells(f'A{current_row}:C{current_row}')
            ws_analise[f'A{current_row}'].alignment = Alignment(horizontal='center')
            
            current_row += 2
            header_analise_row = current_row
            
            # Cabeçalhos da tabela
            ws_analise[f'A{current_row}'] = "Data"
            ws_analise[f'B{current_row}'] = "Produto"
            ws_analise[f'C{current_row}'] = "Quantidade"
            
            for col in ['A', 'B', 'C']:
                ws_analise[f'{col}{current_row}'].font = Font(bold=True, size=11, color="FFFFFF")
                ws_analise[f'{col}{current_row}'].fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
            
            ws_analise.column_dimensions['A'].width = 15
            ws_analise.column_dimensions['B'].width = 25
            ws_analise.column_dimensions['C'].width = 15
            
            current_row += 1
            first_analise_row = current_row
            
            # Preencher dados
            for data in datas_lista_analise:
                for produto in produtos_lista_analise:
                    quantidade = vendas_por_dia_analise[data].get(produto, 0)
                    if quantidade > 0:
                        ws_analise[f'A{current_row}'] = data
                        ws_analise[f'B{current_row}'] = produto
                        ws_analise[f'C{current_row}'] = quantidade
                        
                        # Alternar cores
                        if current_row % 2 == 0:
                            for col in ['A', 'B', 'C']:
                                ws_analise[f'{col}{current_row}'].fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
                        
                        current_row += 1
            
            last_analise_row = current_row - 1
            
            # Adicionar filtros
            ws_analise.auto_filter.ref = f'A{header_analise_row}:C{last_analise_row}'
            
            # ===== CRIAR GRÁFICO DINÂMICO =====
            chart = BarChart()
            chart.type = "col"
            chart.style = 11
            chart.title = "Vendas Por Data e Produto"
            chart.y_axis.title = 'Quantidade'
            chart.x_axis.title = 'Produto'
            chart.grouping = "clustered"
            
            # Dados do gráfico
            data_chart = Reference(ws_analise, min_col=3, min_row=header_analise_row, max_row=last_analise_row)
            cats = Reference(ws_analise, min_col=2, min_row=header_analise_row + 1, max_row=last_analise_row)
            
            chart.add_data(data_chart, titles_from_data=True)
            chart.set_categories(cats)
            
            chart.height = 15
            chart.width = 25
            
            # Posicionar gráfico
            ws_analise.add_chart(chart, f'E{header_analise_row}')
        
        # ===== CRIAR ABA DE TRANSAÇÕES DETALHADAS =====
        ws_trans = wb.create_sheet(title="Todas as Transações")
        
        # Cabeçalhos
        ws_trans['A1'] = "Cliente"
        ws_trans['B1'] = "Produto/Tipo"
        ws_trans['C1'] = "Valor (R$)"
        ws_trans['D1'] = "Data e Hora"
        
        for col in ['A', 'B', 'C', 'D']:
            ws_trans[f'{col}1'].font = Font(bold=True, size=11)
            ws_trans[f'{col}1'].fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            ws_trans[f'{col}1'].font = Font(bold=True, size=11, color="FFFFFF")
        
        # Ajustar largura das colunas
        ws_trans.column_dimensions['A'].width = 25
        ws_trans.column_dimensions['B'].width = 25
        ws_trans.column_dimensions['C'].width = 15
        ws_trans.column_dimensions['D'].width = 20
        
        # Preencher dados das transações
        for idx, transaction in enumerate(transactions, start=2):
            if len(transaction) >= 4:
                ws_trans[f'A{idx}'] = transaction[0].strip()
                ws_trans[f'B{idx}'] = transaction[1].strip()
                try:
                    valor = float(transaction[2].replace(',', '.'))
                    ws_trans[f'C{idx}'] = valor
                    ws_trans[f'C{idx}'].number_format = 'R$ #,##0.00'
                except:
                    ws_trans[f'C{idx}'] = transaction[2]
                ws_trans[f'D{idx}'] = transaction[3].strip()
                
                # Alternar cores das linhas
                if idx % 2 == 0:
                    for col in ['A', 'B', 'C', 'D']:
                        ws_trans[f'{col}{idx}'].fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
        
        # Adicionar filtro automático na tabela de transações
        if len(transactions) > 0:
            ws_trans.auto_filter.ref = f'A1:D{len(transactions) + 1}'
        
        # Salvar arquivo
        filename = "relatorio do barzinho.xlsx"
        wb.save(filename)
        
        messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\nArquivo: {filename}")
        
    except Exception as e:
        log_error("Erro ao gerar relatório", e)
        messagebox.showerror("Erro", "Não foi possível gerar o relatório.\nVerifique o arquivo error_log.txt para mais detalhes.")


def reset_application():
    """Função para resetar o aplicativo apagando todos os CSVs"""
    reset_window = Toplevel(login)
    reset_window.title("Resetar Aplicativo")
    reset_window.geometry(f"500x250+{int(monitor_width-250)}+{int(monitor_height-125)}")
    reset_window.configure(background="#fff")
    reset_window.resizable(False, False)
    
    # Título de aviso
    warning_label = Label(reset_window, text="⚠️ ATENÇÃO ⚠️", 
                         font=("Helvetica", 16, "bold"), 
                         fg="red", 
                         background="#fff")
    warning_label.pack(pady=10)
    
    # Mensagem de instrução
    instruction_label = Label(reset_window, 
                             text="Para resetar o aplicativo e apagar todos os dados,\nescreva a frase abaixo:", 
                             font=("Helvetica", 10), 
                             background="#fff",
                             justify=CENTER)
    instruction_label.pack(pady=5)
    
    # Frase que deve ser digitada
    phrase_label = Label(reset_window, 
                        text="ESTOU CIENTE QUE IREI APAGAR TUDO", 
                        font=("Helvetica", 10, "bold"), 
                        fg="darkred",
                        background="#fff")
    phrase_label.pack(pady=5)
    
    # Campo de entrada
    confirmation_entry = Entry(reset_window, width=40, font=("Helvetica", 10))
    confirmation_entry.pack(pady=10)
    confirmation_entry.focus()
    
    # Função para verificar e apagar
    def confirm_and_delete():
        if confirmation_entry.get().strip() == "ESTOU CIENTE QUE IREI APAGAR TUDO":
            try:
                # Lista de arquivos CSV para apagar
                csv_files = ["client_data.csv", "transacoes.csv", "products.csv", 
                            "promotions.csv", "names.csv"]
                
                deleted_files = []
                for csv_file in csv_files:
                    if os.path.exists(csv_file):
                        os.remove(csv_file)
                        deleted_files.append(csv_file)
                
                # Criar names.csv vazio
                with open("names.csv", "w", encoding='UTF-8') as file:
                    pass  # Cria arquivo vazio
                
                # Criar products.csv vazio
                with open("products.csv", "w", encoding='UTF-8') as file:
                    pass  # Cria arquivo vazio
                
                reset_window.destroy()
                messagebox.showinfo("Sucesso", 
                                   f"Aplicativo resetado com sucesso!\n\nArquivos apagados:\n" + 
                                   "\n".join(deleted_files) +
                                   "\n\nnames.csv e products.csv foram criados vazios.\n\nO aplicativo será fechado.")
                login.destroy()
                
            except Exception as e:
                log_error("Erro ao resetar aplicativo", e)
                messagebox.showerror("Erro", f"Não foi possível resetar o aplicativo:\n{str(e)}")
        else:
            messagebox.showerror("Erro", "A frase digitada está incorreta!\nDigite exatamente como mostrado.")
            confirmation_entry.delete(0, END)
            confirmation_entry.focus()
    
    # Botão de apagar (vermelho)
    delete_button = Button(reset_window, 
                          text="APAGAR TUDO", 
                          command=confirm_and_delete,
                          bg="red", 
                          fg="white", 
                          font=("Helvetica", 12, "bold"),
                          width=20,
                          height=2,
                          cursor="hand2")
    delete_button.pack(pady=10)
    
    # Botão de cancelar
    cancel_button = Button(reset_window, 
                          text="Cancelar", 
                          command=reset_window.destroy,
                          font=("Helvetica", 10),
                          width=15)
    cancel_button.pack(pady=5)
    
    # Bind Enter key
    confirmation_entry.bind("<Return>", lambda event: confirm_and_delete())


def home():
    init_client_data()
    load_client_values()
    global search_query, listbox
    login.title("Barzinho")
    login.geometry(f"{form_width}x{form_height+20}+{int(monitor_width-form_width/2)}+{int(monitor_height-form_height/2)}")
    login.configure(background="#fff")

    # Criar menu uma vez no início (otimização)
    menu = Menu(login, tearoff=0)
    menu.add_command(label="Emitir Relatório", command=gerar_relatorio)
    menu.add_separator()
    menu.add_command(label="Adicionar Pessoa", command=add_person)
    menu.add_command(label="Gerenciar Produtos", command=manage_products)
    menu.add_command(label="Adicionar Promoção", command=add_promotion)
    menu.add_command(label="Gerenciar Promoções", command=manage_promotions)
    menu.add_separator()
    menu.add_command(label="🔄 Resetar Aplicativo", command=reset_application, foreground="red")

    # Função para mostrar menu dropdown
    def show_menu():
        try:
            menu.tk_popup(menu_button.winfo_rootx(), menu_button.winfo_rooty() + menu_button.winfo_height())
        finally:
            menu.grab_release()
    
    # Botão Menu no canto superior direito
    menu_button = Button(login, text="☰ Menu", bd='3', command=show_menu, font=("Helvetica", 10))
    menu_button.place(x=form_width - 80, y=10)
    
    icon_image = PhotoImage(file='icone/barbilonia.png').subsample(2, 2)

    icon_label = Label(login, image=icon_image, background="#fff")
    icon_label.image = icon_image

    search_label = Label(login, text="Buscar:", background="#fff", anchor=W)

    search_query = StringVar()
    entry_width = 200
    entry_x = form_width / 2 - entry_width / 2
    search_entry = Entry(login, textvariable=search_query)
    search_entry.place(x=entry_x, y=form_height/5+2, width=entry_width)
    search_entry.bind("<Return>", lambda event: search_names())

    total_width = icon_label.winfo_reqwidth() + search_label.winfo_reqwidth() + entry_width + 50 + 50
    start_x = form_width / 2 - total_width / 2

    icon_x = form_width / 2 - total_width / 2 + icon_image.width()/2 + 80
    icon_label.place(x=icon_x, y=form_height / 5 - icon_image.height() - 5)

    label_x = start_x + icon_label.winfo_reqwidth() + 50
    search_label.place(x=label_x, y=form_height / 5)

    listbox = Listbox(login, width=int(form_width/7), height=20)
    listbox.place(x=30, y=form_height/5 + 40)
    for nome in names:
        listbox.insert(END, nome)
    listbox.bind("<<ListboxSelect>>", select_name)

    search_button = Button(login, text="Buscar", bd='3', command=search_names)
    search_button.place(x=form_width/2 + entry_width/2 + 10, y=form_height/5)

    exit_button = Button(login, text="Sair", bd='3', command=login.destroy)
    exit_x = form_width - exit_button.winfo_reqwidth() - 10
    exit_button.place(x=exit_x, y=form_height - exit_button.winfo_reqheight())

    login.mainloop()

def load_client_values():
    global client_values
    if os.path.exists("client_data.csv"):
        with open("client_data.csv", "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                client_values[row[0].strip()] = float(row[1])
if __name__ == "__main__":
    home()