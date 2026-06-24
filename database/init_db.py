import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "helpdesk.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    keywords TEXT NOT NULL,
    solution TEXT NOT NULL,
    solution_en TEXT NOT NULL DEFAULT '',
    usage_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    problem_id INTEGER,
    was_helpful INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problem_id) REFERENCES problems(id)
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    off_topic_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    closed INTEGER DEFAULT 0
);
"""

# Each tuple: (title, category, keywords, solution_pt, solution_en)
PROBLEMS = [
    (
        "Não consigo acessar a VPN",
        "VPN",
        "vpn,acesso,conectar,rede privada,tunnel,cisco,anyconnect,pulse,cannot access,connect",
        """1. Verifique se sua conexão com a internet está funcionando (abra um site qualquer).
2. Confirme se o usuário e senha do VPN estão corretos (sem CAPS LOCK ativo).
3. Feche completamente o cliente VPN e abra novamente.
4. Reinicie o computador e tente conectar novamente.
5. Verifique se o firewall ou antivírus está bloqueando o cliente VPN.
6. Tente se conectar a uma rede diferente (dados móveis do celular).
7. Se o erro persistir, entre em contato com o Service Desk informando o código de erro exibido.""",
        """1. Check that your internet connection is working (open any website).
2. Confirm your VPN username and password are correct (no CAPS LOCK active).
3. Fully close the VPN client and reopen it.
4. Restart your computer and try connecting again.
5. Check if your firewall or antivirus is blocking the VPN client.
6. Try connecting from a different network (mobile hotspot).
7. If the error persists, contact the Service Desk with the error code displayed."""
    ),
    (
        "Minha impressora não imprime",
        "Impressora",
        "impressora,imprimir,impressão,printer,papel,tinta,toner,offline,not printing,print",
        """1. Verifique se a impressora está ligada e com papel na bandeja.
2. Confirme se o cabo USB/rede está bem conectado, ou se está na mesma rede Wi-Fi.
3. No Windows: vá em Dispositivos e Impressoras → clique com botão direito → "Ver o que está imprimindo" → cancele todos os trabalhos.
4. Defina a impressora como padrão se necessário.
5. Reinicie o serviço de spooler: Win+R → services.msc → Print Spooler → Reiniciar.
6. Verifique os níveis de tinta/toner pela própria impressora ou software.
7. Reinstale o driver da impressora caso necessário.""",
        """1. Check that the printer is powered on and has paper in the tray.
2. Confirm the USB/network cable is properly connected, or that it's on the same Wi-Fi network.
3. On Windows: go to Devices and Printers → right-click → "See what's printing" → cancel all jobs.
4. Set the printer as default if needed.
5. Restart the spooler service: Win+R → services.msc → Print Spooler → Restart.
6. Check ink/toner levels via the printer itself or its software.
7. Reinstall the printer driver if necessary."""
    ),
    (
        "Esqueci minha senha",
        "Senha",
        "senha,password,esqueci,resetar,redefinir,login,acesso,bloqueado,forgot,reset,locked",
        """1. Acesse o portal de autoatendimento da empresa para redefinir sua senha (geralmente intranet/reset).
2. Use a opção "Esqueci minha senha" na tela de login do Windows ou sistema.
3. Se usar autenticação multifator (MFA), verifique seu e-mail ou app autenticador.
4. Senhas corporativas geralmente exigem: mínimo 8 caracteres, maiúsculas, minúsculas, número e símbolo.
5. Não reutilize as últimas 5 senhas cadastradas.
6. Após redefinir, troque a senha no primeiro login em TODOS os dispositivos.
7. Se a conta estiver bloqueada por tentativas, aguarde 15 minutos ou acione o Service Desk.""",
        """1. Access the company self-service portal to reset your password (usually intranet/reset).
