import streamlit as st
from supabase import create_client, Client
import random
import numpy as np
from scipy.io import wavfile
import io
import time

st.set_page_config(page_title="EXV Portal de Mini-Games", page_icon="🎮", layout="centered")

# --- CONFIGURAÇÃO DO SUPABASE ---
# Use as suas credenciais reais (as do Quem é Quem ou as principais)
URL_SUPABASE = "https://ldjtqgeyorkzbvuichjj.supabase.co"
CHAVE_SUPABASE = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

@st.cache_resource
def conectar_supabase():
    return create_client(URL_SUPABASE, CHAVE_SUPABASE)

supabase = conectar_supabase()

# ==============================================================================
# 🌐 CENTRAL DE ESTADOS GLOBAIS (COLE ISSO APÓS A CONFIGURAÇÃO DO SUPABASE)
# ==============================================================================
if "username_atual" not in st.session_state: st.session_state.username_atual = None

# Jogo: Cara a Cara
if "cara_modo" not in st.session_state: st.session_state.cara_modo = None
if "bot_suspeito" not in st.session_state: st.session_state.bot_suspeito = None
if "sala_id" not in st.session_state: st.session_state.sala_id = None
if "meu_numero" not in st.session_state: st.session_state.meu_numero = None
if "eliminados" not in st.session_state: st.session_state.eliminados = set()

# Jogo: UNO
if "uno_modo" not in st.session_state: st.session_state.uno_modo = None
if "uno_sala_id" not in st.session_state: st.session_state.uno_sala_id = None
# ==============================================================================

# --- FUNÇÃO DO MODIFICADOR DE VOZ (QUEM É QUEM) ---
def aplicar_modificador_voz(audio_bytes, efeito):
    try:
        samplerate, data = wavfile.read(io.BytesIO(audio_bytes))
        if len(data.shape) > 1:
            data = data[:, 0]  # Converte estéreo para mono

        if efeito == "🦹‍♂️ Vilão (Grave)":
            novo_samplerate = int(samplerate * 0.70)
        elif efeito == "🐿️ Esquilo (Fino)":
            novo_samplerate = int(samplerate * 1.45)
        elif efeito == "🤖 Robô / Ciborgue":
            rhythm = np.sin(2 * np.pi * np.arange(len(data)) * 60 / samplerate)
            data = (data * rhythm).astype(data.dtype)
            novo_samplerate = samplerate
        else:
            novo_samplerate = samplerate

        buffer_saida = io.BytesIO()
        wavfile.write(buffer_saida, novo_samplerate, data)
        return buffer_saida.getvalue()
    except Exception as e:
        st.error(f"Erro ao processar modificador de voz: {e}")
        return audio_bytes

# Inicializa as variáveis de sessão essenciais do portal
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "username_atual" not in st.session_state:
    st.session_state.username_atual = None
if "tela_atual" not in st.session_state:
    st.session_state.tela_atual = "login"

# Estados internos do Cara a Cara
if "sala_id" not in st.session_state:
    st.session_state.sala_id = None
    st.session_state.meu_numero = None
    st.session_state.eliminados = set()

