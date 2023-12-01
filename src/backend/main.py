import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from scipy.optimize import linprog
from ttkthemes import ThemedStyle


class LinearProgrammingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(
            "Aplicação de Programação Linear - Maximizar ou Reduzir seus custos"
        )

        # Variáveis para o número de modelos e restrições
        self.num_modelos_var = tk.StringVar(value="")
        self.num_restricoes_var = tk.StringVar(value="")

        # Inicializar listas de variáveis para contribuições, coeficientes e limites
        self.contribuicoes_var = []
        self.coeficientes_var = []
        self.limites_var = []
        self.tipo_restricao_var = []
        self.nomes_modelos = []

        # Espaçamento e padding
        self.padx = 10
        self.pady = 5

        # Configurar a interface gráfica
        self.setup_ui()

    def setup_ui(self):
        # Aplicar um tema aprimorado
        style = ThemedStyle(self.root)
        style.set_theme(
            "arc"
        )  # Alterei o tema para "arc" para uma aparência mais moderna

        # Limpar campos existentes
        self.clear_widgets()

        # Labels e Entry para o número de modelos
        self.create_label_entry("Número de Produtos:", self.num_modelos_var, 0)

        # Labels e Entry para o número de restrições
        self.create_label_entry("Número de Restrições:", self.num_restricoes_var, 1)

        # Botão para criar campos com base no número de modelos e restrições inseridos
        create_button = ttk.Button(
            self.root, text="Criar Campos", command=self.create_fields
        )
        create_button.grid(
            row=2,
            columnspan=2,
            padx=(self.padx, self.padx * 2),
            pady=self.pady,
            sticky="ew",
        )
        create_button.state(["!disabled"])  # Ativar o botão

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_label_entry(self, label_text, text_var, row):
        label = ttk.Label(self.root, text=label_text)
        label.grid(row=row, column=0, padx=self.padx, pady=self.pady, sticky="w")
        entry = ttk.Entry(self.root, textvariable=text_var)
        entry.grid(row=row, column=1, padx=self.padx, pady=self.pady, sticky="ew")

    def create_fields(self):
        try:
            num_modelos = int(self.num_modelos_var.get())
            num_restricoes = int(self.num_restricoes_var.get())

            if num_modelos <= 0 or num_restricoes <= 0:
                messagebox.showerror(
                    "Erro",
                    "Por favor, insira valores válidos maiores que zero para o número de modelos e restrições.",
                )
                return

            # Limpar campos existentes
            self.clear_widgets()

            # Labels e Entry para o número de modelos
            self.create_label_entry("Número de Produtos:", self.num_modelos_var, 0)

            # Labels e Entry para o número de restrições
            self.create_label_entry("Número de Restrições:", self.num_restricoes_var, 1)

            # Inicializar listas de variáveis para contribuições, coeficientes e limites
            self.contribuicoes_var = [tk.DoubleVar() for _ in range(num_modelos)]
            self.coeficientes_var = [
                [tk.DoubleVar() for _ in range(num_modelos)]
                for _ in range(num_restricoes)
            ]
            self.limites_var = [tk.DoubleVar() for _ in range(num_restricoes)]
            self.tipo_restricao_var = [
                tk.StringVar(value="≤") for _ in range(num_restricoes)
            ]
            self.nomes_modelos = [
                tk.StringVar(value=f"Produtos: {i + 1}") for i in range(num_modelos)
            ]

            # Labels para informar ao usuário
            ttk.Label(self.root, text="Nomes dos Produtos:").grid(
                row=2, column=0, columnspan=num_modelos, pady=self.pady, sticky="w"
            )

            # Entry para os nomes dos modelos
            for i in range(num_modelos):
                ttk.Entry(self.root, textvariable=self.nomes_modelos[i]).grid(
                    row=3, column=i, padx=self.padx, pady=self.pady, sticky="ew"
                )

            # Labels e Entry para Preço dos Produtos
            ttk.Label(
                self.root, text="Preço dos Produtos:"
            ).grid(  # settar o input para R$
                row=4, column=0, columnspan=num_modelos, pady=self.pady, sticky="w"
            )
            for i in range(num_modelos):
                entry = ttk.Entry(self.root, textvariable=self.contribuicoes_var[i])
                entry.grid(
                    row=5, column=i, padx=self.padx, pady=self.pady, sticky="ew"
                )

                # Adicione a validação para permitir apenas números positivos
                entry.config(validate="key", validatecommand=(entry.register(self.validate_price), "%P"))

            # Labels e Entry para coeficientes das restrições
            ttk.Label(self.root, text="Coeficientes das Restrições:").grid(
                row=6, column=0, columnspan=num_modelos, pady=self.pady, sticky="w"
            )
            for i in range(num_restricoes):
                for j in range(num_modelos):
                    ttk.Entry(self.root, textvariable=self.coeficientes_var[i][j]).grid(
                        row=7 + i, column=j, padx=self.padx, pady=self.pady, sticky="ew"
                    )
                ttk.Combobox(
                    self.root,
                    values=["≤", "≥", "="],
                    textvariable=self.tipo_restricao_var[i],
                ).grid(
                    row=7 + i,
                    column=num_modelos,
                    padx=self.padx,
                    pady=self.pady,
                    sticky="ew",
                )
                ttk.Entry(self.root, textvariable=self.limites_var[i]).grid(
                    row=7 + i,
                    column=num_modelos + 1,
                    padx=self.padx,
                    pady=self.pady,
                    sticky="ew",
                )

            # Botão para resolver o problema de programação linear
            resolve_button = ttk.Button(
                self.root, text="Resolver", command=self.resolve_lp
            )
            resolve_button.grid(
                row=8 + num_restricoes,
                columnspan=num_modelos + 3,
                padx=(self.padx, self.padx * 2),
                pady=self.pady,
                sticky="ew",
            )

            # Botão para limpar inputs e voltar à tela de escolher a quantidade
            clear_button = ttk.Button(
                self.root, text="Limpar Inputs", command=self.clear_inputs
            )
            clear_button.grid(
                row=9 + num_restricoes,
                columnspan=num_modelos + 3,
                pady=self.pady,
                padx=(self.padx, self.padx * 2),
                sticky="ew",
            )

        except ValueError:
            messagebox.showerror(
                "Erro",
                "Por favor, insira valores válidos para o número de produtos e restrições.",
            )

    # Função de validação para preços
    def validate_price(self, new_value):
        try:
            # Tenta converter o novo valor para um número
            price = float(new_value)
            # Verifica se o preço é maior que zero
            return price > 0
        except ValueError:
            # Se a conversão falhar, o usuário digitou algo que não é um número
            return False

    def resolve_lp(self):
        try:
            num_modelos = int(self.num_modelos_var.get())
            num_restricoes = int(self.num_restricoes_var.get())

            contribuicoes = [-var.get() for var in self.contribuicoes_var]
            coeficientes = [[var.get() for var in row] for row in self.coeficientes_var]
            limites = [var.get() for var in self.limites_var]
            tipos_restricao = [var.get() for var in self.tipo_restricao_var]

            c = contribuicoes
            A_ub = []
            b_ub = []

            for i in range(num_restricoes):
                coeficientes_restricao = coeficientes[i]
                limite = limites[i]

                if tipos_restricao[i] == "≤":
                    A_ub.append(coeficientes_restricao)
                    b_ub.append(limite)
                elif tipos_restricao[i] == "≥":
                    A_ub.append([-x for x in coeficientes_restricao])
                    b_ub.append(-limite)
                elif tipos_restricao[i] == "=":
                    A_ub.append(coeficientes_restricao)
                    b_ub.append(limite)

            resultado = linprog(
                c,
                A_ub=A_ub,
                b_ub=b_ub,
            )

            if resultado.success:
                lucro_maximo = round(-resultado.fun, 2)
                quantidades_modelos = resultado.x

                resultado_str = f"Aqui está seu resultado: \n\n"
                resultado_str += f"Lucro máximo: R${lucro_maximo:.2f}\n\n"
                resultado_str += "Quantidade de produtos a serem produzidos:\n \n"
                for i, quantidade in enumerate(quantidades_modelos):
                    resultado_str += f"Quantidade de {self.nomes_modelos[i].get()}: {quantidade:.2f}\n"

                resultado_str += "\nRestrições:\n\n"
                for i in range(num_restricoes):
                    restricao_calculada = sum(
                        coeficientes[i][j] * resultado.x[j] for j in range(num_modelos)
                    )
                    limite_arredondado = (
                        round(limites[i], 2) if limites[i] % 1 != 0 else int(limites[i])
                    )
                    resultado_str += f"Restrição {i + 1} calculada: {restricao_calculada:.2f} (Limite: {limite_arredondado})\n"

                # Criar uma nova janela para exibir os resultados
                self.show_result_window(resultado_str)

            else:
                self.resultado_label = ttk.Label(
                    self.root,
                    text="O problema não possui solução viável.",
                    justify="left",
                )
                self.resultado_label.grid(
                    row=9, column=0, columnspan=num_modelos + 2, sticky="w"
                )

        except ValueError:
            messagebox.showerror(
                "Erro", "Por favor, insira valores válidos para os campos."
            )

    def show_result_window(self, resultado_str):
        result_window = Toplevel(self.root)
        result_window.title("Resultado")
        result_label = ttk.Label(result_window, text=resultado_str, justify="left")
        result_label.pack()

    def clear_inputs(self):
        # Limpar inputs e voltar à tela inicial
        self.num_modelos_var.set("")
        self.num_restricoes_var.set("")
        for nome_modelo in self.nomes_modelos:
            nome_modelo.set("")
        self.setup_ui()


if __name__ == "__main__":
    root = tk.Tk()
    app = LinearProgrammingGUI(root)
    root.mainloop()