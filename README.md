Jogo "Caça ao Objeto" com IA (YOLOv8)

Este é um jogo interativo de webcam criado para a Feira de Profissões. O jogo usa o modelo de Inteligência Artificial YOLOv8 para desafiar os jogadores a encontrarem objetos do dia a dia em tempo real.

🎮 Como Funciona

O jogo começa em tela cheia.

Clique em INICIAR.

O jogo tem 5 rounds.

A cada round, o jogo pedirá um objeto aleatório (ex: "Livro").

Você tem 30 segundos para encontrar o objeto e mostrá-lo para a webcam.

Se encontrar a tempo, você ganha um ponto e avança para o próximo round.

Se o tempo acabar, você não ganha o ponto e avança para o próximo round.

No final, ele mostra sua pontuação (quantos objetos você encontrou de 5).

📋 Lista de Objetos

O jogo só vai pedir objetos que a IA foi treinada para reconhecer. Prepare estes itens:

Ursinho

Livro

Celular

Mochila

Garrafa

Copo

Controle Remoto

Tesoura

💻 Como Instalar e Rodar (Guia para sua amiga)

Para rodar este projeto no seu notebook, você só precisa ter o Python instalado.

Requisito: Python 3.10 ou Python 3.11. (Versões mais novas como 3.12+ ou mais antigas podem dar erro na instalação).

Passo 1: Baixar o Projeto (Clone)

No seu terminal (CMD, PowerShell ou Git Bash), rode:

git clone [COLE O LINK DO SEU REPOSITÓRIO AQUI]
cd [NOME-DO-SEU-REPOSITORIO]


Passo 2: Criar o Ambiente Virtual

É essencial criar um ambiente virtual para não bagunçar o Python da sua máquina.

# Rode este comando (usando python 3.11, por exemplo)
py -3.11 -m venv env_jogo


Passo 3: Ativar o Ambiente

# No Windows (PowerShell)
.\env_jogo\Scripts\Activate.ps1

# No Windows (CMD)
.\env_jogo\Scripts\activate


O seu terminal deve mostrar (env_jogo) no início da linha.

Passo 4: Instalar as Dependências

Agora, vamos instalar tudo que o jogo precisa com um só comando (ele vai ler o arquivo requirements.txt):

pip install -r requirements.txt


Isso pode demorar alguns minutos, pois ele vai baixar o opencv e o ultralytics.

Passo 5: Rodar o Jogo!

Pronto! Agora é só executar:

python jogo_feira.py


O jogo deve abrir em tela cheia. Pressione Esc a qualquer momento para sair.

⚠️ Solução de Problemas

Jogo muito lento (travando): Se o notebook não tiver uma boa placa de vídeo, o modelo yolov8s.pt pode ser pesado.

Solução: Abra o arquivo jogo_feira.py, vá para a linha 11 e mude MODEL_NAME para o modelo "nano", que é muito mais leve:

MODEL_NAME = 'yolov8n.pt'
