import os
import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2 # Apenas a biblioteca do PostgreSQL é necessária
from psycopg2.extras import RealDictCursor # Para obter dicionários como resultado
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURAÇÃO INICIAL ---
app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv("SECRET_KEY", "uma_chave_padrao_para_desenvolvimento")

# --- CONEXÃO COM BANCO DE DADOS NA NUVEM ---
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None

# --- DECORADOR DE LOGIN ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Por favor, faça o login para acessar esta página.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROTA DE INICIALIZAÇÃO DO BANCO (PARA USAR UMA ÚNICA VEZ) ---
@app.route('/init-db')
def init_db():
    conn = get_db_connection()
    if conn is None:
        return "Erro: Não foi possível conectar ao banco de dados."
    
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos (
        id SERIAL PRIMARY KEY, nome VARCHAR(100) NOT NULL, email VARCHAR(100) NOT NULL,
        telefone VARCHAR(20), tratamento VARCHAR(100) NOT NULL, parte_corpo VARCHAR(100),
        data DATE NOT NULL, horario TIME NOT NULL, criado_em TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY, username VARCHAR(80) UNIQUE NOT NULL, email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL, is_active BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    return "Tabelas 'agendamentos' e 'usuarios' criadas com sucesso!"

# --- ROTAS DE AUTENTICAÇÃO ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor) # ### CORRIGIDO ###
        cursor.execute("SELECT * FROM usuarios WHERE email = %s OR username = %s", (email, username))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Email ou nome de usuário já cadastrado.", "danger")
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        
        cursor.execute("INSERT INTO usuarios (username, email, password_hash) VALUES (%s, %s, %s)",
                       (username, email, password_hash))
        conn.commit()
        
        flash('Cadastro realizado com sucesso! Aguarde a aprovação da administradora para fazer o login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor) # ### CORRIGIDO ###
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user or not check_password_hash(user['password_hash'], password):
            flash('Email ou senha inválidos.', 'danger')
            return redirect(url_for('login'))
        
        if not user['is_active']:
            flash('Sua conta ainda não foi aprovada pela administradora.', 'warning')
            return redirect(url_for('login'))

        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect(url_for('listar_agendamentos'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Você foi desconectado.", "info")
    return redirect(url_for('login'))

# --- ROTAS PÚBLICAS ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/servicos")
def servicos():
    lista_servicos = [ "Depilação a laser", "Remoção de Tattoo/Micro", "Emagrecimento", "Tratamentos Faciais", "Tratamentos Corporais", "Tratamentos Capilares", "Micose de Unha a laser" ]
    return render_template("servicos.html", servicos=lista_servicos)

@app.route("/agendamento", methods=["GET", "POST"])
def agendamento():
    if request.method == "POST":
        nome, email, telefone = request.form.get("nome"), request.form.get("email"), request.form.get("telefone")
        tratamento, parte_corpo = request.form.get("tratamento"), request.form.get("parte_corpo")
        data_str, horario_str = request.form.get("data"), request.form.get("horario")

        conn = get_db_connection()
        if conn is None:
            flash("❌ Erro de conexão com o banco de dados. Tente mais tarde.", "danger")
            return redirect(url_for('agendamento'))

        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id FROM agendamentos WHERE data = %s AND horario = %s", (data_str, horario_str))
            horario_existente = cursor.fetchone()

            if horario_existente:
                data_formatada = datetime.datetime.strptime(data_str, '%Y-%m-%d').strftime('%d/%m/%Y')
                flash(f"❌ Desculpe, o horário das {horario_str} no dia {data_formatada} já está ocupado.", "danger")
                return redirect(url_for('agendamento'))

            sql = "INSERT INTO agendamentos (nome, email, telefone, tratamento, parte_corpo, data, horario) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (nome, email, telefone, tratamento, parte_corpo, data_str, horario_str)
            cursor.execute(sql, values)
            conn.commit()

            return redirect(url_for("confirmacao", nome=nome, tratamento=tratamento, data=data_str, horario=horario_str))
        except Exception as e:
            flash(f"❌ Ocorreu um erro ao realizar o agendamento: {e}", "danger")
            return redirect(url_for('agendamento'))
        finally:
            cursor.close()
            conn.close()

    return render_template("agendamento.html")

@app.route("/confirmacao")
def confirmacao():
    data_formatada = ""
    try:
        data_str = request.args.get('data')
        data_formatada = datetime.datetime.strptime(data_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        data_formatada = "Data inválida"

    return render_template("confirmacao.html", nome=request.args.get('nome'), tratamento=request.args.get('tratamento'), data=data_formatada, horario=request.args.get('horario'))

@app.route("/contato")
def contato():
    return render_template("contato.html")

# --- ROTAS DE ADMIN (PROTEGIDAS) ---

@app.route("/admin/agendamentos")
@login_required
def listar_agendamentos():
    conn = get_db_connection()
    if conn is None: return "Erro de conexão com o banco de dados.", 500
        
    cursor = conn.cursor(cursor_factory=RealDictCursor) # ### CORRIGIDO ###
    # ### CORRIGIDO: trocado DATE_FORMAT por TO_CHAR para PostgreSQL ###
    cursor.execute("""
        SELECT id, nome, email, telefone, tratamento, parte_corpo, 
               TO_CHAR(data, 'DD/MM/YYYY') as data, horario, criado_em 
        FROM agendamentos 
        ORDER BY agendamentos.data DESC, agendamentos.horario ASC
    """)
    agendamentos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin.html", agendamentos=agendamentos)

@app.route("/admin/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def editar_agendamento(id):
    conn = get_db_connection()
    if conn is None:
        flash("❌ Erro de conexão com o banco de dados.", "danger")
        return redirect(url_for('listar_agendamentos'))
    
    cursor = conn.cursor(cursor_factory=RealDictCursor) # ### CORRIGIDO ###

    if request.method == 'POST':
        nome, email, telefone = request.form.get("nome"), request.form.get("email"), request.form.get("telefone")
        tratamento, data_str, horario_str = request.form.get("tratamento"), request.form.get("data"), request.form.get("horario")
        
        sql = "UPDATE agendamentos SET nome=%s, email=%s, telefone=%s, tratamento=%s, data=%s, horario=%s WHERE id=%s"
        values = (nome, email, telefone, tratamento, data_str, horario_str, id)
        cursor.execute(sql, values)
        conn.commit()
        
        flash("✅ Agendamento atualizado com sucesso!", "success")
        return redirect(url_for('listar_agendamentos'))

    cursor.execute("SELECT * FROM agendamentos WHERE id = %s", (id,))
    agendamento = cursor.fetchone()

    if not agendamento:
        flash("❌ Agendamento não encontrado.", "danger")
        return redirect(url_for('listar_agendamentos'))
    
    return render_template("edit_agendamento.html", agendamento=agendamento)

@app.route("/admin/delete/<int:id>", methods=['POST'])
@login_required
def excluir_agendamento(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agendamentos WHERE id = %s", (id,))
    conn.commit()
    flash("🗑️ Agendamento excluído com sucesso.", "info")
    return redirect(url_for('listar_agendamentos'))

@app.route('/admin/usuarios')
@login_required
def manage_users():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor) # ### CORRIGIDO ###
    cursor.execute("SELECT * FROM usuarios WHERE is_active = FALSE")
    pending_users = cursor.fetchall()
    cursor.execute("SELECT * FROM usuarios WHERE is_active = TRUE")
    active_users = cursor.fetchall()
    conn.close()
    return render_template('admin_usuarios.html', pending_users=pending_users, active_users=active_users)

@app.route('/admin/approve_user/<int:id>', methods=['POST'])
@login_required
def approve_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET is_active = TRUE WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash('Usuário aprovado com sucesso!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/delete_user/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if id == session.get('user_id'):
        flash('Você não pode excluir a si mesmo.', 'danger')
        return redirect(url_for('manage_users'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash('Usuário excluído com sucesso.', 'info')
    return redirect(url_for('manage_users'))

if __name__ == "__main__":
    app.run(debug=True)