2. Use the "Forgot my password" option on the Windows or system login screen.
3. If using multi-factor authentication (MFA), check your email or authenticator app.
4. Corporate passwords usually require: minimum 8 characters, uppercase, lowercase, number and symbol.
5. Do not reuse your last 5 passwords.
6. After resetting, change the password on first login on ALL devices.
7. If the account is locked due to too many attempts, wait 15 minutes or contact the Service Desk."""
    ),
    (
        "Erro ao conectar no Wi-Fi",
        "Rede",
        "wifi,wi-fi,wireless,internet,sem fio,rede,conexão,sinal,not connecting,network,signal",
        """1. Verifique se o Wi-Fi está ativado no dispositivo (ícone de avião desativado?).
2. Esqueça a rede e reconecte: clique na rede → Esquecer → conecte novamente com a senha.
3. Reinicie o roteador (desplugue por 30 segundos).
4. Verifique se outros dispositivos conseguem se conectar à mesma rede.
5. No Windows: Configurações → Rede → Solucionar problemas.
6. Atualize o driver da placa de rede Wi-Fi.
7. Se for rede corporativa, verifique se seu dispositivo está cadastrado no sistema de controle de acesso (NAC).""",
        """1. Check that Wi-Fi is enabled on your device (is airplane mode off?).
2. Forget the network and reconnect: click the network → Forget → reconnect with the password.
3. Restart the router (unplug for 30 seconds).
4. Check if other devices can connect to the same network.
5. On Windows: Settings → Network → Troubleshoot.
6. Update the Wi-Fi network adapter driver.
7. On a corporate network, check if your device is registered in the access control system (NAC)."""
    ),
    (
        "Computador muito lento",
        "Desempenho",
        "lento,travando,demora,performance,cpu,memória,ram,disco,processador,slow,freezing,lagging",
        """1. Reinicie o computador — muitos processos acumulam na memória.
2. Verifique o uso de CPU e memória: Ctrl+Shift+Esc → aba Desempenho.
3. Encerre programas em segundo plano desnecessários na aba Processos.
4. Desative programas na inicialização: Gerenciador de Tarefas → aba Inicializar.
5. Verifique espaço em disco — mantenha ao menos 10% livre no disco C:.
6. Execute limpeza de disco: Win+R → cleanmgr.
7. Verifique se há atualizações do Windows ou antivírus em execução consumindo recursos.""",
        """1. Restart your computer — many processes accumulate in memory over time.
2. Check CPU and memory usage: Ctrl+Shift+Esc → Performance tab.
3. End unnecessary background programs in the Processes tab.
4. Disable startup programs: Task Manager → Startup tab.
5. Check disk space — keep at least 10% free on the C: drive.
6. Run disk cleanup: Win+R → cleanmgr.
7. Check if Windows updates or antivirus scans are running in the background."""
    ),
    (
        "E-mail não está funcionando",
        "E-mail",
        "email,e-mail,outlook,correio,mensagem,enviar,receber,corporativo,exchange,not working,send,receive",
        """1. Verifique sua conexão com a internet.
2. No Outlook: olhe o rodapé — se mostrar "Desconectado" ou "Trabalhando offline", clique em Enviar/Receber → Trabalhar Online.
3. Verifique se a caixa de entrada está cheia (cota excedida).
4. Tente acessar o webmail pelo navegador (OWA) para isolar o problema.
5. Feche e reabra o Outlook. Se não abrir, tente no Modo Seguro: Win+R → outlook /safe.
6. Recriar o perfil do Outlook pode resolver: Painel de Controle → Mail → Perfis.
7. Verifique com o Service Desk se há alguma manutenção no servidor de e-mail.""",
        """1. Check your internet connection.
2. In Outlook: look at the status bar — if it shows "Disconnected" or "Working Offline", click Send/Receive → Work Online.
3. Check if your inbox is full (quota exceeded).
4. Try accessing webmail via browser (OWA) to isolate the problem.
5. Close and reopen Outlook. If it won't open, try Safe Mode: Win+R → outlook /safe.
6. Recreating the Outlook profile may help: Control Panel → Mail → Profiles.
7. Check with the Service Desk if there is scheduled maintenance on the mail server."""
    ),
    (
        "Câmera não funciona em videoconferência",
        "Videoconferência",
        "camera,câmera,webcam,teams,zoom,meet,videoconferência,reunião,vídeo,not working,video call",
        """1. Verifique se a câmera está conectada corretamente (USB) ou se é integrada ao notebook.
