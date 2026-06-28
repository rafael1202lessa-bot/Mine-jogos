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

        # --- MONTAGEM DO TABULEIRO # ---
    # Criamos as 3 linhas do jogo. O loop garante que elas fiquem lado a lado no mobile.
    for i in range(3):
        cols = st.columns(3, gap="small") # O gap="small" economiza espaço nas laterais
        for j in range(3):
            index = i * 3 + j
            txt_botao = st.session_state.tabuleiro[index]
            label = txt_botao if txt_botao != " " else "  "
            
            # Renderiza o botão na coluna correspondente
            cols[j].button(
                label, 
                key=f"b_{index}", 
                on_click=clique_botao, 
                args=(index,), 
                use_container_width=True
            )
        
        # Só coloca a linha divisória horizontal entre a linha 0 e 1, e entre a 1 e 2
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
