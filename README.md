# 🐾 Nacho – AI HelpDesk Assistant

> CS50x Final Project | Seu assistente inteligente de TI

![Python](https://img.shields.io/badge/Python-Flask-blue)
![SQL](https://img.shields.io/badge/SQL-SQLite-green)
![AI](https://img.shields.io/badge/AI-Claude%20API-orange)

---

## 📋 Descrição

**Nacho** é um assistente de HelpDesk de TI com personalidade de Beagle, construído com Flask, SQLite e integração opcional com a API da Anthropic (Claude). Ele resolve os **14 problemas de TI mais comuns** de forma inteligente, com proteção contra uso fora do escopo.

---

## 🚀 Como rodar

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. (Opcional) Configure a API Key da Anthropic

Para respostas aprimoradas com IA:

```bash
export ANTHROPIC_API_KEY="sua-chave-aqui"
```

Sem a chave, o Nacho usa as respostas do banco de dados (funciona perfeitamente).

### 3. Inicialize o banco e rode

```bash
python app.py
```

Acesse: **http://localhost:5000**

Dashboard admin: **http://localhost:5000/dashboard**

---

## 🗂️ Estrutura do Projeto

```
nacho-helpdesk/
├── app.py                  # Flask app principal (rotas, lógica de chat)
├── requirements.txt
├── database/
│   ├── init_db.py          # Schema SQL + 14 problemas seed
│   └── helpdesk.db         # SQLite (gerado automaticamente)
├── templates/
│   ├── index.html          # Interface de chat
│   └── dashboard.html      # Painel de estatísticas (Admin)
└── static/
    ├── css/
    │   ├── style.css       # Estilos globais (tema Beagle)
    │   └── dashboard.css   # Estilos do dashboard
    └── js/
        ├── chat.js         # Lógica do chat (mensagens, feedback)
        └── dashboard.js    # Animações do dashboard
```

---

## 🔧 Tecnologias

| Stack      | Uso                                    |
|-----------|----------------------------------------|
| Python 3  | Linguagem principal                    |
| Flask     | Framework web                          |
| SQLite    | Banco de dados dos 14 problemas        |
| HTML/CSS  | Interface responsiva                   |
| JavaScript| Interatividade do chat                 |
| JSON      | Comunicação API REST                   |
| Claude AI | Enriquecimento das respostas (opcional)|

---

## 🧠 Os 14 Problemas de HelpDesk

1. VPN sem acesso
2. Impressora não imprime
3. Senha esquecida
4. Wi-Fi sem conexão
5. Computador lento
6. E-mail com falha
7. Câmera em videoconferência
8. Instalação de software bloqueada
9. Tela azul (BSOD)
10. Arquivos sumidos ou deletados
11. Acesso a sistema/plataforma negado
12. Microfone com problema
13. Atualização do Windows falhando
14. Compartilhamento de rede inoperante

---

## 🔐 Segurança

- Sessões limitadas: após **3 tentativas** fora do escopo de HelpDesk, a sessão é encerrada automaticamente
- Nacho não responde perguntas fora de TI/HelpDesk
- Cada sessão tem um UUID único

---

## 🎨 Design

Paleta inspirada nas cores do Beagle:
- **Marrom escuro**: `#4A2512` (sidebar)
- **Marrom médio**: `#A0522D` (acentos)
- **Creme**: `#F5EBE0` (fundos)
- **Laranja**: `#E8712A` (CTAs)

---

*Nacho aprovado! 🐾*