# Estados internos do Quem é Quem
if "qq_sala" not in st.session_state:
    st.session_state.qq_sala = ""
    st.session_state.qq_nome_real = ""
    st.session_state.qq_turma = ""
    st.session_state.qq_registrado = False

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
    
    jogo_escolhido = st.selectbox("Escolha o Jogo:", ["🔤 Jogo da Forca", "👤 Cara a Cara (Multiplayer)", "🕵️ Quem é Quem? (Walkie-Talkie)", "🃏 Jogo do UNO (Multiplayer)"])
       
    # ================= JOGO 1: FORCA =================
    if jogo_escolhido == "🔤 Jogo da Forca":
        st.subheader("🔤 Jogo da Forca EXV")
        
        modo_forca = st.radio("Modo de Jogo:", ["Palavras Aleatórias", "Digitar Palavra Secreta"], horizontal=True)

        if modo_forca == "Digitar Palavra Secreta":
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
                  
        # ================= JOGO 2: CARA A CARA =================
    elif jogo_escolhido == "👤 Cara a Cara (Multiplayer)":
        st.subheader("👤 Cara a Cara EXV — Tabuleiro Clássico")
        
        # Inicializa variáveis do Cara a Cara localmente se não existirem
        if "cara_modo" not in st.session_state: st.session_state.cara_modo = None
        if "bot_suspeito" not in st.session_state: st.session_state.bot_suspeito = None
        if "sala_id" not in st.session_state: st.session_state.sala_id = None
        if "meu_numero" not in st.session_state: st.session_state.meu_numero = None
        if "eliminados" not in st.session_state: st.session_state.eliminados = set()

        # Lista exata e oficial de personagens baseada no print original!
        personagens_oficiais = [
            "TRISTAN", "BOBBY", "LINDA", "KELLEN", "FLOYD", "CLEO", "TODD", "FRED",
            "LOLA", "CHUCK", "RENATA", "ALINE", "ANDY", "SAMUEL", "GADI", "GIGI",
            "MELISSA", "RONI", "LEO", "DENIS", "ANA", "SUZI", "MAUDE", "SÔNIA"
        ]

        # MENU DE SELEÇÃO DO MODO
        if st.session_state.cara_modo is None:
            st.write("### Escolha o Modo de Jogo:")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                if st.button("🤖 Jogar Contra o Bot (Solo)", use_container_width=True):
                    st.session_state.cara_modo = "solo"
                    st.session_state.bot_suspeito = random.choice(personagens_oficiais)
                    st.rerun()
            with col_m2:
                if st.button("👥 Jogar com Amigo (Online)", use_container_width=True):
                    st.session_state.cara_modo = "online"
                    st.rerun()

        # --- MODO SOLO (CONTRA O BOT) ---
        elif st.session_state.cara_modo == "solo":
            st.write("🤖 Você está jogando no **Modo Solo** contra a Inteligência Artificial!")
            if st.sidebar.button("🏳️ Sair do Jogo Solo"):
                st.session_state.cara_modo = None
                st.session_state.eliminados = set()
                st.rerun()

            st.markdown("### 🎴 Seu Tabuleiro de Suspeitos")
            colunas_tabuleiro = st.columns(4)
            for indice, nome_suspeito in enumerate(personagens_oficiais):
                com_coluna = colunas_tabuleiro[indice % 4]
                with com_coluna:
                    esta_eliminado = nome_suspeito in st.session_state.eliminados
                    if esta_eliminado:
                                st.markdown(f"<div style='opacity: 0.2; text-align: center; font-size: 24px; padding: 10px; background: #333; border-radius: 5px;'>❌<br><b style='font-size:12px;'>{nome_suspeito}</b></div>",unsafe_allow_html=True)
                                                                 if st.button("🔼 Levantar", key=f"up_solo_{nome_suspeito}_{indice}", use_container_width=True):
                            st.session_state.eliminados.remove(nome_suspeito)
                            st.rerun()
                    else:
                        st.markdown(
                    "<div style='border: 2px solid #FFA500; padding: 10px; background-color: #FFF3CD;'>Tabuleiro Ativo</div>",unsafe_allow_html=True)         
                    if st.button("🔻 Abaixar", key=f"dw_solo_{nome_suspeito}_{indice}", use_container_width=True):
                            st.session_state.eliminados.add(nome_suspeito)
                            st.rerun()

            st.write("---")
            st.markdown("### 🔍 Dar Palpite Final")
            chute = st.selectbox("Quem você acha que o Bot escolheu?", ["Selecione..."] + personagens_oficiais)
            if st.button("Confirmar Palpite! 🎯", use_container_width=True):
                if chute == st.session_state.bot_suspeito:
                    st.balloons()
                    st.success(f"🏆 PARABÉNS! Você acertou! O Bot era realmente o **{st.session_state.bot_suspeito}**!")
                else:
                    st.error(f"❌ Errou! O Bot não era o {chute}. Continue eliminando suspeitos!")

        # --- MODO ONLINE (MULTIPLAYER ORIGINAL) ---
        elif st.session_state.cara_modo == "online":
            if st.sidebar.button("↩️ Mudar de Modo (Voltar)"):
                st.session_state.cara_modo = None
                st.session_state.sala_id = None
                st.rerun()
                
            if st.session_state.sala_id is None:
                col_sala1, col_sala2 = st.columns(2)
                with col_sala1:
                    if st.button("🆕 Criar Nova Sala"):
                        try:
                            nova_sala = supabase.table("partidas_cara_a_cara").insert({
                                "jogador_1": st.session_state.username_atual, "status": "aguardando", "turno": st.session_state.username_atual
                            }).execute()
                            if len(nova_sala.data) > 0:
                                st.session_state.sala_id = nova_sala.data[0]["id"]
                                st.session_state.meu_numero = 1
                                st.rerun()
                        except Exception as e: st.error(f"Erro: {e}")

                with col_sala2:
                    st.write("**Salas Disponíveis:**")
                    try:
                        salas_abertas = supabase.table("partidas_cara_a_cara").select("*").eq("status", "aguardando").execute()
                        if len(salas_abertas.data) == 0: st.caption("Nenhuma sala aberta.")
                        for sala in salas_abertas.data:
                            if sala["jogador_1"] != st.session_state.username_atual:
                                if st.button(f"Entrar na Sala de {sala['jogador_1']}", key=f"s_{sala['id']}"):
                                    supabase.table("partidas_cara_a_cara").update({"jogador_2": st.session_state.username_atual, "status": "jogando"}).eq("id", sala["id"]).execute()
                                    st.session_state.sala_id = sala["id"]
                                    st.session_state.meu_numero = 2
                                    st.rerun()
                    except Exception as e: st.error(f"Erro: {e}")
            else:
                try: dados_sala = supabase.table("partidas_cara_a_cara").select("*").eq("id", st.session_state.sala_id).execute().data[0]
                except: st.session_state.sala_id = None; st.rerun()

                if st.sidebar.button("🏳️ Sair da Partida"):
                    supabase.table("partidas_cara_a_cara").update({"status": "finalizado"}).eq("id", st.session_state.sala_id).execute()
                    st.session_state.sala_id = None
                    st.session_state.eliminados = set()
                    st.rerun()

                if dados_sala["status"] == "aguardando":
                    st.warning("⏳ Aguardando oponente...")
                    if st.button("🔄 Atualizar"): st.rerun()
                elif dados_sala["status"] == "jogando":
                    oponente = dados_sala["jogador_2"] if st.session_state.meu_numero == 1 else dados_sala["jogador_1"]
                    st.write(f"⚔️ Oponente: **{oponente}**")
                    if dados_sala["turno"] == st.session_state.username_atual: st.success("🟢 Sua vez!")
                    else: 
                        st.warning(f"🟡 Vez de {dados_sala['turno']}")
                        if st.button("🔄 Atualizar Turno"): st.rerun()

                    st.write("---")
                    st.markdown("### 🎴 Seu Tabuleiro de Suspeitos")
                    colunas_tabuleiro = st.columns(4)
                    for indice, nome_suspeito in enumerate(personagens_oficiais):
                        com_coluna = colunas_tabuleiro[indice % 4]
                        with com_coluna:
                            esta_eliminado = nome_suspeito in st.session_state.eliminados
                            if esta_eliminado:
                                st.markdown(f"<div style='opacity: 0.2; text-align: center; font-size: 24px; padding: 10px; background: #333; border-radius: 5px;'>❌<br><b style='font-size:12px;'>{nome_suspeito}</b></div>", unsafe_url_allowed=True)
                                if st.button("🔼 Levantar", key=f"up_{nome_suspeito}_{indice}", use_container_width=True):
                                    st.session_state.eliminados.remove(nome_suspeito)
                                    st.rerun()
                            else:
                                st.markdown(f"<div style='text-align: center; border: 2px solid #FFA500; background: #FFF3CD; padding: 15px; border-radius: 8px; color: #000;'>👤<br><b style='color: #000;'>{nome_suspeito}</b></div>", unsafe_url_allowed=True)
                                if st.button("🔻 Abaixar", key=f"dw_{nome_suspeito}_{indice}", use_container_width=True):
                                    st.session_state.eliminados.add(nome_suspeito)
                                    st.rerun()
                                   
    # ================= JOGO 3: QUEM É QUEM (WALKIE-TALKIE) =================
    elif jogo_escolhido == "🕵️‍♂️ Quem é Quem? (Walkie-Talkie)":
        st.subheader("🕵️‍♂️ Jogo: Quem é Quem? Anônimo")
        
                # Se não configurou a sala de teleporte do grupo ainda
        if not st.session_state.qq_registrado:
            st.markdown("Combine um **Nome de Grupo** com seus amigos para entrar na mesma sala de investigação!")
            
            # AGORA SIM: Campo para escolher o Nick Falso/Secreto da partida!
            nick_falso_partida = st.text_input("Escolha seu Nick Secreto para esta partida (Falso):", placeholder="Ex: NinjaAnonimo").strip()
            nome_real_investigador = st.text_input("Seu Nome Verdadeiro (Ficará 100% oculto dos outros):", placeholder="Ex: Rafael").strip()
            grupo_turma = st.text_input("Nome do Grupo ou Turma (Mesmo nome para a galera):", placeholder="Ex: GrupoDoRafa").strip()
            
            if st.button("Entrar no Jogo (Teleportar) 🌀"):
                if nick_falso_partida == "" or nome_real_investigador == "" or grupo_turma == "":
                    st.error("Preencha todos os campos obrigatórios!")
                else:
                    try:
                        sala_encontrada = ""
                        numero_da_sala = 1
                        grupo_limpo = grupo_turma.upper()
                        
                        while sala_encontrada == "":
                            nome_sala_teste = f"{grupo_limpo} - SALA {numero_da_sala}"
                            resposta_sala = supabase.table("jogadores").select("*").eq("sala", nome_sala_teste).execute()
                            qtd_jogadores = len(resposta_sala.data) if resposta_sala.data else 0
                            
                            if qtd_jogadores < 4:
                                sala_encontrada = nome_sala_teste
                            else:
                                numero_da_sala += 1
                        
                        # Cadastra no banco usando o Nick Falso que você escolheu!
                        supabase.table("jogadores").insert({
                            "nick": nick_falso_partida, 
                            "sala": sala_encontrada,
                            "nome_real": nome_real_investigador,
                            "turma": grupo_limpo
                        }).execute()
                        
                        # Salva o nick falso no estado para usar no chat e áudios
                        st.session_state.username_atual_quem_e_quem = nick_falso_partida
                        st.session_state.qq_sala = sala_encontrada
                        st.session_state.qq_nome_real = nome_real_investigador
                        st.session_state.qq_turma = grupo_limpo
                        st.session_state.qq_registrado = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao entrar na sala do Quem é Quem: {e}")
                          
                        # Cadastra o jogador usando o Nick do Login do Portal de forma automática!
                        supabase.table("jogadores").insert({
                            "nick": st.session_state.username_atual, 
                            "sala": sala_encontrada,
                            "nome_real": nome_real_investigador,
                            "turma": grupo_limpo
                        }).execute()
                        
                        st.session_state.qq_sala = sala_encontrada
                        st.session_state.qq_nome_real = nome_real_investigador
                        st.session_state.qq_turma = grupo_limpo
                        st.session_state.qq_registrado = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao entrar na sala do Quem é Quem: {e}")
        
        # Painel do Jogo Ativo
        else:
            st.write(f"🏠 Grupo: **{st.session_state.qq_turma}** | Sala: **{st.session_state.qq_sala}**")
            st.write(f"Seu Nick Secreto (Identidade Visual): **{st.session_state.username_atual}**")
            
            try:
                parceiros = supabase.table("jogadores").select("nick").eq("sala", st.session_state.qq_sala).execute()
                lista_nicks = [p['nick'] for p in parceiros.data] if parceiros.data else []
                if lista_nicks: st.caption(f"🕵️‍♂️ Suspeitos conectados nesta sala: {', '.join(lista_nicks)}")
            except: pass

            aba_pistas, aba_palpites, aba_regras = st.tabs(["💬 Modo Walkie-Talkie / Chat", "🚨 Dar Palpite", "📜 Regras"])
            
            # --- ABA 1: CHAT ---
            with aba_pistas:
                modo_comunicacao = st.radio("Como deseja enviar sua pista?", ["Texto Tradicional", "🎤 Ligação Walkie-Talkie (Anônima)"], horizontal=True)
                
                if modo_comunicacao == "Texto Tradicional":
                    pergunta = st.text_input("Sua Pista por texto:", placeholder="Escreva aqui...", key="input_pista")
                    if st.button("Enviar Pista por Texto"):
                        if pergunta.strip() != "":
                            supabase.table("mensagens").insert({
                                "jogador": st.session_state.username_atual, "texto": pergunta.strip(), "sala": st.session_state.qq_sala
                            }).execute()
                            st.toast("Pista enviada! 🚀")
                            st.rerun()
                else:
                    st.markdown("### 🎙️ Central do Walkie-Talkie")
                    efeito = st.selectbox("Escolha seu disfarce de voz:", ["Voz Normal", "🦹‍♂️ Vilão (Grave)", "🐿️ Esquilo (Fino)", "🤖 Robô / Ciborgue"])
                    audio_capturado = st.audio_input("Grave seu áudio de pista:")
                    
                    if audio_capturado is not None:
                        bytes_originais = audio_capturado.read()
                        if st.button("🚀 Enviar Áudio com Disfarce", use_container_width=True):
                            try:
                                with st.spinner("Modificando voz... ⚡"):
                                    bytes_modificados = aplicar_modificador_voz(bytes_originais, efeito)
                                    nome_arq = f"audio_{int(time.time())}_{st.session_state.username_atual}.wav"
                                    
                                    supabase.storage.from_("audios_jogo").upload(path=nome_arq, file=bytes_modificados, file_options={"content-type": "audio/wav"})
                                    url_som_publica = supabase.storage.from_("audios_jogo").get_public_url(nome_arq)
                                    
                                    supabase.table("mensagens").insert({
                                        "jogador": st.session_state.username_atual, "texto": f"📢 [Mensagem de Voz - Disfarce: {efeito}]", "audio_url": url_som_publica, "sala": st.session_state.qq_sala
                                    }).execute()
                                    st.success("Áudio enviado!")
                                    st.rerun()
                            except Exception as e: st.error(f"Erro: {e}")
                
                st.markdown("---")
                st.subheader("📋 Histórico de Pistas Recentes")
                try:
                    historico = supabase.table("mensagens").select("*").eq("sala", st.session_state.qq_sala).order("created_at", desc=True).execute()
                    if historico.data:
                        for msg in historico.data:
                            with st.container(border=True):
                                st.markdown(f"**🕵️‍♂️ Pista recebida:**")
                                st.write(msg['texto'])
                                if msg.get('audio_url'): st.audio(msg['audio_url'], format="audio/wav")
                    else: st.write("Nenhuma pista enviada ainda.")
                except: st.write("Aguardando novas pistas...")

            # --- ABA 2: PALPITES ---
            with aba_palpites:
                st.subheader("Quem você acha que é?")
                nick_suspeito = st.text_input("Nick Secreto do Suspeito:", placeholder="Ex: rafael12", key="nick_s").strip()
                palpite_nome_real = st.text_input("Qual o Nome Verdadeiro dele?", placeholder="Ex: Rafael", key="nome_s").strip()
                
                if st.button("Lançar Palpite Oficial 🚨"):
                    if nick_suspeito and palpite_nome_real:
                        try:
                            busca = supabase.table("jogadores").select("nome_real").eq("sala", st.session_state.qq_sala).eq("nick", nick_suspeito).execute()
                            resultado_status = "❌ ERROU"
                            if busca.data:
                                if busca.data[0]['nome_real'].lower() == palpite_nome_real.lower():
                                    resultado_status = "💥 ACERTOU EM CHEIO! DESMASCARADO!"
                            
                            supabase.table("palpites").insert({
                                "acusador": st.session_state.username_atual, "suspeito": f"{nick_suspeito} ({palpite_nome_real})", "palpite": resultado_status, "sala": st.session_state.qq_sala
                            }).execute()
                            
                            if "💥" in resultado_status: st.balloons(); st.success(resultado_status)
                            else: st.error(resultado_status)
                            st.rerun()
                        except Exception as e: st.error(f"Erro: {e}")

                st.markdown("---")
                st.subheader("📢 Histórico de Acusações")
                try:
                    lista_palpites = supabase.table("palpites").select("*").eq("sala", st.session_state.qq_sala).order("created_at", desc=True).execute()
                    for pal in lista_palpites.data:
                        if "💥" in pal['palpite']: st.success(f"💥 **{pal['acusador']}** desmascarou o suspeito!")
                        else: st.warning(f"🕵️‍♂️ **{pal['acusador']}** acusou **{pal['suspeito']}** ➔ {pal['palpite']}")
                except: st.write("Sem acusações feitas.")

            # --- ABA 3: REGRAS ---
            with aba_regras:
                st.subheader("📜 Como Jogar")
                st.markdown("1. Digite seu nome real e o nome do seu grupo.\n2. Mande áudios anônimos usando o Walkie-Talkie com modificador de voz.\n3. Descubra o nome real por trás do Nick de cada colega!")

                        # --- FINAL DO QUEM É QUEM (JOGO 3) ---
            if st.button("🚪 Sair do Quem é Quem"):
                try: 
                    supabase.table("jogadores").delete().eq("nick", st.session_state.username_atual).eq("sala", st.session_state.qq_sala).execute()
                except: 
                    pass
                st.session_state.qq_registrado = False
                st.rerun()

    # ================= JOGO 4: UNO MULTIPLAYER =================
    elif jogo_escolhido == "🃏 Jogo do UNO (Multiplayer)":
        st.subheader("🃏 UNO EXV — Multiplayer em Tempo Real")
     
        # Inicializa estados do UNO na sessão
        if "uno_sala_id" not in st.session_state:
            st.session_state.uno_sala_id = None
            st.session_state.uno_meu_numero = None
            st.session_state.minhas_cartas = []

        # --- SISTEMA DE LOGOBY / SALAS ---
        if st.session_state.uno_sala_id is None:
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                if st.button("🆕 Criar Sala de UNO"):
                    try:
                        # Cria o baralho inicial e sorteia a primeira carta da mesa
                        cores = ["Vermelho", "Azul", "Amarelo", "Verde"]
                        valores = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+2", "Bloqueio", "Inverter"]
                        baralho_completo = [f"{c} {v}" for c in cores for v in valores] + ["Coringa", "Coringa +4"] * 2
                        
                        carta_inicial = random.choice([c for c in baralho_completo if "Coringa" not in c])
                        cor_inicial = carta_inicial.split()[0]
                        
                        # Sorteia as 7 cartas do Criador da Sala
                        minhas_7 = [random.choice(baralho_completo) for _ in range(7)]
                        st.session_state.minhas_cartas = minhas_7

                        nova_sala = supabase.table("partidas_uno").insert({
                            "jogador_1": st.session_state.username_atual,
                            "status": "aguardando",
                            "turno": st.session_state.username_atual,
                            "carta_mesa": carta_inicial,
                            "cor_atual": cor_inicial
                        }).execute()
                        
                        if len(nova_sala.data) > 0:
                            id_sala = nova_sala.data[0]["id"]
                            st.session_state.uno_sala_id = id_sala
                            st.session_state.uno_meu_numero = 1
                            
                            # Salva a mão inicial no banco
                            supabase.table("maos_uno").insert({
                                "sala_id": id_sala, "jogador": st.session_state.username_atual, "cartas": minhas_7
                            }).execute()
                            st.rerun()
                    except Exception as e: st.error(f"Erro ao criar sala de UNO: {e}")

            with col_u2:
                st.write("**Salas de UNO esperando:**")
                try:
                    salas_uno = supabase.table("partidas_uno").select("*").eq("status", "aguardando").execute()
                    if len(salas_uno.data) == 0: st.caption("Nenhuma sala de UNO aberta.")
                    for sala in salas_uno.data:
                        if sala["jogador_1"] != st.session_state.username_atual:
                            if st.button(f"Jogar contra {sala['jogador_1']}", key=f"uno_{sala['id']}"):
                                # Sorteia as 7 cartas do jogador 2
                                cores = ["Vermelho", "Azul", "Amarelo", "Verde"]
                                valores = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+2", "Bloqueio", "Inverter"]
                                baralho_completo = [f"{c} {v}" for c in cores for v in valores] + ["Coringa", "Coringa +4"] * 2
                                suas_7 = [random.choice(baralho_completo) for _ in range(7)]
                                st.session_state.minhas_cartas = suas_7

                                supabase.table("partidas_uno").update({
                                    "jogador_2": st.session_state.username_atual, "status": "jogando"
                                }).eq("id", sala["id"]).execute()
                                
                                supabase.table("maos_uno").insert({
                                    "sala_id": sala["id"], "jogador": st.session_state.username_atual, "cartas": suas_7
                                }).execute()

                                st.session_state.uno_sala_id = sala["id"]
                                st.session_state.uno_meu_numero = 2
                                st.rerun()
                except Exception as e: st.error(f"Erro ao buscar salas: {e}")
        
        # --- DENTRO DA PARTIDA DE UNO ---
        else:
            try:
                dados_uno = supabase.table("partidas_uno").select("*").eq("id", st.session_state.uno_sala_id).execute().data[0]
                # Puxa a mão atualizada do banco de dados
                minha_mao_banco = supabase.table("maos_uno").select("cartas").eq("sala_id", st.session_state.uno_sala_id).eq("jogador", st.session_state.username_atual).execute().data[0]["cartas"]
                st.session_state.minhas_cartas = minha_mao_banco
            except:
                st.session_state.uno_sala_id = None
                st.rerun()

            if st.sidebar.button("🏳️ Abandonar UNO"):
                supabase.table("partidas_uno").update({"status": "finalizado"}).eq("id", st.session_state.uno_sala_id).execute()
                st.session_state.uno_sala_id = None
                st.rerun()

            if dados_uno["status"] == "aguardando":
                st.warning("⏳ Aguardando um amigo entrar na partida...")
                if st.button("🔄 Atualizar"): st.rerun()
            
            elif dados_uno["status"] == "jogando":
                oponente = dados_uno["jogador_2"] if st.session_state.uno_meu_numero == 1 else dados_uno["jogador_1"]
                st.write(f"⚔️ Duelando contra: **{oponente}**")
                
                # Exibe a mesa
                st.markdown("### 🎴 Mesa do Jogo")
                carta_mesa = dados_uno["carta_mesa"]
                cor_ativa = dados_uno["cor_atual"]
                
                # Estiliza a cor de fundo da mesa
                cor_hex = "#DC3545" if cor_ativa == "Vermelho" else "#007BFF" if cor_ativa == "Azul" else "#FFC107" if cor_ativa == "Amarelo" else "#28A745"
                texto_cor = "#000" if cor_ativa == "Amarelo" else "#FFF"
                
                st.markdown(f"""
                <div style='background-color: {cor_hex}; padding: 25px; border-radius: 12px; text-align: center; color: {texto_cor}; font-size: 24px; font-weight: bold; border: 4px solid white;'>
                    {carta_mesa}<br><span style='font-size: 14px;'>Cor Ativa: {cor_ativa}</span>
                </div>
                """, unsafe_url_allowed=True)
                
                # Turno
                st.write("")
                meu_turno = dados_uno["turno"] == st.session_state.username_atual
                if meu_turno:
                    st.success("🟢 É a SUA vez de jogar!")
                else:
                    st.warning(f"🟡 Vez de **{dados_uno['turno']}** jogar...")
                    if st.button("🔄 Ver se já jogaram"): st.rerun()

                st.write("---")
                
                # --- EXIBE AS CARTAS DO JOGADOR ---
                st.markdown("### 🖐️ Sua Mão")
                
                # Botão de COMPRAR CARTA
                if meu_turno:
                    if st.button("📥 Comprar 1 Carta do Baralho", use_container_width=True):
                        cores = ["Vermelho", "Azul", "Amarelo", "Verde"]
                        valores = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+2", "Bloqueio", "Inverter"]
                        baralho_completo = [f"{c} {v}" for c in cores for v in valores] + ["Coringa", "Coringa +4"] * 2
                        nova_carta = random.choice(baralho_completo)
                        
                        nova_mao = st.session_state.minhas_cartas + [nova_carta]
                        supabase.table("maos_uno").update({"cartas": nova_mao}).eq("sala_id", st.session_state.uno_sala_id).eq("jogador", st.session_state.username_atual).execute()
                        
                        # Passa o turno para o oponente
                        supabase.table("partidas_uno").update({"turno": oponente}).eq("id", st.session_state.uno_sala_id).execute()
                        st.success(f"Você comprou: {nova_carta}!")
                        st.rerun()

                # Listando as cartas em formato de botões organizados
                colunas_cartas = st.columns(4)
                for idx, carta in enumerate(st.session_state.minhas_cartas):
                    col_idx = colunas_cartas[idx % 4]
                    with col_idx:
                        # Validação de regras do UNO
                        pode_jogar = False
                        if "Coringa" in carta:
                            pode_jogar = True
                        else:
                            cor_carta = carta.split()[0]
                            valor_carta = carta.split()[1] if len(carta.split()) > 1 else ""
                            
                            cor_mesa = carta_mesa.split()[0]
                            valor_mesa = carta_mesa.split()[1] if len(carta_mesa.split()) > 1 else ""
                            
                            if cor_carta == cor_ativa or valor_carta == valor_mesa:
                                p_jogar = True
                                pode_jogar = True

                        if st.button(f"{carta}", key=f"c_{idx}", disabled=not (meu_turno and pode_jogar), use_container_width=True):
                            # LÓGICA DE DESCARTAR CARTA
                            nova_mao = list(st.session_state.minhas_cartas)
                            carta_jogada = nova_mao.pop(idx)
                            
                            # Define nova cor ativa
                            nova_cor = cor_ativa
                            if "Coringa" not in carta_jogada:
                                nova_cor = carta_jogada.split()[0]
                            else:
                                # Se jogou Coringa, por padrão vamos mudar para uma cor aleatória ou padrão para simplificar nesta fase alpha
                                nova_cor = random.choice(["Vermelho", "Azul", "Amarelo", "Verde"])
                                st.toast(f"Coringa jogado! Cor alterada para {nova_cor} automaticamente!")

                            # Checa Vitória (UNO!)
                            if len(nova_mao) == 0:
                                supabase.table("partidas_uno").update({"status": "finalizado", "turno": f"🏆 {st.session_state.username_atual} GANHOU!"}).eq("id", st.session_state.uno_sala_id).execute()
                                st.balloons()
                                st.success("Você Venceu o Jogo! 🏆")
                            
                            # Atualiza mão e mesa no Supabase
                            supabase.table("maos_uno").update({"cartas": nova_mao}).eq("sala_id", st.session_state.uno_sala_id).eq("jogador", st.session_state.username_atual).execute()
                            
                            # Passa turno (+2 e Bloqueio podem ser implementados na próxima fase!)
                            supabase.table("partidas_uno").update({
                                "carta_mesa": carta_jogada,
                                "cor_atual": nova_cor,
                                "turno": oponente
                            }).eq("id", st.session_state.uno_sala_id).execute()
                            
                            st.rerun()
            
            elif "GANHOU" in dados_uno["turno"]:
                st.success(f"🎮 Fim de Jogo: {dados_uno['turno']}")
                if st.button("Voltar ao Menu Principal"):
                    st.session_state.uno_sala_id = None
                    st.rerun()
            
