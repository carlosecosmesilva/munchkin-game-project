# Munchkin Python Game

**Munchkin Online** é uma implementação do popular jogo de cartas _Munchkin_ programado em Python, utilizando a biblioteca **Pygame**. O jogo permite que até 10 jogadores participem de partidas online ou locais, simulando a experiência do jogo físico. A versão atual já permite realizar partidas normalmente, com melhorias planejadas para o futuro.

## Descrição

O objetivo do jogo é enfrentar monstros, coletar tesouros e evoluir, com o suporte a até 6 jogadores. As partidas podem ser realizadas localmente ou online, permitindo que jogadores humanos joguem contra outros jogadores ou uma IA.

### Funcionalidades

-   **Jogabilidade**: Suporte para até 6 jogadores humanos, com a possibilidade de jogar contra a IA.
-   **Sistema de Cartas**: Cartas de Porta, Tesouro, Classe e Raça, cada uma com habilidades e bônus específicos.
-   **IA**: A IA é capaz de tomar decisões e interagir com o jogo.
-   **Inventário**: Sistema de gerenciamento de itens para armazenar e usar tesouros coletados.

## O Jogo Possui 6 Áreas Distintas:

1. **Table**: Área onde os jogadores batalham e jogam cartas. Inclui contadores de bônus.
2. **Players**: Exibe informações dos jogadores conectados, como nome, nível e número de cartas.
3. **Equipments**: Exibe os equipamentos e maldições de cada jogador, visíveis para todos.
4. **Hand**: Área exclusiva de cada jogador onde são visualizadas as cartas que estão na mão.
5. **Deck**: Contém 4 pilhas para as cartas de porta, tesouro e seus descartes.
6. **Logs**: Exibe os registros das últimas ações realizadas, com um simulador de dados.

## Comandos

| Comando                     |                         Ação                         |
| --------------------------- | :--------------------------------------------------: |
| Botão esquerdo mouse        |                  Segura uma carta\*                  |
| Soltar botão esquerdo mouse |                 Solta uma carta\*\*                  |
| Botão direito mouse         |              Vira a face de uma carta\*              |
| D                           |                Descartar uma carta\*                 |
| V                           |          Exibe a carta com tamanho maior\*           |
| Números                     |       Altera o nível do próprio jogador\*\*\*        |
| reset12345                  | Retorna todas as cartas do jogo às pilhas do baralho |
| reset54321                  |  Retorna as cartas do descarte às pilhas do baralho  |

\* O cursor do mouse deve estar em cima da carta para ter efeito  
\*\* O jogador deve estar segurando uma carta para a ação ter efeito  
\*\*\* O cursor do mouse deve estar na área Players

## Instruções para Execução do Jogo

### LOCALMENTE

**Iniciando o servidor**:  
No arquivo `server.py`, descomente as linhas 12 e 13, configurando o IP da sua rede e o número da porta (por padrão, a porta é 5555). Depois, execute o arquivo `server.py` com o Python 3.

**Iniciando o cliente**:  
No arquivo `conf.txt`, insira seu nome na primeira linha, o IP da sua rede na segunda e a porta na terceira. O cliente pode ser iniciado através do executável `client.exe` (gerado pelo PyInstaller) ou pelo código `client.py`, sendo necessário instalar a biblioteca Pygame para rodar o código.

### ONLINE

**Iniciando o servidor**:  
Para jogar online, hospede o servidor na nuvem. Aqui está como fazer isso no **Google Cloud Platform (GCP)**:

1. Acesse a ferramenta **Compute Engine** no GCP e crie uma nova instância de VM.
2. Na VM criada, acesse o terminal via SSH e crie o arquivo `server.py`.
3. Execute o servidor na VM com o comando:
    ```bash
    python3 server.py
    ```

**Iniciando o cliente**:  
No arquivo `conf.txt`, insira seu nome, o IP externo da VM e a porta (3389). O cliente pode ser executado pelo executável `client.exe` ou pelo código `client.py`.

### Requisitos

-   Python 3.9 ou superior.
-   Pygame (para execução do código).

### Como Executar o Jogo

1. Clone o repositório:
    ```bash
    git clone https://github.com/seuusuario/munchkin-python-game.git
    cd munchkin-python-game
    ```
2. Execute o jogo:
    ```bash
    python main.py
    ```

### Agradecimentos

Agradecemos ao **Steve Jackson**, criador do jogo Munchkin, e ao **Tim Ruscica** do site [TechWithTim](https://www.techwithtim.net/tutorials/python-online-game-tutorial/) pela inspiração e suporte na implementação do jogo online.

## Contribuição

Contribuições são bem-vindas! Abra uma _issue_ para sugestões e envie _pull requests_ para melhorias.