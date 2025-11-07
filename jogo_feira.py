import cv2
import time
import random
import numpy as np
from ultralytics import YOLO
import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk

# --- Configurações do Jogo ---
ROUND_DURATION = 30  # Duração de cada round em segundos
TOTAL_ROUNDS = 5     # O jogo terá 5 rounds
CONFIDENCE_THRESHOLD = 0.35  # 35% de confiança (bom para o modelo 's')
MODEL_NAME = 'yolov8s.pt'  # O equilíbrio perfeito! 's' (Small)

# 1. Dicionário de objetos para o jogo (SÓ COISAS FÁCEIS E QUE O MODELO CONHECE)
translations = {
    'teddy bear': 'Ursinho',
    'cell phone': 'Celular',
    'mouse': 'Mouse', # TROCADO: Banana era ruim de levar
    'keyboard': 'Teclado', # ADICIONADO
    'bottle': 'Garrafa',
    'cup': 'Copo',
    'remote': 'Controle Remoto',
    'scissors': 'Tesoura'
}

# --- Classe Principal do Aplicativo (Tkinter) ---
class YoloGameApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Caça ao Objeto - Feira de Profissões")

        # --- Variáveis do Jogo ---
        self.game_state = "MENU"  # "MENU", "PLAYING", "GAME_OVER"
        self.score = 0 # Agora conta os rounds vencidos
        self.start_time = 0
        self.time_left = ROUND_DURATION
        self.current_round = 0
        self.target_object = ""
        self.target_display_name = ""

        # --- Carregar Recursos ---
        print("Carregando modelo YOLO... (Isso pode demorar um pouco na primeira vez)")
        self.model = YOLO(MODEL_NAME)
        self.class_names = self.model.names
        print("Modelo carregado.")
        
        # Inicializar a Webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Erro: Não foi possível abrir a webcam.")
            return
            
        # Pega as dimensões da câmera
        self.cam_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.cam_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Cria a camada preta (overlay) que será usada para escurecer
        self.black_overlay = np.zeros((self.cam_height, self.cam_width, 3), dtype=np.uint8)

        # --- Modo Tela Cheia ---
        self.root.attributes('-fullscreen', True)
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.bind('<Escape>', self.close_fullscreen)


        # --- Interface Gráfica (Tkinter) ---
        
        # Estilos de fonte
        self.title_font = tkFont.Font(family="Helvetica", size=24, weight="bold")
        self.status_font = tkFont.Font(family="Helvetica", size=18)
        self.target_font = tkFont.Font(family="Helvetica", size=32, weight="bold")
        self.button_font = tkFont.Font(family="Helvetica", size=16)

        # Frame Principal
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Label para o Vídeo
        self.video_label = tk.Label(self.main_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # --- Telas (Frames sobrepostos) ---
        self.create_menu_screen()
        self.create_game_screen() # Isso agora só CRIA os elementos, não os mostra
        self.create_game_over_screen()

        # Iniciar o loop do vídeo
        self.update_frame()

    # --- Funções de Tela ---

    def create_menu_screen(self):
        self.menu_frame = tk.Frame(self.main_frame, bg='black')
        
        tk.Label(self.menu_frame, text="Caça ao Objeto!", font=self.title_font, fg="white", bg="black").pack(pady=(100, 20))
        tk.Label(self.menu_frame, text="Encontre o objeto pedido antes que o tempo acabe!", font=self.status_font, fg="white", bg="black").pack(pady=20)
        
        self.start_button = tk.Button(self.menu_frame, text="INICIAR", font=self.button_font, bg="#4CAF50", fg="white", command=self.start_game)
        self.start_button.pack(pady=50, padx=50, ipady=10, ipadx=10)
        
        tk.Label(self.menu_frame, text="Pressione 'Esc' a qualquer momento para sair.", font=self.status_font, fg="gray", bg="black").pack(side=tk.BOTTOM, pady=10)

    def create_game_screen(self):
        self.status_bar = tk.Frame(self.main_frame, bg="#333")
        
        self.time_label = tk.Label(self.status_bar, text=f"Tempo: {self.time_left}", font=self.status_font, fg="white", bg="#333", width=15)
        self.time_label.pack(side='left', padx=20, pady=10)
        
        self.score_label = tk.Label(self.status_bar, text="Pontos: 0", font=self.status_font, fg="white", bg="#333", width=15)
        self.score_label.pack(side='right', padx=20, pady=10)

        self.round_label = tk.Label(self.status_bar, text="Round: 0 / 5", font=self.status_font, fg="white", bg="#333")
        self.round_label.pack(side='left', fill='x', expand=True)

        self.target_frame = tk.Frame(self.main_frame, bg="#000000") # Barra de alvo
        
        self.target_label = tk.Label(self.target_frame, text="Procure por:", font=self.title_font, fg="white", bg="#000000")
        self.target_label.pack(pady=(10, 0))
        self.target_object_label = tk.Label(self.target_frame, text="...", font=self.target_font, fg="yellow", bg="#000000")
        self.target_object_label.pack(pady=(0, 10))

    def create_game_over_screen(self):
        self.game_over_frame = tk.Frame(self.main_frame, bg='black')
        
        tk.Label(self.game_over_frame, text="Jogo Finalizado!", font=self.title_font, fg="red", bg="black").pack(pady=(100, 20))
        # --- ALTERAÇÃO AQUI ---
        # Texto padrão atualizado para a nova lógica
        self.final_score_label = tk.Label(self.game_over_frame, text=f"Você encontrou 0 de {TOTAL_ROUNDS} objetos!", font=self.status_font, fg="white", bg="black")
        self.final_score_label.pack(pady=20)
        
        self.restart_button = tk.Button(self.game_over_frame, text="JOGAR NOVAMENTE", font=self.button_font, bg="#4CAF50", fg="white", command=self.start_game)
        self.restart_button.pack(pady=50, padx=50, ipady=10, ipadx=10)

        tk.Label(self.game_over_frame, text="Pressione 'Esc' para sair.", font=self.status_font, fg="gray", bg="black").pack(side=tk.BOTTOM, pady=10)

    # --- Funções de Lógica do Jogo ---

    def start_game(self):
        # Reseta o estado do jogo
        self.score = 0
        self.current_round = 1
        self.score_label.config(text=f"Pontos: {self.score}")
        self.start_new_round()

    def start_new_round(self):
        print(f"Iniciando round {self.current_round}")
        self.round_label.config(text=f"Round: {self.current_round} / {TOTAL_ROUNDS}")
        self.start_time = time.time()
        self.time_left = ROUND_DURATION
        self.time_label.config(text=f"Tempo: {self.time_left}")
        self.get_new_target()
        self.game_state = "PLAYING"

    def get_new_target(self):
        # Garante que o novo alvo seja diferente do anterior
        new_target, new_display_name = random.choice(list(translations.items()))
        while new_target == self.target_object:
            new_target, new_display_name = random.choice(list(translations.items()))
            
        self.target_object = new_target
        self.target_display_name = new_display_name
        
        self.target_object_label.config(text=self.target_display_name)
        print(f"Novo alvo: {self.target_display_name}")

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self.update_frame) # Tenta ler de novo
            return

        frame = cv2.flip(frame, 1) # Espelha a câmera
        
        # Garante que o black_overlay tenha o mesmo tamanho do frame (antes do resize)
        if frame.shape[0] != self.black_overlay.shape[0] or frame.shape[1] != self.black_overlay.shape[1]:
             self.black_overlay = np.zeros((frame.shape[0], frame.shape[1], 3), dtype=np.uint8)

        # Lógica de atualização baseada no estado do jogo
        if self.game_state == "PLAYING":
            self.process_playing_frame(frame)
            self.update_timer()
        
        elif self.game_state == "GAME_OVER":
            # Esconde todos os frames de jogo e mostra o de fim de jogo
            self.status_bar.place_forget()
            self.target_frame.place_forget()
            self.menu_frame.place_forget()
            self.game_over_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=1, relheight=1)
            
            # Deixa o vídeo escurecido no fundo
            frame = cv2.addWeighted(frame, 0.3, self.black_overlay, 0.7, 0)

        elif self.game_state == "MENU":
            # Esconde todos os frames de jogo e mostra o de menu
            self.status_bar.place_forget()
            self.target_frame.place_forget()
            self.game_over_frame.place_forget()
            self.menu_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=1, relheight=1)

            # Deixa o vídeo escurecido no fundo
            frame = cv2.addWeighted(frame, 0.3, self.black_overlay, 0.7, 0)
        
        # Redimensiona o frame para preencher a tela
        frame = cv2.resize(frame, (self.screen_width, self.screen_height))

        # Converte o frame do OpenCV para o Tkinter
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)

        self.video_label.imgtk = img_tk
        self.video_label.configure(image=img_tk)

        # Chama a si mesmo para o próximo frame
        self.root.after(10, self.update_frame)

    def process_playing_frame(self, frame):
        # Mostra a UI do jogo
        self.menu_frame.place_forget()
        self.game_over_frame.place_forget()
        
        # Coloca a UI do jogo no lugar
        self.status_bar.place(x=0, y=0, relwidth=1)
        self.target_frame.place(x=0, rely=1, relwidth=1, anchor='sw') # bota no canto inferior

        # Realiza a detecção
        results = self.model(frame, stream=True, conf=CONFIDENCE_THRESHOLD, verbose=False)

        target_found_this_frame = False

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                detected_name = self.class_names[cls_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # LÓGICA DO JOGO: Checa se o objeto é o alvo
                if detected_name == self.target_object:
                    target_found_this_frame = True
                    # Desenha caixa VERDE (destaque)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
                    cv2.putText(frame, "ENCONTRADO!", (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                else:
                    # Desenha caixas NORMAIS (Roxo)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)

        # --- LÓGICA DO JOGO ALTERADA ---
        # Se o alvo foi encontrado, o round ACABA e vamos para o próximo.
        if target_found_this_frame:
            self.score += 1
            self.score_label.config(text=f"Pontos: {self.score}")
            print(f"Encontrado! Pontos: {self.score}. Indo para o próximo round.")
            
            self.current_round += 1
            if self.current_round > TOTAL_ROUNDS:
                self.game_state = "GAME_OVER"
                # Atualiza a tela final com a pontuação de vitória
                self.final_score_label.config(text=f"Parabéns! Você encontrou {self.score} de {TOTAL_ROUNDS} objetos!")
            else:
                self.start_new_round() # Reseta o timer e pega um novo alvo

    def update_timer(self):
        # Só atualiza o timer se estivermos jogando
        if self.game_state != "PLAYING":
            return

        elapsed = time.time() - self.start_time
        self.time_left = max(0, int(ROUND_DURATION - elapsed))
        self.time_label.config(text=f"Tempo: {self.time_left}")

        # --- LÓGICA DO JOGO ALTERADA ---
        # Se o tempo acabar, você "perde" o round e passa para o próximo.
        if self.time_left == 0:
            print(f"Tempo esgotado! Não encontrou {self.target_display_name}.")
            
            self.current_round += 1
            if self.current_round > TOTAL_ROUNDS:
                self.game_state = "GAME_OVER"
                # Atualiza a tela final com a pontuação
                self.final_score_label.config(text=f"Tempo esgotado! Você encontrou {self.score} de {TOTAL_ROUNDS} objetos.")
            else:
                self.start_new_round()

    def on_close(self):
        # Para a câmera e fecha a janela
        print("Fechando...")
        self.cap.release()
        self.root.destroy()

    def close_fullscreen(self, event=None):
        print("Saindo do modo tela cheia...")
        self.root.attributes('-fullscreen', False)
        # Bugar o Esc para fechar o app se for pressionado de novo
        self.root.bind('<Escape>', lambda e: self.on_close())

# --- Executar o Aplicativo ---
if __name__ == "__main__":
    root = tk.Tk()
    app = YoloGameApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close) # Para fechar corretamente
    root.mainloop()
