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
    def deduct_product_amount(produto, valor):
        if selected_client_name not in client_values:
            client_values[selected_client_name] = 0
        client_values[selected_client_name] -= valor 

        agora = datetime.datetime.now()
        hora_formatada = agora.strftime("%Y-%m-%d %H:%M:%S")

        with open("transacoes.csv", "a", newline="", encoding='utf-8') as file:
            writer = csv.writer(file)
            if os.stat("transacoes.csv").st_size == 0:
                writer.writerow(["Pessoa", "Produto", "Valor", "Hora"])
            writer.writerow([selected_client_name.strip(), produto, valor, hora_formatada])

        save_client_data_csv()
        saldo = client_values.get(selected_client_name, 0.0)
        if saldo < 0:
            valor_label.config(text=f"Valor total: R${saldo:.2f}", fg="red")
        else:
            valor_label.config(text=f"Valor total: R${saldo:.2f}", fg="black")

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

    # Frame para organizar os botões dos produtos (desativados por enquanto)
    button_frame = Frame(product_screen)
    button_frame.pack()

    column = 0
    row = 0
    cont = 0
    for product_name, valor in products.items():
        if (cont % 6 == 0):
            column = column + 1
            row = 0
        product_button = Button(button_frame, text=f"{product_name}\nR${valor:.2f}", width=25,
                            command=lambda p=product_name, v=valor: deduct_product_amount(p, v)) # Chama subtrair_produto
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
    selected_name = listbox.get(listbox.curselection())
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
        ws[f'A{current_row}'] = "Saldo Final (Depósitos + Vendas - Retiradas)"
        ws[f'A{current_row}'].font = Font(bold=True)
        ws[f'B{current_row}'] = total_depositado + total_vendas - total_retirado
        ws[f'B{current_row}'].number_format = 'R$ #,##0.00'
        ws[f'B{current_row}'].font = Font(bold=True)
        ws[f'B{current_row}'].fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
        
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


def home():
    init_client_data()
    load_client_values()
    global search_query, listbox
    login.title("Barzinho")
    login.geometry(f"{form_width}x{form_height+20}+{int(monitor_width-form_width/2)}+{int(monitor_height-form_height/2)}")
    login.configure(background="#fff")

    # Botão Emitir Relatório no canto superior esquerdo
    emitir_relatorio_button = Button(login, text="Emitir Relatório", bd='3', command=gerar_relatorio)
    emitir_relatorio_button.place(x=10, y=10)
    
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

    add_person_button = Button(login, text="Adicionar Pessoa", bd='1', command=add_person)
    add_person_button.place(x=30, y=form_height - exit_button.winfo_reqheight())

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