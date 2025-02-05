from tkinter import *
from tkinter import messagebox
import csv
import os

login = Tk()
monitor_width = login.winfo_screenwidth()/2
monitor_height = login.winfo_screenheight()/2
form_width = 500
form_height = 500

names = ["João Silva", "João", "Maria Souza", "Pedro Alves", "Ana Oliveira", "José Santos",
     "Paulo Costa", "Marcos Pereira", "Lucas Rodrigues", "Rafael Almeida", "Bruno Gomes"]

products = {
    "Produto A": 10.0,
    "Produto B": 25.0,
    "Produto C": 15.50,
    "Produto D": 5.0,
    "Produto E": 30.0,
}

client_values = {}

def save_csv():
    with open("client_data.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Nome", "Valor"])  # Cabeçalho
        for name, value in client_values.items():
            writer.writerow([name, value])

def open_product_screen(selected_client_name):
    product_screen = Toplevel(login)
    product_screen.title(f"Produtos - {selected_client_name}")
    product_screen.geometry(f"{form_width}x{form_height}+{int(monitor_width-form_width/2)}+{int(monitor_height-form_height/2)}")

    # Label com o nome do cliente
    Label(product_screen, text=f"Cliente: {selected_client_name}", font=("Helvetica", 16)).pack(pady=10)

    def add_value():
        try:
            added_value = float(valor_entry.get())
            if selected_client_name in client_values:
                client_values[selected_client_name] += added_value
            else:
                client_values[selected_client_name] = added_value
            save_csv()
            valor_label.config(text=f"Valor total: R${client_values.get(selected_client_name, 0.0):.2f}")
            valor_entry.delete(0, END)
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor numérico válido.")

    status_message_label = Label(product_screen, text="", fg="red")
    status_message_label.pack()
    def deduct_product_amount(produto, valor):
        if selected_client_name not in client_values or client_values[selected_client_name] < valor:
            status_message_label.config(text=f"Saldo insuficiente para {produto}", fg="red")  # Mostra mensagem na tela
            return

        client_values[selected_client_name] -= valor
        save_csv()
        valor_label.config(text=f"Valor total: R${client_values.get(selected_client_name, 0.0):.2f}") # Atualiza o label primeiro

    # Frame para o botão e entrada de valor
    input_frame = Frame(product_screen)
    input_frame.pack(pady=10)

    Label(input_frame, text="Valor a adicionar:").pack(side=LEFT)
    valor_entry = Entry(input_frame)
    valor_entry.pack(side=LEFT, padx=5)

    add_value_button = Button(input_frame, text="Adicionar", command=add_value)
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


def search_names():
    search_value = search_query.get().lower()
    filtered_names = [nome for nome in names if search_value in nome.lower()]

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

def home():
    load_csv()
    global search_query, listbox
    login.title("BarBilônia")
    login.geometry(f"{form_width}x{form_height}+{int(monitor_width-form_width/2)}+{int(monitor_height-form_height/2)}")

    search_query = StringVar()

    Label(login, text="Buscar:", background="#fff", anchor=W).place(x=form_width/5, y=form_height/5)

    search_entry = Entry(login, textvariable=search_query)
    search_entry.place(x=form_width/5+50, y=form_height/5+2, width=150)

    listbox = Listbox(login, width=30)
    listbox.place(x=form_width/5, y=form_height/5 + 40)
    for nome in names:
        listbox.insert(END, nome)
    listbox.bind("<<ListboxSelect>>", select_name)

    # Buttons
    search = Button(login, text="Buscar", bd='3', command=search_names)
    search.place(x=form_width/5+210, y=form_height/5)

    exit_button = Button(login, text="Sair", bd='3', command=login.destroy)
    exit_button.place(x=form_width-35, y=form_height-30)

    login.mainloop()

def load_csv():
    global client_values
    if os.path.exists("client_data.csv"):
        with open("client_data.csv", "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)  # Pula o cabeçalho
            for row in reader:
                client_values[row[0]] = float(row[1])

home()