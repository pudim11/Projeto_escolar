import sqlite3
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from datetime import datetime
import logging

# Configuração básica do logger
logging.basicConfig(filename='error.log', level=logging.ERROR)

# Importe o objeto app do módulo Sistema
from Sistema import app

# Defina o caminho do banco de dados
DATABASE = 'database.db'

# Função para obter conexão com o banco de dados
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Função para inicializar o banco de dados
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
    table_exists = cursor.fetchone()

    if not table_exists:
        with open('schema.sql') as f:
            conn.executescript(f.read())
        print("Banco de dados inicializado com sucesso.")
    else:
        print("O banco de dados já está inicializado.")

    conn.close()

# Inicialização do banco de dados
init_db()

# Pagina Inicial > Portais
@app.route('/')
def portais():
    return render_template('portais.html')

# Rota para o formulário de login do aluno
@app.route('/portal_aluno')
def portal_aluno():
    return render_template('portal_aluno.html')

# Rota para processar os dados do formulário de login do aluno
@app.route('/home_aluno', methods=['POST', 'GET'])
def home_aluno():
    conn = get_db_connection()
    if request.method == 'POST':
        matricula = request.form['matricula']
        password = request.form['password']
    else:
        matricula = session.get('matricula')
        password = session.get('password')

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE matricula = ? AND senha = ?", (matricula, password))
    student = cursor.fetchone()

    if student:
        session['matricula'] = matricula
        session['password'] = password
        idres = student[0]
        return redirect(url_for('mostrar_boletim'))  # Corrigindo o redirecionamento para a rota correta
    else:
        flash('Usuário não cadastrado!', 'error')
        return redirect(url_for('portal_aluno'))

# Rota para exibir o boletim
@app.route('/boletim')
def mostrar_boletim():
    if 'matricula' not in session:
        return redirect(url_for('portal_aluno'))
    
    matricula = session['matricula']
    student_name, boletim_data = get_boletim_por_matricula(matricula)
    
    if not boletim_data:
        flash('Boletim não encontrado.', 'error')
        return redirect(url_for('portal_aluno'))  # Redirecionar para uma página adequada
    
    return render_template('boletim.html', boletim=boletim_data, student_name=student_name, matricula=matricula)

# Rota para o formulário de login do professor
@app.route('/portal_professor')
def portal_professor():
    return render_template('portal_professor.html')

# Rota para processar os dados do formulário de login do professor
@app.route('/home_professor', methods=['POST', 'GET'])
def home_professor():
    conn = get_db_connection()
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
    else:
        user = session.get('user')
        password = session.get('password')

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user = ? AND password = ?", (user, password))
    prof = cursor.fetchone()

    if prof:
        session['user'] = user
        session['password'] = password
        idres = prof[0]
        return render_template('home_professor.html', user=user, password=password, idres=idres)
    else:
        return "Usuário não cadastrado!"

