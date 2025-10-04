#  Sistema de Agendamento - Karine Almeida Centro Estético (Versão 2.0)

![Logo da Clínica](https://i.imgur.com/x07bOax.png)

## 📄 Descrição

Este é o projeto de um site institucional e sistema de agendamento online para o **Karine Almeida Centro Estético**. O site permite que clientes conheçam os serviços, entrem em contato e agendem horários de forma prática.

Esta versão inclui um robusto sistema de segurança para a área administrativa, com cadastro de múltiplos administradores e um fluxo de aprovação manual controlado pela dona do estabelecimento, garantindo total controle sobre quem pode gerenciar os agendamentos.

---

## ✨ Funcionalidades

### Para Clientes
-   **Homepage Atraente:** Apresentação profissional da clínica e seus valores.
-   **Página de Serviços:** Detalhamento de todos os tratamentos oferecidos.
-   **Formulário de Agendamento Inteligente:**
    -   Seleção de horários em intervalos fixos (08:00 - 18:00).
    -   **Validação de Disponibilidade:** O sistema impede agendamentos em horários já ocupados.
    -   **Campos Dinâmicos:** Um campo adicional para a área do corpo é exibido ao selecionar "Depilação a laser".
-   **Página de Contato:** Informações completas com endereço, WhatsApp, redes sociais e mapa.
-   **Página de Confirmação:** Mensagem de sucesso após um agendamento bem-sucedido.

### Para Administradores
-   **Sistema de Autenticação Seguro:**
    -   Página de login com design personalizado e profissional.
    -   As senhas são armazenadas com **hash**, garantindo que a senha original nunca seja salva.
    -   **Fluxo de Cadastro com Aprovação em 2 Etapas:**
        1. Novos administradores se cadastram através de um formulário.
        2. A conta fica "pendente" até que um administrador já ativo a aprove.
-   **Painel de Agendamentos (`/admin/agendamentos`):**
    -   Visualização completa de todos os agendamentos.
    -   Permite **Editar** e **Excluir** agendamentos existentes.
-   **Painel de Gerenciamento de Usuários (`/admin/usuarios`):**
    -   Lista de cadastros pendentes de aprovação.
    -   Botão para **Aprovar** novos administradores, liberando seu acesso.
    -   Lista de administradores já ativos.
    -   Opção de **Excluir** usuários (pendentes ou ativos).

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3
    * **Framework:** Flask
    * **Segurança:** Werkzeug (para hashing de senhas)
    * **Banco de Dados:** `mysql-connector-python`
* **Frontend:**
    * HTML5
    * CSS3 (com design personalizado)
    * Bootstrap 5
    * JavaScript
* **Banco de Dados:** MySQL Server

---

## 🚀 Instalação e Execução

Siga os passos abaixo para configurar e rodar o projeto localmente.

### Pré-requisitos
-   Python 3.8 ou superior
-   MySQL Server instalado e em execução (Ex: XAMPP, MySQL Workbench)

### Passo a Passo

1.  **Baixe os arquivos** para uma pasta no seu computador.

2.  **Crie e ative um ambiente virtual** dentro da pasta do projeto:
    ```bash
    # Criar o ambiente
    python -m venv venv

    # Ativar no Windows (PowerShell)
    .\venv\Scripts\Activate.ps1

    # Ativar no Mac/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o Banco de Dados:**
    -   Abra seu gerenciador de MySQL.
    -   Execute o script SQL abaixo para criar o banco de dados e as tabelas `agendamentos` e `usuarios`:

    ```sql
    CREATE DATABASE IF NOT EXISTS clinica_estetica CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    USE clinica_estetica;

    CREATE TABLE IF NOT EXISTS agendamentos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL,
        telefone VARCHAR(20),
        tratamento VARCHAR(100) NOT NULL,
        parte_corpo VARCHAR(100) NULL DEFAULT NULL,
        data DATE NOT NULL,
        horario TIME NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ```

5.  **Configure a Conexão no Código:**
    -   Abra o arquivo `app.py`.
    -   Localize a seção `DB_CONFIG` e altere a senha para a sua senha do MySQL.

    ```python
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'sua_senha', # <-- ALTERE AQUI
        'database': 'clinica_estetica'
    }
    ```

6.  **Ative o Primeiro Administrador:**
    -   Execute a aplicação com `python app.py`.
    -   Acesse a página de **Cadastro** (`/register`) e crie sua conta de administradora principal.
    -   Vá ao seu gerenciador MySQL e execute o comando abaixo, **substituindo pelo seu e-mail**:
    ```sql
    UPDATE clinica_estetica.usuarios SET is_active = TRUE WHERE email = 'seu-email-aqui@exemplo.com';
    ```

7.  **Execute a Aplicação:**
    -   Se o servidor não estiver rodando, inicie-o no terminal:
    ```bash
    python app.py
    ```

---

## 🌐 Acessando a Aplicação

* **Site Principal:** `http://127.0.0.1:5000/`
* **Página de Login:** `http://127.0.0.1:5000/login` (ou pelo atalho no rodapé do site)
* **Painel de Agendamentos:** `http://127.0.0.1:5000/admin/agendamentos`
* **Painel de Usuários:** `http://127.0.0.1:5000/admin/usuarios`