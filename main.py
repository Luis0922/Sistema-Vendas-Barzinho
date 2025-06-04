from tkinter import *
from tkinter import messagebox
import csv
import os
import datetime
import unicodedata

login = Tk()
monitor_width = login.winfo_screenwidth()/2
monitor_height = login.winfo_screenheight()/2
form_width = 500
form_height = 500


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

products = get_products()

client_values = {}

def save_csv():
    with open("client_data.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Nome", "Valor"])  # Cabeçalho
        for name, value in client_values.items():
            writer.writerow([name, value])

def open_product_screen(selected_client_name):
    product_screen = Toplevel(login)
    product_screen.title(f"{selected_client_name}")
    product_screen.geometry(f"{form_width}x{form_height}+{int(monitor_width-form_width/2)+20}+{int(monitor_height-form_height/2)+20}")

    # Label com o nome do cliente
    Label(product_screen, text=f"Cliente: {selected_client_name}", font=("Helvetica", 16)).pack(pady=10)

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
            with open("transacoes.csv", "a", newline="") as file:
                writer = csv.writer(file)
                if os.stat("transacoes.csv").st_size == 0:
                    writer.writerow(["Pessoa", "Produto", "Valor", "Hora"])
                writer.writerow([selected_client_name.strip(), "DEPOSITOU", added_value, formated_hour])
            
            save_csv()
            valor_label.config(text=f"Valor total: R${client_values.get(selected_client_name, 0.0):.2f}")
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
                if client_values[selected_client_name] - subbed_value < 0:
                    messagebox.showerror("Erro", f"O {selected_client_name.strip()} não pode ficar com saldo negativo.")
                    return
                client_values[selected_client_name] -= subbed_value
            else:
                messagebox.showerror("Erro", f"O cliente {selected_client_name.strip()} não tem saldo.")
                return
            
            agora = datetime.datetime.now()
            formated_hour = agora.strftime("%Y-%m-%d %H:%M:%S")
            with open("transacoes.csv", "a", newline="") as file:
                writer = csv.writer(file)
                if os.stat("transacoes.csv").st_size == 0:
                    writer.writerow(["Pessoa", "Produto", "Valor", "Hora"])
                writer.writerow([selected_client_name.strip(), "RETIRAR", subbed_value, formated_hour])
            
            save_csv()
            valor_label.config(text=f"Valor total: R${client_values.get(selected_client_name, 0.0):.2f}")
            valor_sub_entry.delete(0, END)
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor numérico válido.")

    status_message_label = Label(product_screen, text="", fg="red")
    status_message_label.pack()
    def deduct_product_amount(produto, valor):
        if selected_client_name not in client_values or client_values[selected_client_name] < valor:
            status_message_label.config(text=f"Saldo insuficiente para {produto}", fg="red")  # Mostra mensagem na tela
            return

        client_values[selected_client_name] -= valor

        agora = datetime.datetime.now()
        hora_formatada = agora.strftime("%Y-%m-%d %H:%M:%S")

        with open("transacoes.csv", "a", newline="") as file:
            writer = csv.writer(file)
            if os.stat("transacoes.csv").st_size == 0:
                writer.writerow(["Pessoa", "Produto", "Valor", "Hora"])
            writer.writerow([selected_client_name.strip(), produto, valor, hora_formatada])

        save_csv()
        valor_label.config(text=f"Valor total: R${client_values.get(selected_client_name, 0.0):.2f}") # Atualiza o label primeiro

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
    valor_label = Label(product_screen, text=f"Saldo: R${client_values.get(selected_client_name, 0.0):.2f}", font=("Helvetica", 14))
    valor_label.pack(pady=10)

    # Frame para organizar os botões dos produtos (desativados por enquanto)
    button_frame = Frame(product_screen)
    button_frame.pack()

    for product_name, valor in products.items():
        product_button = Button(button_frame, text=f"{product_name} - R${valor:.2f}", width=20,
                            command=lambda p=product_name, v=valor: deduct_product_amount(p, v)) # Chama subtrair_produto
        product_button.pack(pady=5)

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
            filtered_names.append(nome) # Adiciona o nome original à lista

    listbox.delete(0, END)  

    if filtered_names:
        for nome in filtered_names:
            listbox.insert(END, nome)
    else:
        listbox.insert(END, "Nenhum nome encontrado.")

def select_name(event):
    selected_name = listbox.get(listbox.curselection())
    if selected_name and selected_name != "Nenhum nome encontrado.":
        open_product_screen(selected_name)

def add_person():
    add_person_screen = Toplevel(login)
    add_person_screen.title("Adicionar Pessoa")
    add_person_screen.geometry("400x75")  # Aumentei um pouco a altura para acomodar os elementos

    name_label = Label(add_person_screen, text="Nome:")
    name_label.grid(row=0, column=0, padx=10, sticky="w")  # Use grid para melhor organização

    name_entry = Entry(add_person_screen)
    name_entry.grid(row=1, column=0, padx=10)
    name_entry.bind("<Return>", lambda event: add_name_to_list())

    def name_exists(name):
        try:
            with open("names.csv", "r", encoding='utf-8') as file:  # encoding para lidar com caracteres especiais
                reader = csv.reader(file)
                next(reader, None)  # Pula o cabeçalho, se existir
                for row in reader:
                    if row and row[0].lower() == name.lower():  # Comparação sem case-sensitive
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

        # Se chegou aqui, o nome é válido
        with open("names.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if os.stat("names.csv").st_size == 0:
                writer.writerow(["Pessoa"])
            writer.writerow([new_name])

        names = get_names()  # Certifique-se de que get_names() esteja definida e funcionando corretamente
        home()
        add_person_screen.destroy() # Fecha a janela após adicionar

    add_button = Button(add_person_screen, text="Adicionar", command=add_name_to_list)
    add_button.grid(row=1, column=1, padx=10)



def home():
    load_csv()
    global search_query, listbox
    login.title("Barzinho")
    login.geometry(f"{form_width}x{form_height}+{int(monitor_width-form_width/2)}+{int(monitor_height-form_height/2)}")
    login.configure(background="#fff") # Define o fundo branco

    
    icon_image = PhotoImage(file='icone/barbilonia.png').subsample(2, 2)

    # Criar o Label para exibir o ícone (sem posicioná-lo ainda)
    icon_label = Label(login, image=icon_image, background="#fff")
    icon_label.image = icon_image

    # Criar o Label "Buscar:" (sem posicioná-lo ainda)
    search_label = Label(login, text="Buscar:", background="#fff", anchor=W)

    search_query = StringVar()
    entry_width = 200  # Largura do campo de entrada
    entry_x = form_width / 2 - entry_width / 2  # Centraliza a entry
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
    exit_button.place(x=exit_x, y=form_height - exit_button.winfo_reqheight() - 10)

    add_person_button = Button(login, text="Adicionar Pessoa", bd='1', command=add_person)
    add_person_button.place(x=30, y=form_height - exit_button.winfo_reqheight()-10)

    login.mainloop()

def load_csv():
    global client_values
    if os.path.exists("client_data.csv"):
        with open("client_data.csv", "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)  # Pula o cabeçalho
            for row in reader:
                client_values[row[0]] = float(row[1])

if __name__ == "__main__":
    home()