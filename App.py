import streamlit as st

st.set_page_config(page_title="EXV Mini-Games", page_icon="🎮", layout="centered")

st.title("🎮 EXV Mini-Games")
st.write("Bem-vindo ao portal de jogos da turma! Escolha um jogo no menu abaixo.")

# Menu de seleção de jogos
jogo_escolhido = st.selectbox(
    "O que você quer jogar agora?",
    ["Selecione um jogo...", "❌ Jogo da Velha", "🔤 Jogo da Forca", "💡 Meu Jogo Inventado"]
)

# -------------------------------------------------------------------
# LÓGICA DO JOGO DA VELHA VERSÃO HASHTAG (#)
# -------------------------------------------------------------------
if jogo_escolhido == "❌ Jogo da Velha":
    st.header("❌ Jogo da Velha ⭕")
    
    # Inicializa o tabuleiro na memória
    if "tabuleiro" not in st.session_state:
        st.session_state.tabuleiro = [" "] * 9
        st.session_state.turno = "X"
        st.session_state.vencedor = None

    def verificar_vencedor():
        t = st.session_state.tabuleiro
        linhas_vitoria = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # Horizontais
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # Verticais
            [0, 4, 8], [2, 4, 6]             # Diagonais
        ]
        for linha in linhas_vitoria:
            if t[linha[0]] == t[linha[1]] == t[linha[2]] != " ":
                return t[linha[0]]
        if " " not in t:
            return "Empate"
        return None

    def clique_botao(index):
        if st.session_state.tabuleiro[index] == " " and not st.session_state.vencedor:
            st.session_state.tabuleiro[index] = st.session_state.turno
            vencedor = verificar_vencedor()
            if vencedor:
                st.session_state.vencedor = vencedor
            else:
                st.session_state.turno = "O" if st.session_state.turno == "X" else "X"

            # --- MONTAGEM DO TABULEIRO # COM FORÇADO PARA CELULAR ---
    # Esse bloco injeta um código invisível que obriga as colunas a ficarem lado a lado no celular
    st.markdown(
        """
        <style>
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Agora desenhamos o tabuleiro usando o mesmo estilo
    for i in range(3):
        cols = st.columns(3)
        for j in range(3):
            index = i * 3 + j
            txt_botao = st.session_state.tabuleiro[index]
            label = txt_botao if txt_botao != " " else "  "
            
            cols[j].button(
                label, 
                key=f"b_{index}", 
                on_click=clique_botao, 
                args=(index,), 
                use_container_width=True
            )
        
        if i < 2:
            st.markdown("---")
                 
    # Linha 2 do #
    col4, col5, col6 = st.columns(3)
    with col4: st.button(st.session_state.tabuleiro[3] if st.session_state.tabuleiro[3] != " " else "  ", key="b3", on_click=clique_botao, args=(3,), use_container_width=True)
    with col5: st.button(st.session_state.tabuleiro[4] if st.session_state.tabuleiro[4] != " " else "  ", key="b4", on_click=clique_botao, args=(4,), use_container_width=True)
    with col6: st.button(st.session_state.tabuleiro[5] if st.session_state.tabuleiro[5] != " " else "  ", key="b5", on_click=clique_botao, args=(5,), use_container_width=True)
    
    st.markdown("---") # Outra linha horizontal do #

    # Linha 3 do #
    col7, col8, col9 = st.columns(3)
    with col7: st.button(st.session_state.tabuleiro[6] if st.session_state.tabuleiro[6] != " " else "  ", key="b6", on_click=clique_botao, args=(6,), use_container_width=True)
    with col8: st.button(st.session_state.tabuleiro[7] if st.session_state.tabuleiro[7] != " " else "  ", key="b7", on_click=clique_botao, args=(7,), use_container_width=True)
    with col9: st.button(st.session_state.tabuleiro[8] if st.session_state.tabuleiro[8] != " " else "  ", key="b8", on_click=clique_botao, args=(8,), use_container_width=True)
    
    st.write("") # Espaço em branco

    # Mostra o status do jogo
    if st.session_state.vencedor:
        if st.session_state.vencedor == "Empate":
            st.info("Deu Velha! Empate! 🤝")
        else:
            st.success(f"🎉 O jogador '{st.session_state.vencedor}' venceu!")
    else:
        st.write(f"Vez do jogador: **{st.session_state.turno}**")

    # Botão para reiniciar
    if st.button("Reiniciar Jogo"):
        st.session_state.tabuleiro = [" "] * 9
        st.session_state.turno = "X"
        st.session_state.vencedor = None
        st.rerun()
                                                                                                                                                 
# -------------------------------------------------------------------
# LÓGICA DO JOGO DA FORCA
# -------------------------------------------------------------------
elif jogo_escolhido == "🔤 Jogo da Forca":
    st.header("🔤 Jogo da Forca EXV")
    
    import random

    # 1. Lista de palavras secretas da turma (Pode alterar ou adicionar mais!)
    if "lista_palavras" not in st.session_state:
        st.session_state.lista_palavras = ["KAUNNY", "RAFAEL", "MEXICO", "CHAT", "ESCOLA", "AMIGOS"]

    # 2. Inicializa as variáveis do jogo na memória
    if "palavra_secreta" not in st.session_state:
        st.session_state.palavra_secreta = random.choice(st.session_state.lista_palavras)
        st.session_state.letras_descobertas = set()
        st.session_state.letras_erradas = set()
        st.session_state.tentativas_restantes = 6

    palavra = st.session_state.palavra_secreta
    erradas = st.session_state.letras_erradas
    descobertas = st.session_state.letras_descobertas

    # 3. Desenha a palavra na tela (ex: R _ F _ _ L)
    palavra_mascarada = ""
    for letra in palavra:
        if letra in descobertas:
            palavra_mascarada += letra + " "
        else:
            palavra_mascarada += "_ "
            
    st.markdown(f"### Palavra: `{palavra_mascarada.strip()}`")
    st.write(f"❤️ Tentativas restantes: **{st.session_state.tentativas_restantes}**")
    
    if erradas:
        st.write(f"❌ Letras erradas: {', '.join(sorted(list(erradas)))}")

    # 4. Verifica se o jogo acabou
    ganhou = all(letra in descobertas for letra in palavra)
    perdeu = st.session_state.tentativas_restantes <= 0

    if ganhou:
        st.success(f"🎉 Parabéns! Você acertou a palavra: **{palavra}**!")
    elif perdeu:
        st.error(f"💥 Game Over! A palavra era: **{palavra}**.")
    else:
        # Campo para o jogador chutar uma letra
        letra_chute = st.text_input("Chute uma letra:", max_chars=1, key="input_letra").upper()
        
        if st.button("Verificar Letra"):
            if letra_chute:
                if letra_chute in descobertas or letra_chute in erradas:
                    st.warning("Você já tentou essa letra!")
                elif letra_chute in palavra:
                    st.session_state.letras_descobertas.add(letra_chute)
                    st.success("Acertou a letra!")
                    st.rerun()
                else:
                    st.session_state.letras_erradas.add(letra_chute)
                    st.session_state.tentativas_restantes -= 1
                    st.error("Letra errada!")
                    st.rerun()
            else:
                st.info("Digite uma letra antes de clicar.")

    # 5. Botão para reiniciar com uma nova palavra
    st.write("---")
    if st.button("Nova Palavra / Reiniciar Forca"):
        st.session_state.palavra_secreta = random.choice(st.session_state.lista_palavras)
        st.session_state.letras_descobertas = set()
        st.session_state.letras_erradas = set()
        st.session_state.tentativas_restantes = 6
        st.rerun()
    
