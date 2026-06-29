import streamlit as st
import random

# 1. Lógica do Jogo (O motor)
class Uno:
    def __init__(self):
        cores = ["azul", "vermelho", "verde", "amarelo"]
        valores = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "bloqueio", "inverso", "+2"]
        self.deck = [{"cor": c, "valor": v} for c in cores for v in valores]
        random.shuffle(self.deck)

    def comprar_carta(self):
        return self.deck.pop() if self.deck else None

# 2. Interface Visual
def renderizar_uno():
    st.title("🃏 UNO EXV — Versão Visual")
    
    if "jogo_iniciado" not in st.session_state:
        st.session_state.engine = Uno()
        st.session_state.mao = [st.session_state.engine.comprar_carta() for _ in range(7)]
        st.session_state.mesa = st.session_state.engine.comprar_carta()
        st.session_state.jogo_iniciado = True

    # Exibição da Mesa
    st.subheader("Carta na Mesa")
    carta_mesa = st.session_state.mesa
    # Aqui você usaria o caminho das suas imagens: f"cartas/{carta_mesa['cor']}_{carta_mesa['valor']}.png"
    st.info(f"Carta atual: {carta_mesa['cor'].upper()} {carta_mesa['valor'].upper()}")

    # Exibição da Mão
    st.write("---")
    st.subheader("Sua Mão")
    cols = st.columns(4)
    
    for i, carta in enumerate(st.session_state.mao):
        with cols[i % 4]:
            # Criamos um botão com o nome da carta
            # Para usar IMAGENS, substitua o botão por: st.image(f"caminho/{carta['cor']}_{carta['valor']}.png")
            if st.button(f"{carta['cor']} {carta['valor']}", key=f"carta_{i}"):
                if carta['cor'] == carta_mesa['cor'] or carta['valor'] == carta_mesa['valor']:
                    st.session_state.mesa = st.session_state.mao.pop(i)
                    st.rerun()
                else:
                    st.error("Jogada Inválida!")

if __name__ == "__main__":
    renderizar_uno()
    
