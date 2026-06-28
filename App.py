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
        
        # --- CARA A CARA MULTIPLAYER ---
    elif jogo_escolhido == "👤 Cara a Cara (Multiplayer)":
        st.subheader("👤 Cara a Cara EXV — Multiplayer")
        
        # --- LÓGICA DE SALAS MULTIPLAYER ---
        if "sala_id" not in st.session_state:
            st.session_state.sala_id = None
            st.session_state.meu_numero = None # 1 ou 2
            st.session_state.eliminados = set() # Guarda quem o jogador clicou para "abaixar"

        # Se não estiver em nenhuma sala, mostra opções de Criar ou Entrar
        if st.session_state.sala_id is None:
            col_sala1, col_sala2 = st.columns(2)
            
            with col_sala1:
                if st.button("🆕 Criar Nova Sala"):
                    try:
                        nova_sala = supabase.table("partidas_cara_a_cara").insert({
                            "jogador_1": st.session_state.username_atual,
                            "status": "aguardando",
                            "turno": st.session_state.username_atual
                        }).execute()
                        if len(nova_sala.data) > 0:
                            st.session_state.sala_id = nova_sala.data[0]["id"]
                            st.session_state.meu_numero = 1
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar sala: {e}")

            with col_sala2:
                st.write("**Salas Disponíveis:**")
                try:
                    salas_abertas = supabase.table("partidas_cara_a_cara").select("*").eq("status", "aguardando").execute()
                    if len(salas_abertas.data) == 0:
                        st.caption("Nenhuma sala aberta no momento. Crie uma!")
                    for sala in salas_abertas.data:
                        if sala["jogador_1"] != st.session_state.username_atual:
                            if st.button(f"Entrar na Sala de {sala['jogador_1']}", key=f"sala_{sala['id']}"):
                                supabase.table("partidas_cara_a_cara").update({
                                    "jogador_2": st.session_state.username_atual,
                                    "status": "jogando"
                                }).eq("id", sala["id"]).execute()
                                st.session_state.sala_id = sala["id"]
                                st.session_state.meu_numero = 2
                                st.rerun()
                except Exception as e:
                    st.error(f"Erro ao buscar salas: {e}")

        # --- SE JÁ ESTIVER DENTRO DE UMA SALA ---
        else:
            try:
                # Atualiza os dados da sala em tempo real
                dados_sala = supabase.table("partidas_cara_a_cara").select("*").eq("id", st.session_state.sala_id).execute().data[0]
            except:
                st.error("Sala não encontrada.")
                if st.button("Voltar ao Menu"):
                    st.session_state.sala_id = None
                    st.rerun()
                st.stop()

            # Botão de emergência para abandonar a partida
            if st.sidebar.button("🏳️ Sair da Partida"):
                supabase.table("partidas_cara_a_cara").update({"status": "finalizado"}).eq("id", st.session_state.sala_id).execute()
                st.session_state.sala_id = None
                st.session_state.eliminados = set()
                st.rerun()

            # Status da Sala
            if dados_sala["status"] == "aguardando":
                st.warning("⏳ Aguardando um oponente entrar na sala...")
                if st.button("🔄 Atualizar Tela"):
                    st.rerun()
            
            elif dados_sala["status"] == "jogando":
                oponente = dados_sala["jogador_2"] if st.session_state.meu_numero == 1 else dados_sala["jogador_1"]
                st.write(f"⚔️ Você está duelando contra: **{oponente}**")
                
                # Mostra o Turno Atual
                if dados_sala["turno"] == st.session_state.username_atual:
                    st.success("🟢 É a sua vez de fazer uma pergunta ou chutar!")
                else:
                    st.warning(f"🟡 Vez de **{dados_sala['turno']}** jogar...")
                    if st.button("🔄 Conferir se já é minha vez"):
                        st.rerun()

                st.write("---")

                # --- BUSCA TODOS OS PERFIS PARA MONTAR O TABULEIRO ---
                try:
                    todos_perfis = supabase.table("perfis_jogos_exv").select("username", "foto_url").execute().data
                except Exception as e:
                    st.error(f"Erro ao carregar os rostos: {e}")
                    todos_perfis = []

                # --- DESENHA O TABULEIRO VISUAL (GRADE DE CARTAS) ---
                st.markdown("### 🎴 Seu Tabuleiro de Suspeitos")
                st.caption("Clique no botão abaixo da foto para 'abaixar' ou 'levantar' a carta do amigo!")

                # Criamos uma grade com 4 colunas (fica ótimo no celular e PC)
                colunas_tabuleiro = st.columns(4)
                
                for indice, perfil in enumerate(todos_perfis):
                    nome_suspeito = perfil["username"]
                    url_foto = perfil["foto_url"]
                    
                    # Identifica em qual das 4 colunas a carta vai ficar
                    com_coluna = colunas_tabuleiro[indice % 4]
                    
                    with com_coluna:
                        esta_eliminado = nome_suspeito in st.session_state.eliminados
                        
                        if esta_eliminado:
                            # Efeito visual de carta virada/escura
                            st.markdown(f"<div style='opacity: 0.25; text-align: center;'>👤<br><b>{nome_suspeito}</b></div>", unsafe_url_allowed=True)
                            if st.button("🔼 Levantar", key=f"up_{nome_suspeito}_{indice}"):
                                st.session_state.eliminados.remove(nome_suspeito)
                                st.rerun()
                        else:
                            # Mostra a foto real do banco de dados
                            if url_foto:
                                st.image(url_foto, use_container_width=True)
                            else:
                                st.subheader("👤")
                            st.markdown(f"<p style='text-align: center; margin-bottom: 2px;'><b>{nome_suspeito}</b></p>", unsafe_url_allowed=True)
                            
                            if st.button("🔻 Abaixar", key=f"down_{nome_suspeito}_{indice}"):
                                st.session_state.eliminados.add(nome_suspeito)
                                st.rerun()
                
                st.write("---")
                # --- SISTEMA DE CHUTE (JÁ SABE QUEM É?) ---
                st.markdown("### 👁️ Já sabe quem é?")
                chute = st.selectbox("Escolha o seu palpite certeiro:", ["Selecione..."] + [p["username"] for p in todos_perfis], key="campo_chute")
                
                if st.button("🚨 Dar Palpite Final!"):
                    if chute != "Selecione...":
                        st.info(f"Você chutou que o personagem secreto é o **{chute}**!")
                        # Na próxima etapa vamos checar se acertou contra o 'secreto' guardado na tabela!
                        
