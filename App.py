import streamlit as st

st.set_page_config(page_title="EXV Mini-Games", page_icon="🎮", layout="centered")

st.title("🎮 EXV Mini-Games")
st.write("Bem-vindo ao portal de jogos da turma! Escolha um jogo no menu abaixo.")

---

# Menu de seleção de jogos
jogo_escolhido = st.selectbox(
    "O que você quer jogar agora?",
    ["Selecione um jogo...", "❌ Jogo da Velha", "🔤 Jogo da Forca", "💡 Meu Jogo Inventado"]
)

# -------------------------------------------------------------------
# LÓGICA DO JOGO DA VELHA
# -------------------------------------------------------------------
if jogo_escolhido == "❌ Jogo da Velha":
    st.header("❌ Jogo da Velha ⭕")
    
    # Inicializa o tabuleiro na memória do Streamlit
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

    # Função chamada quando um botão do tabuleiro é clicado
    def clique_botao(index):
        if st.session_state.tabuleiro[index] == " " and not st.session_state.vencedor:
            st.session_state.tabuleiro[index] = st.session_state.turno
            vencedor = verificar_vencedor()
            if vencedor:
                st.session_state.vencedor = vencedor
            else:
                st.session_state.turno = "O" if st.session_state.turno == "X" else "X"

    # Criando o tabuleiro 3x3 com botões do Streamlit
    grid = [st.columns(3) for _ in range(3)]
    for i in range(3):
        for j in range(3):
            index = i * 3 + j
            txt_botao = st.session_state.tabuleiro[index]
            # Se o espaço estiver vazio, exibe um espaço em branco no botão
            label = txt_botao if txt_botao != " " else "  "
            grid[i][j].button(label, key=f"btn_{index}", on_click=clique_botao, args=(index,), use_container_width=True)

    # Mostra o status do jogo
    if st.session_state.vencedor:
        if st.session_state.vencedor == "Empate":
            st.info("Deu Velha! Empate! 🤝")
        else:
            st.success(f"🎉 O jogador '{st.session_state.vencedor}' venceu!")
    else:
        st.write(f"Vez do jogador: **{st.session_state.turno}**")

    # Botão para reiniciar o jogo
    if st.button("Reiniciar Jogo da Velha"):
        st.session_state.tabuleiro = [" "] * 9
        st.session_state.turno = "X"
        st.session_state.vencedor = None
        st.rerun()

# -------------------------------------------------------------------
# LÓGICA DO JOGO DA FORCA (ESPAÇO RESERVADO)
# -------------------------------------------------------------------
elif jogo_escolhido == "🔤 Jogo da Forca":
    st.header("🔤 Jogo da Forca")
    st.write("Em breve! Vamos programar esse em seguida com palavras secretas da turma.")

# -------------------------------------------------------------------
# JOGO INVENTADO POR VOCÊ (ESPAÇO RESERVADO)
# -------------------------------------------------------------------
elif jogo_escolhido == "💡 Meu Jogo Inventado":
    st.header("💡 Jogo Inventado pelo Rafa")
    st.write("Aqui vai entrar a sua imaginação! Qual é a ideia desse jogo?")