2. Permissões do navegador/app: clique no cadeado na barra de endereço → permita Câmera.
3. No Windows: Configurações → Privacidade → Câmera → permita acesso aos apps.
4. Feche outros aplicativos que possam estar usando a câmera simultaneamente.
5. Atualize ou reinstale o driver da câmera no Gerenciador de Dispositivos.
6. Teste a câmera no app Câmera do Windows para verificar se o hardware funciona.
7. Em reuniões Teams/Zoom: verifique as configurações de vídeo dentro do próprio app.""",
        """1. Check if the camera is properly connected (USB) or if it's a built-in laptop camera.
2. Browser/app permissions: click the padlock in the address bar → allow Camera.
3. On Windows: Settings → Privacy → Camera → allow access for apps.
4. Close other applications that may be using the camera simultaneously.
5. Update or reinstall the camera driver in Device Manager.
6. Test the camera in the Windows Camera app to confirm the hardware works.
7. In Teams/Zoom meetings: check the video settings within the app itself."""
    ),
    (
        "Não consigo instalar um programa",
        "Software",
        "instalar,instalação,programa,software,aplicativo,permissão,bloqueado,admin,install,blocked,permission",
        """1. Verifique se você tem permissões de administrador — a maioria das instalações corporativas requer aprovação de TI.
2. Em ambientes corporativos, use o portal de software aprovado (Software Center, Intune, etc.).
3. Se for software autorizado: clique com botão direito no instalador → Executar como administrador.
4. Verifique se há espaço suficiente no disco.
5. Desative temporariamente o antivírus e tente novamente (apenas para software confiável).
6. Verifique se o .NET Framework ou outro pré-requisito está instalado.
7. Abra uma solicitação no Service Desk para instalação de software — nossa equipe pode fazer remotamente.""",
        """1. Check if you have administrator permissions — most corporate installs require IT approval.
2. In corporate environments, use the approved software portal (Software Center, Intune, etc.).
3. For authorized software: right-click the installer → Run as administrator.
4. Check if there is enough free disk space.
5. Temporarily disable antivirus and try again (only for trusted software).
6. Check if .NET Framework or another prerequisite is installed.
7. Submit a request to the Service Desk for software installation — our team can do it remotely."""
    ),
    (
        "Tela azul (BSOD)",
        "Sistema",
        "tela azul,bsod,blue screen,travou,reiniciou,crash,kernel,dump,error,stop code",
        """1. Anote ou fotografe o código de erro exibido (ex: MEMORY_MANAGEMENT, DRIVER_IRQL).
2. Reinicie o computador — muitas vezes é um evento isolado.
3. Se for recorrente, inicialize no Modo Seguro: segure Shift ao clicar em Reiniciar → Modo de Segurança.
4. Verifique drivers recém-instalados/atualizados e faça rollback se necessário.
5. Execute: sfc /scannow no Prompt de Comando como administrador.
6. Verifique a memória RAM com o Windows Memory Diagnostic.
7. Encaminhe o código de erro e a frequência ao Service Desk para análise do minilog.""",
        """1. Note or photograph the error code displayed (e.g. MEMORY_MANAGEMENT, DRIVER_IRQL).
2. Restart your computer — it is often an isolated event.
3. If it recurs, boot into Safe Mode: hold Shift while clicking Restart → Safe Mode.
4. Check recently installed/updated drivers and roll back if necessary.
5. Run: sfc /scannow in Command Prompt as administrator.
6. Test your RAM with Windows Memory Diagnostic.
7. Send the error code and frequency to the Service Desk for minidump analysis."""
    ),
    (
        "Arquivos sumidos ou deletados",
        "Arquivos",
        "arquivo,sumiu,deletado,perdeu,pasta,documento,excluído,recovery,backup,missing,deleted,lost,files",
        """1. Verifique a Lixeira do Windows — o arquivo pode estar lá.
