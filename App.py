import streamlit as st
from supabase import create_client, Client
import os

st.set_page_config(page_title="EXV Mini-Games", page_icon="🎮", layout="centered")

# --- CONFIGURAÇÃO DO SUPABASE ---
# Substitua pelas suas credenciais reais do projeto!
URL_SUPABASE = "https://ldjtqgeyorkzbvuichjj.supabase.co"
CHAVE_SUPABASE = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

@st.cache_resource
def conectar_supabase():
    return create_client(URL_SUPABASE, CHAVE_SUPABASE)

supabase = conectar_supabase()

# Inicializa as variáveis de sessão
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "username_atual" not in st.session_state:
    st.session_state.username_atual = None
if "tela_atual" not in st.session_state:
    st.session_state.tela_atual = "login"

# --- FLUXO DE AUTENTICAÇÃO ---
if st.session_state.usuario_logado is None:
    
    # --- TELA DE LOGIN ---
    if st.session_state.tela_atual == "login":
        st.title("🔑 Login - EXV Mini-Games")
        st.write("Entre com a sua conta de jogos!")

        usuario = st.text_input("Usuário / Nickname:", key="login_user").strip()
        senha = st.text_input("Senha:", type="password", key="login_pass")

        if st.button("Entrar"):
            if usuario and senha:
                try:
                    # Busca na tabela exclusiva de jogos
                    resposta = supabase.table("perfis_jogos_exv").select("*").eq("username", usuario).eq("senha", senha).execute()
                    
                    if len(resposta.data) > 0:
                        st.session_state.usuario_logado = resposta.data[0]["id"]
                        st.session_state.username_atual = resposta.data[0]["username"]
                        st.success(f"🎉 Bem-vindo de volta, {usuario}!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos!")
                except Exception as e:
                    st.error(f"Erro no banco: {e}")
            else:
                st.warning("Preencha todos os campos!")
        
        st.write("---")
        if st.button("Não tem uma conta? Cadastre-se aqui!"):
            st.session_state.tela_atual = "cadastro"
            st.rerun()

    # --- TELA DE CADASTRO (COM FOTO DE PERFIL) ---
    elif st.session_state.tela_atual == "cadastro":
        st.title("📝 Criar Conta - EXV Mini-Games")
        st.write("Crie o seu perfil para jogar com a turma!")

        novo_usuario = st.text_input("Escolha um Usuário / Nickname:", key="cad_user").strip()
        nova_senha = st.text_input("Escolha uma Senha:", type="password", key="cad_pass")
        confirmar_senha = st.text_input("Confirme a Senha:", type="password", key="cad_pass_conf")
        
        # Campo de Upload da Foto de Perfil
        foto_enviada = st.file_uploader("Escolha sua Foto de Perfil (Para o Cara a Cara):", type=["png", "jpg", "jpeg"])

        if st.button("Criar Minha Conta"):
            if novo_usuario and nova_senha and confirmar_senha:
                if nova_senha != confirmar_senha:
                    st.error("As senhas não coincidem!")
                elif not foto_enviada:
                    st.error("Por favor, selecione uma foto de perfil! Ela é obrigatória para o jogo Cara a Cara.")
                else:
                    try:
                        # 1. Verifica se o usuário já existe
                        existente = supabase.table("perfis_jogos_exv").select("*").eq("username", novo_usuario).execute()
                        
                        if len(existente.data) > 0:
                            st.error("Esse usuário já existe! Escolha outro nome.")
                        else:
                            # 2. Faz o upload da foto para o Storage (Bucket) do Supabase
                            extensao = foto_enviada.name.split(".")[-1]
                            nome_arquivo_storage = f"{novo_usuario}_perfil.{extensao}"
                            bytes_da_foto = foto_enviada.getvalue()
                            
                            supabase.storage.from_("fotos_perfil").upload(
                                path=nome_arquivo_storage,
                                file=bytes_da_foto,
                                file_options={"content-type": foto_enviada.type, "upsert": "true"}
                            )
                            
                            # 3. Pega a URL pública da foto enviada
                            foto_url = supabase.storage.from_("fotos_perfil").get_public_url(nome_arquivo_storage)
                            
                            # 4. Salva o registro completo na tabela perfis_jogos_exv
                            dados_novos = {
                                "username": novo_usuario, 
                                "senha": nova_senha,
                                "foto_url": foto_url
                            }
                            supabase.table("perfis_jogos_exv").insert(dados_novos).execute()
                            
                            st.success("🎉 Conta criada com sucesso com foto de perfil! Faça seu login.")
                            st.session_state.tela_atual = "login"
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar cadastro ou imagem: {e}")
            else:
                st.warning("Por favor, preencha todos os campos!")

        if st.button("Voltar para a tela de Login"):
            st.session_state.tela_atual = "login"
            st.rerun()

# --- ÁREA DOS JOGOS (SÓ ACESSA LOGADO) ---
else:
    st.sidebar.write(f"🎮 Jogador: **{st.session_state.username_atual}**")
    if st.sidebar.button("Sair / Logout"):
        st.session_state.usuario_logado = None
        st.session_state.username_atual = None
        st.rerun()

    st.title("🎮 EXV Portal de Mini-Games")
    st.write(f"Olá, {st.session_state.username_atual}!")
    
    # O menu de seleção cria a variável 'jogo_escolhido' de forma segura aqui dentro
    jogo_escolhido = st.selectbox(
        "Escolha o modo de jogo:",
        ["Selecione...", "🔤 Jogo da Forca", "👤 Cara a Cara (Multiplayer)"]
    )
    
    # TODA a lógica dos jogos deve ficar recuada (com tab) dentro deste ELSE
    if jogo_escolhido == "🔤 Jogo da Forca":
        st.subheader("🔤 Jogo da Forca EXV")
        # (Aqui você pode colar o código completo daquela sua Forca com as funções de chutar letras)
        
    elif jogo_escolhido == "👤 Cara a Cara (Multiplayer)":
        st.subheader("👤 Cara a Cara EXV")
        st.write("A base de dados de fotos está pronta! Vamos programar as regras agora.")
        
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
    