# Função para obter boletim por matricula
def get_boletim_por_matricula(matricula):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subjects.nome AS materia, 
               grades.nota1, grades.nota2, grades.nota3, grades.nota4
        FROM students
        LEFT JOIN grades ON students.id = grades.student_id
        LEFT JOIN subjects ON grades.subject_id = subjects.id
        WHERE students.matricula = ?
    """, (matricula,))

    boletim_data = cursor.fetchall()
    
    # Buscar o nome do aluno
    cursor.execute("SELECT nome FROM students WHERE matricula = ?", (matricula,))
    student_name = cursor.fetchone()['nome']
    
    conn.close()

    return student_name, boletim_data

# Rota para a página de chamada/frequência
@app.route('/registrar_presenca', methods=["GET", "POST"])
def registrar_presenca():
    if request.method == 'POST':
        turma_id = request.form.get('turma')
        if turma_id:
            conn = get_db_connection()
            cursor = conn.execute('SELECT * FROM students WHERE turma_id = ?', (turma_id,))
            table_students = cursor.fetchall()
            size_table_students = len(table_students)
            data = datetime.now().strftime("%d/%m/%Y")
            conn.close()  # Feche a conexão após obter os dados

            return render_template('registrar_presenca.html', turmas=get_classes(), table_students=table_students,
                                   size_table_students=size_table_students, data=data, turma_id=turma_id)
        else:
            flash('Selecione uma turma.', 'error')
            return redirect(url_for('registrar_presenca'))
    else:
        turmas = get_classes()
        return render_template('registrar_presenca.html', turmas=turmas)

# Rota para lançamento de notas
@app.route('/classes_lancamento', methods=['GET', 'POST'])
def classes_lancamento():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        if 'nota1' in request.form:
            # Salvando as notas
            matricula = request.form['matricula']
            materia_id = request.form['materia_id']
            nota1 = request.form['nota1']
            nota2 = request.form['nota2']
            nota3 = request.form['nota3']
            nota4 = request.form['nota4']
            
            student = cursor.execute("SELECT id FROM students WHERE matricula = ?", (matricula,)).fetchone()
            if student:
                student_id = student['id']
                
                # Verificar se o registro de notas já existe
                cursor.execute("""
                    SELECT * FROM grades
                    WHERE student_id = ? AND subject_id = ?
                """, (student_id, materia_id))
                grades_exist = cursor.fetchone()
                
                if grades_exist:
                    # Atualizar as notas
                    cursor.execute("""
                        UPDATE grades
                        SET nota1 = ?, nota2 = ?, nota3 = ?, nota4 = ?
                        WHERE student_id = ? AND subject_id = ?
                    """, (nota1, nota2, nota3, nota4, student_id, materia_id))
                else:
                    # Inserir novas notas
                    cursor.execute("""
                        INSERT INTO grades (student_id, subject_id, nota1, nota2, nota3, nota4)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (student_id, materia_id, nota1, nota2, nota3, nota4))
                
                flash('Notas atualizadas com sucesso!', 'success')
                conn.commit()
            else:
                flash('Estudante não encontrado.', 'error')
                logging.error(f'Estudante não encontrado para matrícula {matricula}')
            
            return redirect(url_for('classes_lancamento'))

        else:
            # Buscando as notas
            try:
                matricula = request.form['matricula']
                materia_id = request.form['materia_id']
                
                student = cursor.execute("SELECT id FROM students WHERE matricula = ?", (matricula,)).fetchone()
                if student:
                    student_id = student['id']
                    boletim = cursor.execute("""
                        SELECT subjects.nome AS materia, 
                               grades.nota1, grades.nota2, grades.nota3, grades.nota4
                        FROM grades
                        JOIN subjects ON grades.subject_id = subjects.id
                        WHERE grades.student_id = ? AND grades.subject_id = ?
                    """, (student_id, materia_id)).fetchone()

                    if not boletim:
                        boletim = {'nota1': None, 'nota2': None, 'nota3': None, 'nota4': None}
                    
                    return render_template('lancamento.html', boletim=boletim, materias=get_subjects(), matricula=matricula, materia_id=materia_id)
                else:
                    flash('Estudante não encontrado.', 'error')
                    logging.error(f'Estudante não encontrado para matrícula {matricula}')
                    return redirect(url_for('classes_lancamento'))
            except Exception as e:
                flash(f'Ocorreu um erro: {e}', 'error')
                logging.error(f'Ocorreu um erro ao buscar notas: {str(e)}')
                return redirect(url_for('classes_lancamento'))

    return render_template('lancamento.html', materias=get_subjects(), notas=None)

# Função para buscar as matérias
def get_subjects():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subjects')
    subjects = cursor.fetchall()
    conn.close()
    return subjects

def get_student_name(matricula):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM students WHERE matricula = ?", (matricula,))
    student = cursor.fetchone()
    conn.close()
    return student['nome'] if student else None

@app.route('/save_presenca', methods=['POST'])
def save_presenca():
    conn = get_db_connection()
    cursor = conn.cursor()

    turma_id = request.form['turma_id']
    chamada = request.form.getlist('presenca')
    data = datetime.now().strftime("%d/%m/%Y")

    for student_id in chamada:
        cursor.execute("""
            INSERT INTO presenca (student_id, turma_id, data, presente)
            VALUES (?, ?, ?, 1)
        """, (student_id, turma_id, data))

    conn.commit()
    conn.close()
    
    return redirect(url_for('registrar_presenca'))

# Função para obter as turmas
def get_classes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM turmas")
    classes = cursor.fetchall()
    conn.close()
    return classes