2. Use a busca do Windows Explorer (Win+E → barra de busca) com o nome do arquivo.
3. Verifique versões anteriores: clique com botão direito na pasta → Propriedades → Versões Anteriores.
4. Se eram arquivos na rede, verifique a pasta de Backup do servidor com o Service Desk.
5. Nunca salve a recuperação na mesma partição de onde o arquivo foi perdido.
6. Ferramentas de recuperação como Recuva podem ajudar em discos locais.
7. Abra um chamado imediatamente — quanto antes, maior a chance de recuperação.""",
        """1. Check the Windows Recycle Bin — the file may be there.
2. Use Windows Explorer search (Win+E → search bar) with the file name.
3. Check previous versions: right-click the folder → Properties → Previous Versions.
4. If they were network files, check the server Backup folder with the Service Desk.
5. Never save the recovery to the same partition where the file was lost.
6. Recovery tools like Recuva can help on local drives.
7. Open a ticket immediately — the sooner, the better the chances of recovery."""
    ),
    (
        "Sem acesso a sistema ou plataforma interna",
        "Acesso",
        "acesso,sistema,plataforma,portal,erp,crm,intranet,permissão,bloqueado,login,access denied,no access",
        """1. Verifique se sua senha está correta e se não expirou.
2. Confirme se você tem perfil de acesso ao sistema — pode precisar de aprovação do gestor.
3. Tente acessar pelo navegador em modo anônimo para descartar cache/cookies.
4. Limpe o cache do navegador: Ctrl+Shift+Del → Limpar dados de navegação.
5. Tente em um navegador diferente.
6. Verifique se o sistema está em manutenção na página de status da TI.
7. Solicite ao seu gestor a abertura de uma solicitação de acesso formal no Service Desk.""",
        """1. Check that your password is correct and has not expired.
2. Confirm you have an access profile for the system — manager approval may be required.
3. Try accessing via an incognito browser window to rule out cache/cookies.
4. Clear browser cache: Ctrl+Shift+Del → Clear browsing data.
5. Try a different browser.
6. Check if the system is under maintenance on the IT status page.
7. Ask your manager to submit a formal access request to the Service Desk."""
    ),
    (
        "Microfone não funciona",
        "Áudio",
        "microfone,audio,som,teams,zoom,meet,falar,reunião,headset,fone,microphone,mic,sound,not working",
        """1. Verifique se o microfone está conectado corretamente (P2 ou USB).
2. No Windows: Configurações → Sistema → Som → Entrada — selecione o microfone correto.
3. Permissões: Configurações → Privacidade → Microfone → ative o acesso.
4. Verifique se o microfone não está mutado (botão físico no headset ou teclado).
5. Em Teams/Zoom: Configurações → Áudio → selecione o dispositivo de entrada correto.
6. Teste com outro aplicativo (Gravador de Voz do Windows) para confirmar se é hardware.
7. Atualize o driver de áudio pelo Gerenciador de Dispositivos.""",
        """1. Check that the microphone is properly connected (3.5mm jack or USB).
