import streamlit as st
import random

# --- Classe que gerencia a lógica do UNO ---
class UnoGame:
    def __init__(self):
        self.cores = ["Vermelho", "Azul", "Verde", "Amarelo"]
        self.valores = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Bloqueio", "Inverso", "+2"]
        self.deck = self.criar_deck()
        
    def criar_deck(self):
        deck = []
        for cor in self.cores:
            for valor in self.valores:
                deck.append({"cor": cor, "valor": valor})
        random.shuffle(deck)
        return deck

# --- Interface Visual (Separada da lógica) ---
def renderizar_jogo_uno():
    st.title("🃏 UNO Multiplayer EXV")
    
    if "uno_deck" not in st.session_state:
        st.session_state.uno_deck = UnoGame().deck
        st.session_state.minha_mao = [st.session_state.uno_deck.pop() for _ in range(7)]
        st.session_state.mesa = [st.session_state.uno_deck.pop()]

    # Layout Visual
    st.subheader("Carta na Mesa")
    carta = st.session_state.mesa[-1]
    st.markdown(f"### {carta['cor']} - {carta['valor']}")

    st.write("---")
    st.subheader("Sua Mão:")
    cols = st.columns(4)
    for i, carta_mao in enumerate(st.session_state.minha_mao):
        with cols[i % 4]:
            if st.button(f"{carta_mao['cor']} {carta_mao['valor']}", key=f"c_{i}"):
                # Lógica de validação (Simplificada)
                if carta_mao['cor'] == carta['cor'] or carta_mao['valor'] == carta['valor']:
                    st.session_state.mesa.append(st.session_state.minha_mao.pop(i))
                    st.success("Carta jogada!")
                    st.rerun()
                else:
                    st.error("Jogada inválida!")

if __name__ == "__main__":
    renderizar_jogo_uno()
    
