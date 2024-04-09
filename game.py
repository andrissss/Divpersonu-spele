import tkinter as tk
from enum import Enum
from tkinter import messagebox
import random
from tkinter import font as tkFont
from tkinter import *
import customtkinter as ctk
import time

# spēles beigas rezultāti
experiment_results = {
    'computer_wins': 0, # uzvarētāji
    'human_wins': 0,
    'total_visited_nodes': [],  # kopējais apmeklēto virsotņu skaits 
    'average_move_time': [] # vidējais datorlaiks gājienu izpildei
}

# definēt spēlētājus
class Player(Enum):
    USER = 0
    COMPUTER = 1

# realizēts pamatalgoritmu kods
class Game:
    def __init__(self, target_number=7):
        self.target_number = target_number
        self.current_player = Player.USER
        self.moves_history = []
        self.total_points = 0
        self.bank = 0
        self.final_score = 0
        self.starting_numbers = self.generate_starting_numbers()
        self.current_number = None

        self.visited_nodes = 0
        self.move_times = []
        self.current_number = target_number

    # definet sākuma numuru
    def set_starting_number(self, number):
        self.current_number = number

    # pārbaudīt, vai skaitļus var dalīt ar 3, 4 un 5.
    def is_divisible_by_345(self, n):
        return n % 3 == 0 and n % 4 == 0 and n % 5 == 0

    # ģenerēt sākuma skaitļus no diapazona 40000 līdz 50000, kas dalās ar 3, 4 un 5
    def generate_starting_numbers(self):
        min = 40000
        max = 50000
        numbers = [n for n in range(min, max + 1) if self.is_divisible_by_345(n)]
        return random.sample(numbers, 5)   
     
    # pārbaudīt, vai skaitļus var dalīt bez atlīkuma
    def is_divisible(self, number):
        if self.current_number is None:
            return False 
        return self.current_number % number == 0

    # veikt gājienu spēlē
    def make_move(self, number):
        if self.is_divisible(number): 
            self.moves_history.append((self.current_player, number)) #  saglaba iepriekšējo gājienu spēlē (pašreizējais spēlētajs, veidota skaitlis)
            self.current_number //= number # dala pašreizējo numuru ar dotajā gājienā izvēlēto skaitli
            self.update_points(number) 
            self.switch_player()
        else:
            raise ValueError("Nepareizs gājiens")

    # atjaunat punktus pēc nosacījumiem
    def update_points(self, divisor):
        is_even_number = self.current_number % 2 == 0 

        if is_even_number:  # ja skaitlis ir pāra
            self.total_points += 1  # pievieno 1 punktu kopējam rezultātam
        else:   # ja skaitlis ir nepāra
            self.total_points -= 1  # atņem 1 punktu no kopējā rezultāta 

        last_digit = self.current_number % 10

        if last_digit == 0 or last_digit == 5: # ja skaitlis beidzas ar ciparu 0 vai 5 
            self.bank += 1 # pievienot 1 punktu bankai

    # pārslēgties no viena spēlētāja uz citu
    def switch_player(self):
        if self.current_player == Player.USER:
            self.current_player = Player.COMPUTER
        else:
            self.current_player = Player.USER

    # pārbauda, vai spēle ir beigusies
    def is_game_over(self):
        min = 3
        max = 5
        return not any(self.is_divisible(n) for n in range(min, max + 1))  # ja skaitlis vairs nav dalāms ar 3, 4 vai 5
   
    # aprēķina galīgo rezultātu
    def calculate_final_score(self):
        is_even_score = self.total_points % 2 == 0
        if is_even_score:   # ja kopējais punktu skaits ir pāra skaitlis
            self.final_score = self.total_points - self.bank    # atņemiet bankas punktus no kopējā punktu skaita
        else:   # ja kopējais punktu skaits ir nepāra skaitlis
            self.final_score = self.total_points + self.bank

    # heiristiskā novērtējuma funkcija
    def evaluate_heuristic(self):
        score = self.total_points
        bank = self.bank
        number = self.current_number

        # Prognozē punktus, balstoties uz pašreizējo skaitli un iespējamajām darbībām
        if number % 2 == 0:
            score += 1  # Pievieno punktu, ja skaitlis ir pāra
        else:
            score -= 1  # Atņem punktu, ja skaitlis ir nepāra

        if number % 10 in [0, 5]:
            bank += 1  # Pievieno punktu bankai, ja skaitlis beidzas ar 0 vai 5

        # Vērtē gala rezultātu, ņemot vērā bankas punktus
        if score % 2 == 0:
            score -= bank   # atņem bankā uzkrātos punktus no kopēja punktu skaita, ja skaitlis ir pāra
        else:
            score += bank   # pieskaita bankā uzkrātos punktus kopējam punktu skaitam, ja skaitlis ir nepāra

        return score

    # minimax algoritms 
    def minimax(self, depth, maximizing_player):
        if depth == 0 or self.is_game_over(): # ja ir sasniegts 0 dzīļums vai spēlē beizdas tad izmanto hnf 
            return self.evaluate_heuristic()
        
        if maximizing_player:
            max_eval = float('-inf') # inicializēt ar negatīvā bezgalību, lai prioritizēt lielāku vai vienādu vērtību ka pirmo novērtējumu
            for number in [3, 4, 5]:
                if self.is_divisible(number):
                    self.current_number = number # maina tagadējo skaitli uz jaunu izveidoto
                    eval = self.minimax(depth - 1, False) # pārvieto uz vienu dziļumu zemāk spēles kokā, mainot uz cita spēlētāja (minimizētāju) gājienu 
                    self.current_number *= number # atjaunot spēles stāvokli pirms gājiena veikšanas
                    max_eval = max(max_eval, eval) # atjauno maksīmālo vērtību starp pašreizejo un iegūto novērtējuma vērtību   

                    self.visited_nodes += 1 # identifice apmeklēto virsotņi

            return max_eval
        else:
            min_eval = float('inf') # inicializēt ar negatīvā bezgalību, lai prioritizēt lielāku vai vienādu vērtību ka pirmo novērtējumu
            for number in [3, 4, 5]:
                if self.is_divisible(number):
                    self.current_number = number
                    eval = self.minimax(depth - 1, True) # pārvieto uz vienu dziļumu zemāk spēles kokā, mainot uz cita spēlētāja (maksimizētāju) gājienu 
                    self.current_number *= number
                    min_eval = min(min_eval, eval)

                    self.visited_nodes += 1

            return min_eval
        
    # alfa-beta lgoritms 
    def alphabeta(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.is_game_over():
            return self.evaluate_heuristic()

        if maximizing_player:
            max_eval = float('-inf')
            for number in [3, 4, 5]:
                if self.is_divisible(number):
                    self.current_number //= number
                    eval = self.alphabeta(depth - 1, alpha, beta, False)
                    self.current_number *= number
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:   # ja beta(min) ir mazāka vai vienāda ar alfa(max) vērtību, tad ir atradits labs vai vismaz labs gājiens 
                        break   # maksimizētājs ir atradis tikpat labu gājienu kā pašreizējais labākais minimizētāja gājiens

                    self.visited_nodes += 1
            return max_eval
        else:
            min_eval = float('inf')
            for number in [3, 4, 5]:
                if self.is_divisible(number):
                    self.current_number = number
                    eval = self.alphabeta(depth - 1, alpha, beta, True)
                    self.current_number *= number
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break

                    self.visited_nodes += 1
            return min_eval








# spēlēs lietotāja saskarne
def center_window(window, width=None, height=None):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

class GameGUI:
    def __init__(self, game):
        self.game = game
        self.window = ctk.CTk(fg_color=("#1b2631", "#212f3c"))
        self.custom_font = ctk.CTkFont(family="Arial", size=18)
        self.window.title("Divpersonu spēle")
        self.window.iconbitmap('345.ico')
        center_window(self.window, 500, 920)
        self.window.configure(bg='#f0f0f0')
        self.window.lift()
        self.selected_number_button = None
        self.selected_number = None  
        self.choose_number()
        self.create_widgets()
        self.create_score_labels()
        self.window.mainloop()

    # stils
    def create_widgets(self):

        # spēlēs visparīgais logs
        self.window.title("Divpersonu spēle")

        self.mainframe = ctk.CTkFrame(self.window)
        self.mainframe.configure(fg_color = "#212f3c", border_width = 1, border_color="#547ccb")
        
        self.buttons_frame = ctk.CTkFrame(self.window, width = 500)
        self.buttons_frame.configure(fg_color = "#34495e", border_width = 1, border_color="#547ccb")

        self.players_frame = ctk.CTkFrame(self.window)
        self.players_frame.configure(fg_color="#212f3c", border_width=0)
        self.players_frame.pack(pady=5)

        self.playersname_frame = ctk.CTkFrame(self.window)
        self.playersname_frame.configure(fg_color="#212f3c", border_width=0, width=228, height=28)
        self.playersname_frame.pack(pady=5)

        self.first_player_label = ctk.CTkLabel(self.players_frame, text="Pirmais spēlētajs", font=self.custom_font, text_color="#4763c3")
        self.first_player_label.pack(side="left", padx=10)

        self.second_player_label = ctk.CTkLabel(self.players_frame, text="Otrais spēlētajs", font=self.custom_font, text_color="#c35947")
        self.second_player_label.pack(side="right", padx=10)

        self.label = ctk.CTkLabel(self.buttons_frame, font = self.custom_font, text_color = "#84888e", text=f"Pašreizējais skaitlis: {self.game.current_number}")
        self.label.configure()
        self.label.pack(padx=19, pady=10)

        self.maingameframe = ctk.CTkFrame(self.window)
        self.maingameframe.configure(fg_color = "#212f3c", border_width = 1, border_color="#547ccb")
        
        self.buttons_frame.pack()
        self.maingameframe.pack(pady=5)

        self.player_label = ctk.CTkLabel(self.playersname_frame, text="Cilveks        Dators", font=self.custom_font, text_color="#84888e")
        self.player_label.pack(padx=25)

        self.button3 = ctk.CTkButton(self.buttons_frame, text="Dalīt ar 3", command=lambda: self.on_user_move(3))
        self.button3.configure(text_color="black", font=ctk.CTkFont("Arial", size=20, weight="bold"), fg_color="#50C878", hover_color="#079838", width=10, border_width=1, border_color="#547ccb")
        self.button3.pack(pady=5)

        self.button4 = ctk.CTkButton(self.buttons_frame, text="Dalīt ar 4", command=lambda: self.on_user_move(4))
        self.button4.configure(text_color="black", font=ctk.CTkFont("Arial", size=20, weight="bold"), fg_color="#50C878", hover_color="#079838", width=10, border_width=1, border_color="#547ccb")
        self.button4.pack(pady=5)
        
        self.button5 = ctk.CTkButton(self.buttons_frame, text="Dalīt ar 5", command=lambda: self.on_user_move(5))
        self.button5.configure(text_color="black", font=ctk.CTkFont("Arial", size=20, weight="bold"), fg_color="#50C878", hover_color="#079838", width=10, border_width=1, border_color="#547ccb")
        self.button5.pack(pady=5)

        self.reset_button = ctk.CTkButton(self.buttons_frame, text="Restartēt spēli", command=self.reset_game)
        self.reset_button.configure(width=40, height=45, text_color="white", font=("Arial", 20), fg_color="#3061bf", hover_color="#31559b", border_width=1, border_color="#547ccb")
        self.reset_button.pack(padx=60, pady=12)

        # spēlēš gājienu vēsture
        self.history_label = ctk.CTkLabel(self.maingameframe, text="Gājienu vēsture:", text_color = "#aeb6bf", font=self.custom_font)
        self.history_label.configure()
        self.history_label.pack(pady=5, padx=5)

        self.history_text = ctk.CTkTextbox(self.maingameframe, width=200, height=250)
        self.history_text.configure(font=("Arial", 17), text_color = "green", fg_color = "#0a141c", border_color="#547ccb", border_width=1, corner_radius=15)
        self.history_text.pack(padx=20, pady=10)

    # spēlēs punktu vērtības
    def create_score_labels(self):
        self.point_frame = ctk.CTkFrame(self.window)
        self.point_frame.configure(fg_color="#0a141c", border_width=1, border_color="#547ccb")
        self.point_frame.pack(pady=25)

        self.total_points_label = ctk.CTkLabel(self.point_frame, text="-----------------------------")
        self.total_points_label.configure(font=ctk.CTkFont("Arial", size=20, weight="bold"), text_color="white")
        self.total_points_label.pack(padx=20, pady=5)
        
        self.total_points_label = ctk.CTkLabel(self.point_frame, text=f"Kopējie punkti: {self.game.total_points}")
        self.total_points_label.configure(font=ctk.CTkFont("Arial", size=20, weight="bold"), text_color="#aeb6ff")
        self.total_points_label.pack(pady=5)

        self.plusminus_label = ctk.CTkLabel(self.point_frame, text=f"?")
        self.plusminus_label.configure(font=ctk.CTkFont("Arial", size=20, weight="bold"), text_color="#aeb6ff")
        self.plusminus_label.pack(pady=5)

        self.bank_points_label = ctk.CTkLabel(self.point_frame, text=f"Bankas punkti: {self.game.bank}")
        self.bank_points_label.configure(font=ctk.CTkFont("Arial", size=20, weight="bold"), text_color="#aeb6ff")
        self.bank_points_label.pack(pady=5)

        self.total_points_divider_label = ctk.CTkLabel(self.point_frame, text="====================")
        self.total_points_divider_label.configure(font=ctk.CTkFont("Arial", size=20, weight="bold"), text_color="white")
        self.total_points_divider_label.pack(padx=20, pady=5)

        self.final_points_label = ctk.CTkLabel(self.point_frame, text=f"Gala rezultats: {self.game.final_score}")
        self.final_points_label.configure(font=ctk.CTkFont("Arial", size=20, weight="bold"), text_color="#aeb6ff")
        self.final_points_label.pack(pady=5)

    def update_score_labels(self):
        tp_text = f"Kopējie punkti: {self.game.total_points}"
        tp_color = "#4763c3" if self.game.total_points % 2 == 0 else "#c35947"

        self.total_points_label.configure(text=tp_text, text_color=tp_color)
        self.bank_points_label.configure(text=f"Bankas punkti: {self.game.bank}")
    
    def update_labels_and_buttons(self):
        self.label.configure(text=f"Pašreizējais skaitlis: {self.game.current_number}")
        self.update_buttons()
        self.update_score_labels()

    def update_buttons(self):
        for button, number in [(self.button3, 3), (self.button4, 4), (self.button5, 5)]:
            if self.game.is_divisible(number):
                button.configure(fg_color="#50C878", text_color="black", state="normal") #green
            else:
                button.configure(fg_color="#DC143C", text_color="black", state="disabled") #red
    
    # spēlēs pirmās vērtības izvēles un spēlēs opciju logs
    def choose_number(self):

        # nodrošina, ka darbojas tikai viens augstākā līmeņa (choose_number_window) vērtības izvēles logs
        if not hasattr(self, 'toplevel_windows'):
            self.toplevel_windows = []

        for choose_number_window in self.toplevel_windows:
            choose_number_window.destroy()
        self.toplevel_windows = []

        choose_button_style = {'text_color': 'white', 'font':self.custom_font, 'fg_color': '#3061bf', 'hover_color':'#31559b', 'width':10, 'border_width':1, 'border_color':"#547ccb"}
        self.window.update()

        ctk.set_default_color_theme("dark-blue")
        choose_number_window = tk.Toplevel(self.window, bg = "#1b2631")
        center_window(choose_number_window, 300, 560)
        choose_number_window.iconbitmap('345.ico')
        self.toplevel_windows.append(choose_number_window)

        self.mainframe = ctk.CTkFrame(choose_number_window)
        self.mainframe.configure(fg_color = "#212f3c", border_width = 1, border_color="#547ccb")
        
        self.tabview = ctk.CTkTabview(self.mainframe, width=300)
        self.tabview.configure(width = 150, height = 150, border_width = 1, text_color="white", border_color = "#547ccb", fg_color="#34495e", segmented_button_fg_color="#212f3c", segmented_button_selected_color="#3061bf", segmented_button_selected_hover_color="#31559b", segmented_button_unselected_color="#212f3c", segmented_button_unselected_hover_color = "#34595e")
        self.tabview.add("Izvelet")
        self.tabview.add("Ievadit")
        self.tabview.tab("Ievadit").grid_columnconfigure(0, weight=5)  
        self.tabview.tab("Izvelet").grid_columnconfigure(0, weight=1)
        self.tabview.pack()

        self.insertnumber = ctk.CTkLabel(self.tabview.tab("Ievadit"), text="Ievadiet skaitli (40000 - 50000):")
        self.insertnumber.configure(font=("Arial", 18), text_color="#84888e")
        self.insertnumber.pack()

        number_entry = ctk.CTkEntry(self.tabview.tab("Ievadit"))
        number_entry.configure(font=("Arial", 16), text_color="#aeb6bf", fg_color="#34495e", border_color = "#547ccb", border_width=1)
        number_entry.pack(pady=20)

        # izvelet skaitļu
        def create_button(number):
            button = ctk.CTkButton(self.tabview.tab("Izvelet"), text=str(number))
            button.configure(**choose_button_style, command=lambda n=number, btn=button: select_number(n, btn))
            button.pack(pady=1)
            return button

        # saglabātu atlasīto numuru
        def select_number(number, button):
            if self.selected_number_button:
                self.selected_number_button.configure(text_color = "white", fg_color="#3061bf", hover_color="#31559b")
            self.selected_number = number
            self.selected_number_button = button
            button.configure(text_color = "black", fg_color="#50C879", hover_color="#079838")
            update_cancel_button()
        
        def cancel_choice():
            if self.selected_number_button:
                self.selected_number_button
                self.selected_number = None
                update_cancel_button()
                reset_button_colors()

        def update_cancel_button(): 
            if self.selected_number is not None:
                cancel_button.pack(pady=10)
            else:
                cancel_button.pack_forget()

        def reset_button_colors():
            for button in button_list:
                button.configure(text_color = "white", fg_color="#3061bf", hover_color="#31559b")

        cancel_button = ctk.CTkButton(self.tabview.tab("Izvelet"), text="Atcelt izvēli", command=cancel_choice, **choose_button_style)     
        self.textstartchoose=ctk.CTkLabel(self.tabview.tab("Izvelet"), text="Izvēlies sākuma skaitli")
        self.textstartchoose.configure(font=("Arial", 18), text_color="#84888e")
        self.textstartchoose.pack()

        button_list = []
        for number in self.game.starting_numbers:
            btn = create_button(number)
            button_list.append(btn)
        self.mainframe.pack()
        self.whoplays=ctk.CTkLabel(self.mainframe, text="Kurš sāk spēli:")
        self.whoplays.configure(font=("Arial", 18), text_color="#aeb6bf")
        self.whoplays.pack(pady=5)

        starter_var = tk.IntVar(value=0)
        
        # saglabāt spēles pirmo vērtību un izvēlētās spēles opcijas
        def on_submit():
            try:
                if self.selected_number is not None and number_entry.get(): # parbauda vai ir izvēlētas abas opcijas 
                    tk.messagebox.showerror("Kļūda", "Var izvēlet tikai vienu opciju - vai ievadiet skaitli pats, vai izvēlet no ģenerētajiem skaitļiem.")
                    self.reset_game()
                # pārbaudīt, vai ir izvēlēts skaitlis no saģēnerētam opcijam vai skaitļu ir uzrakstījis lietotājs 
                elif self.selected_number is not None:  # vai ir izvēlēts skaitlis 
                    number = self.selected_number
                else:  # vai ir uzrakstits
                    number = int(number_entry.get())
                    
                if 40000 <= number <= 50000: 
                    if number % 3 == 0 and number % 4 == 0 and number % 5 == 0: 
                        self.game.set_starting_number(number)
                        self.game.current_player = Player(starter_var.get())
                        choose_number_window.destroy()
                        self.update_labels_and_buttons()
                        if self.game.current_player == Player.COMPUTER:
                            self.computer_move() 
                    else:
                        tk.messagebox.showerror("Kļūda", "Skaitlim jābūt dalāmam ar 3, 4 un 5 bez atlikuma.")
                        self.choose_number() 
                else:
                    tk.messagebox.showerror("Kļūda", "Skaitlim jābūt diapazonā no 40000 līdz 50000.")
                    self.choose_number() 
            except ValueError:
                tk.messagebox.showerror("Kļūda", "Ievadiet derīgu veselu skaitli.")
                self.choose_number() 

        def set_pl_labels_positions():
            if starter_var.get() == 0:  # ja player radio poga
                self.player_label.configure(text="Cilveks        Dators")
               
            else:  # ja dators radio poga
                self.player_label.configure(text="Dators        Cilveks")

        self.gamer=ctk.CTkRadioButton(self.mainframe, text="Cilveks", variable=starter_var, value=0, command=set_pl_labels_positions)
        self.gamer.configure(font=("Arial", 16), text_color="#aeb6ff")
        self.gamer.pack(pady=5)

        self.pc=ctk.CTkRadioButton(self.mainframe, text="Dators", variable=starter_var, value=1, command=set_pl_labels_positions)
        self.pc.configure(font=("Arial", 16), text_color="#aeb6ff")
        self.pc.pack(pady=5)

        self.choosealgorithm = ctk.CTkLabel(self.mainframe, text="Izvēlieties algoritmu:")
        self.choosealgorithm.configure(font=("Arial", 18), text_color="#aeb6bf")
        self.choosealgorithm.pack(pady=5)

        self.algorithm_var = tk.StringVar(value="minimax")
        self.mini = ctk.CTkRadioButton(self.mainframe, text="Minimax", variable=self.algorithm_var, value="minimax")
        self.mini.configure(font=("Arial", 16), text_color="#aeb3ff")
        self.mini.pack(pady=5)

        self.alfa= ctk.CTkRadioButton(self.mainframe, text="Alpha-Beta", variable=self.algorithm_var, value="alphabeta")
        self.alfa.configure(font=("Arial", 16), text_color="#aeb3ff")
        self.alfa.pack(pady=5)

        start_button=ctk.CTkButton(self.mainframe, text="Sākt spēli", command=on_submit, **choose_button_style)
        start_button.configure(width=40, height=45)
        start_button.pack(pady=15)

    def show_final_message(self, final_message):

        result_window = ctk.CTkToplevel(self.window)
        self.window.title("Divpersonu spēle")
        center_window(result_window, 300, 100)
        ctk.CTkLabel(result_window, text=final_message).pack(pady=10)

        def restart_game():
            result_window.destroy()
            self.reset_game()

        def close_result_window():
            result_window.destroy()

        tk.Button(result_window, text="Sākt vēlreiz", command=restart_game).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(result_window, text="Pabeigt", command=close_result_window).pack(side=tk.RIGHT, padx=10, pady=10)

    def add_end_game_buttons(self):
        self.restart_button = tk.Button(self.window, text="Sākt vēlreiz", command=self.reset_game)
        self.restart_button.pack(pady=5)

        def close_program():
            self.window.destroy()

        self.exit_button = tk.Button(self.window, text="Pabeigt", command=close_program)
        self.exit_button.pack(pady=5)

    def reset_game(self):
        self.game = Game()
        self.selected_number = None
        self.selected_number_button = None
        self.plusminus_label.configure(text =f"?")
        self.final_points_label.configure(font=ctk.CTkFont("Arial", size=20, weight="bold"), text_color="#aeb6ff", text=f"Gala rezultats: 0")
        self.player_label.configure(text="Cilveks        Dators")
        self.player_label.configure(text="Cilveks        Dators")
        self.update_history()
        self.choose_number()
        self.update_labels_and_buttons()
        if hasattr(self, 'restart_button'):
            self.restart_button.destroy()
            self.exit_button.destroy()
        if hasattr(self.choose_number, 'choose_number_window'):
            tk.Toplevel(self.window).destroy()

    def show_final_results(self, winner_message):
        print("Move times:", self.game.move_times)
        average_move_time = sum(self.game.move_times) / len(self.game.move_times) if self.game.move_times else 0
        visited_nodes = self.game.visited_nodes

        additional_message = f"\nDatora vidējais laiks gājienu izpildei: {average_move_time:.2f} sek.\nApmeklēto virsotņu skaits: {visited_nodes}"
        final_message = winner_message + additional_message
        messagebox.showinfo("Spēle beigusies", final_message)
        self.reset_game()

    def on_user_move(self, number):
        try:
            self.game.make_move(number)
            self.update_labels_and_buttons()
            self.update_history()
            if not self.game.is_game_over():
                self.computer_move()
            else:
                self.game.calculate_final_score()
                if self.game.total_points % 2 == 0:
                    self.plusminus_label.configure(text =f"-")
                else:
                    self.plusminus_label.configure(text =f"+")

                gr_text = f"Gala rezultats: {self.game.final_score}"
                gr_color = "#4763c3" if self.game.final_score % 2 == 0 else "#c35947"
                self.final_points_label.configure(text=gr_text, text_color=gr_color)

                final_message = "Jūs uzvarējāt!" if self.game.final_score % 2 == 0 else "Dators uzvarēja!"
                self.show_final_results(final_message)
                self.reset_game()
        except ValueError:
            messagebox.showerror("Kļūda", "Nederīgs gājiens")

    def computer_move(self):
        start_time = time.perf_counter()

        best_move = None
        best_eval = float('-inf')
        for number in [3, 4, 5]:
            if self.game.is_divisible(number):
                original_number = self.game.current_number
                self.game.current_number = number
                eval = self.game.minimax(3, False)
                self.game.current_number = original_number
                if eval > best_eval:
                    best_eval = eval
                    best_move = number
        if best_move is not None:
            self.game.make_move(best_move)
            self.update_labels_and_buttons()
            self.update_history()

            eval_time = time.perf_counter() - start_time
            self.game.move_times.append(eval_time)

            if self.game.is_game_over():
                self.game.calculate_final_score()
                if self.game.total_points % 2 == 0:
                    self.plusminus_label.configure(text =f"-")
                else:
                    self.plusminus_label.configure(text =f"+")

                gr_text = f"Gala rezultats: {self.game.final_score}"
                gr_color = "#4763c3" if self.game.final_score % 2 == 0 else "#c35947"
                self.final_points_label.configure(text=gr_text, text_color=gr_color)

                final_message = "Dators uzvarēja!" if self.game.final_score % 2 == 0 else "Jūs uzvarējāt!"
                self.show_final_results(final_message)
                self.reset_game()
        else:
            messagebox.showerror("Kļūda", "Dators nevarēja veikt gājienu")

    def update_history(self):
        self.history_text.delete(1.0, tk.END)
        first_player = self.game.moves_history[0][0] if self.game.moves_history else None
        
        if first_player == Player.USER:
            user_color = "#4763c3"
            computer_color = "#c35947"
        else:
            user_color = "#c35947"
            computer_color = "#4763c3"

        for player, move in self.game.moves_history:
            player_name = "Lietotājs" if player == Player.USER else "Dators"
            color = user_color if player == Player.USER else computer_color
            self.history_text.insert(tk.END, f"{player_name} ", f"{player_name}_color")
            self.history_text.insert(tk.END, f"dalīja ar {move}\n")
            self.history_text.tag_config(f"{player_name}_color", foreground=color)


if __name__ == "__main__":
    game = Game()
    gui = GameGUI(game)