2. On Windows: Settings → System → Sound → Input — select the correct microphone.
3. Permissions: Settings → Privacy → Microphone → enable access.
4. Check that the microphone is not muted (physical button on headset or keyboard).
5. In Teams/Zoom: Settings → Audio → select the correct input device.
6. Test with another app (Windows Voice Recorder) to confirm if it's a hardware issue.
7. Update the audio driver via Device Manager."""
    ),
    (
        "Atualização do Windows travada ou falhando",
        "Atualização",
        "atualização,windows update,update,travada,falhando,erro,instalação,pendente,stuck,failing,failed",
        "1. Aguarde — algumas atualizações grandes podem levar 30–60 minutos.\n"
        "2. Reinicie o computador e deixe o processo de 'Configurando atualizações' concluir.\n"
        "3. Execute o Windows Update Troubleshooter: Configurações → Atualização → Solucionar Problemas.\n"
        "4. Libere espaço em disco — atualizações precisam de pelo menos 5-10 GB livres.\n"
        r"5. No cmd como administrador: net stop wuauserv → exclua C:\Windows\SoftwareDistribution\Download → net start wuauserv." + "\n"
        "6. Verifique o histórico de atualizações para identificar o código de erro específico.\n"
        "7. Em ambiente corporativo, atualizações são gerenciadas pelo WSUS — entre em contato com TI.",
        "1. Wait — large updates can take 30–60 minutes.\n"
        "2. Restart your computer and let the 'Configuring updates' process complete.\n"
        "3. Run the Windows Update Troubleshooter: Settings → Update → Troubleshoot.\n"
        "4. Free up disk space — updates need at least 5–10 GB free.\n"
        r"5. In cmd as administrator: net stop wuauserv → delete C:\Windows\SoftwareDistribution\Download → net start wuauserv." + "\n"
        "6. Check update history to identify the specific error code.\n"
        "7. In corporate environments, updates are managed by WSUS — contact IT."
    ),
    (
        "Compartilhamento de arquivos na rede não funciona",
        "Rede",
        "compartilhamento,pasta,rede,mapeamento,drive,servidor,smb,acesso negado,network share,shared folder,mapped drive",
        """1. Verifique se você está conectado à rede corporativa ou VPN.
2. Confirme o endereço do servidor: tente acessar pelo IP (ex: \\\\192.168.1.100\\pasta).
3. No Windows Explorer: \\\\nomeDoServidor — se não abrir, verifique a conectividade.
4. Verifique se o serviço de compartilhamento está ativo: Painel de Controle → Central de Rede → Configurações de Compartilhamento.
5. Remapeie o drive de rede: clique com botão direito em Este Computador → Mapear unidade de rede.
6. Credenciais salvas incorretas: Painel de Controle → Gerenciador de Credenciais → remova entradas antigas.
7. Solicite ao Service Desk verificação das permissões NTFS/Share no servidor.""",
        r"""1. Check that you are connected to the corporate network or VPN.
2. Confirm the server address: try accessing by IP (e.g. \\192.168.1.100\folder).
3. In Windows Explorer: \\serverName — if it doesn't open, check connectivity.
4. Check if the sharing service is active: Control Panel → Network Center → Sharing Settings.
5. Remap the network drive: right-click This PC → Map network drive.
6. Incorrect saved credentials: Control Panel → Credential Manager → remove old entries.
7. Ask the Service Desk to verify NTFS/Share permissions on the server."""
    ),
]


def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(SCHEMA)

    # Add solution_en column if it doesn't exist yet (migration)
    try:
        cursor.execute("ALTER TABLE problems ADD COLUMN solution_en TEXT NOT NULL DEFAULT ''")
        conn.commit()
        print("✅ Coluna solution_en adicionada.")
    except Exception:
        pass  # Column already exists

    cursor.execute("SELECT COUNT(*) FROM problems")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            "INSERT INTO problems (title, category, keywords, solution, solution_en) VALUES (?,?,?,?,?)",
            PROBLEMS
        )
        print(f"✅ {len(PROBLEMS)} problemas inseridos no banco de dados.")
    else:
        # Update solution_en for existing rows
        for p in PROBLEMS:
            cursor.execute(
                "UPDATE problems SET solution_en=? WHERE title=?",
                (p[4], p[0])
            )
        print(f"✅ solution_en atualizado para {len(PROBLEMS)} problemas.")

    conn.commit()
    conn.close()
    print(f"✅ Banco de dados inicializado em: {DB_PATH}")


if __name__ == "__main__":
    init_database()
