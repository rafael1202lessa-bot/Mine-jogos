import streamlit as st

def mostrar_mao_visual(mao):
    st.subheader("Sua Mão")
    # Usamos colunas para dispor as cartas lado a lado
    colunas = st.columns(len(mao))
    
    for i, carta in enumerate(mao):
        with colunas[i]:
            # Nome do arquivo da imagem baseado na cor e valor
            nome_arquivo = f"cartas/{carta['cor'].lower()}_{carta['valor'].lower()}.png"
            
            # O st.image funciona como um botão visual
            # Se a pessoa clicar na imagem, o jogo entende como jogada
            if st.image(nome_arquivo, use_column_width=True):
                if st.button("Jogar esta", key=f"btn_{i}"):
                    # Aqui entra a lógica de validar e jogar no Supabase
                    st.write(f"Você jogou {carta['valor']} de {carta['cor']}")
                    st.rerun()

# --- Exemplo de como chamar no seu app ---
# mao_jogador = [{"cor": "Azul", "valor": "5"}, {"cor": "Vermelho", "valor": "Bloqueio"}]
# mostrar_mao_visual(mao_jogador)
