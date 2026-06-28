import streamlit as st
from supabase import create_client, Client
import random

st.set_page_config(page_title="EXV Mini-Games", page_icon="🎮", layout="centered")

# --- CONFIGURAÇÃO DO SUPABASE ---
# Coloque aqui as suas credenciais reais do projeto!
URL_SUPABASE = "https://ldjtqgeyorkzbvuichjj.supabase.co"
CHAVE_SUPABASE = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

@st.cache_resource
def conectar_supabase():
    return create_client(URL_SUPABASE, CHAVE_SUPABASE)

supabase = conectar_supabase()

# Inicializa as variáveis de sessão essenciais
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "username_atual" not in st.session_state:
    st.session_state.username_atual = None
if "tela_atual" not in st.session_state:
    st.session_state.tela_atual = "login"

# --- FLUXO DE AUTENTICAÇÃO (SÓ ABRE SE NÃO ESTIVER LOGADO) ---
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

    # --- TELA DE CADASTRO ---
    elif st.session_state.tela_atual == "cadastro":
        st.title("📝 Criar Conta - EXV Mini-Games")
        st.write("Crie o seu perfil para jogar com a turma!")

        novo_usuario = st.text_input("Escolha um Usuário / Nickname:", key="cad_user").strip()
        nova_senha = st.text_input("Escolha uma Senha:", type="password", key="cad_pass")
        confirmar_senha = st.text_input("Confirme a Senha:", type="password", key="cad_pass_conf")
        foto_enviada = st.file_uploader("Escolha sua Foto de Perfil (Para o Cara a Cara):", type=["png", "jpg", "jpeg"])

        if st.button("Criar Minha Conta"):
            if novo_usuario and nova_senha and confirmar_senha:
                if nova_senha != confirmar_senha:
                    st.error("As senhas não coincidem!")
                elif not foto_enviada:
                    st.error("Por favor, selecione uma foto de perfil! Ela é obrigatória.")
                else:
                    try:
                        existente = supabase.table("perfis_jogos_exv").select("*").eq("username", novo_usuario).execute()
                        if len(existente.data) > 0:
                            st.error("Esse usuário já existe! Escolha outro nome.")
                        else:
                            # Envia foto ao Storage
                            extensao = foto_enviada.name.split(".")[-1]
                            nome_arquivo_storage = f"{novo_usuario}_perfil.{extensao}"
                            bytes_da_foto = foto_enviada.getvalue()
                            
                            supabase.storage.from_("fotos_perfil").upload(
                                path=nome_arquivo_storage,
                                file=bytes_da_foto,
                                file_options={"content-type": foto_enviada.type, "upsert": "true"}
                            )
                            
                            foto_url = supabase.storage.from_("fotos_perfil").get_public_url(nome_arquivo_storage)
                            
                            # Insere dados na tabela nova
                            dados_novos = {"username": novo_usuario, "senha": nova_senha, "foto_url": foto_url}
                            supabase.table("perfis_jogos_exv").insert(dados_novos).execute()
                            
                            st.success("🎉 Conta criada com sucesso! Faça seu login.")
                            st.session_state.tela_atual = "login"
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar cadastro: {e}")
            else:
                st.warning("Por favor, preencha todos os campos!")

        if st.button("Voltar para a tela de Login"):
            st.session_state.tela_atual = "login"
            st.rerun()

# --- ÁREA DOS JOGOS (SÓ ENTRA SE ESTIVER LOGADO) ---
else:
    st.sidebar.write(f"🎮 Jogador: **{st.session_state.username_atual}**")
    if st.sidebar.button("Sair / Logout"):
        st.session_state.usuario_logado = None
        st.session_state.username_atual = None
        st.rerun()

    st.title("🎮 EXV Portal de Mini-Games")
    st.write(f"Olá, {st.session_state.username_atual}!")
    
    jogo_escolhido = st.selectbox(
        "Escolha o modo de jogo:",
        ["Selecione...", "🔤 Jogo da Forca", "👤 Cara a Cara (Multiplayer)"]
    )
    
    # --- JOGO DA FORCA ---
    if jogo_escolhido == "🔤 Jogo da Forca":
        st.subheader("🔤 Jogo da Forca EXV")
        
        modo_forca = st.radio("Modo de Jogo:", ["Palavras Aleatórias", "Digitar Palavra Secre"], horizontal=True)

        if modo_forca == "Digitar Palavra Secre":
            palavra_custom = st.text_input("Palavra secreta (em segredo):", type="password").upper().strip()
            if st.button("Definir Palavra Secreta"):
                if palavra_custom:
                    st.session_state.palavra_secreta = palavra_custom
                    st.session_state.letras_descobertas = set()
                    st.session_state.letras_erradas = set()
                    st.session_state.tentativas_restantes = 6
                    st.success("Palavra definida!")
                    st.rerun()
        
        if "lista_palavras" not in st.session_state:
            st.session_state.lista_palavras = ["KAUNNY", "RAFAEL", "MEXICO", "CHAT", "ESCOLA"]

        if "palavra_secreta" not in st.session_state:
            st.session_state.palavra_secreta = random.choice(st.session_state.lista_palavras)
            st.session_state.letras_descobertas = set()
            st.session_state.letras_erradas = set()
            st.session_state.tentativas_restantes = 6

        palavra = st.session_state.palavra_secreta
        erradas = st.session_state.letras_erradas
        descobertas = st.session_state.letras_descobertas

        palavra_mascarada = "".join([letra + " " if letra in descobertas else "_ " for letra in palavra])
        st.markdown(f"### Palavra: `{palavra_mascarada.strip()}`")
        st.write(f"❤️ Tentativas restantes: **{st.session_state.tentativas_restantes}**")
        
        if erradas:
            st.write(f"❌ Erradas: {', '.join(sorted(list(erradas)))}")

        if all(letra in descobertas for letra in palavra):
            st.success(f"🎉 Você acertou: **{palavra}**!")
        elif st.session_state.tentativas_restantes <= 0:
            st.error(f"💥 Game Over! Era: **{palavra}**.")
        else:
            letra_chute = st.text_input("Chute uma letra:", max_chars=1, key="input_letra").upper()
            if st.button("Verificar Letra"):
                if letra_chute:
                    if letra_chute in descobertas or letra_chute in erradas:
                        st.warning("Já tentou essa!")
                    elif letra_chute in palavra:
                        st.session_state.letras_descobertas.add(letra_chute)
                        st.rerun()
                    else:
                        st.session_state.letras_erradas.add(letra_chute)
                        st.session_state.tentativas_restantes -= 1
                        st.rerun()

        st.write("---")
        if st.button("Reiniciar Forca"):
            st.session_state.palavra_secreta = random.choice(st.session_state.lista_palavras)
            st.session_state.letras_descobertas = set()
            st.session_state.letras_erradas = set()
            st.session_state.tentativas_restantes = 6
            st.rerun()
        
    # --- CARA A CARA ---
    elif jogo_escolhido == "👤 Cara a Cara (Multiplayer)":
        st.subheader("👤 Cara a Cara EXV")
        st.write("A base de dados de fotos e contas está 100% pronta!")
        st.info("Próximo passo: programar a lógica de turnos e o tabuleiro de rostos.")
                            
