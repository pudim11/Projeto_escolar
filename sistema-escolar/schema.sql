-- Tabela de alunos
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    matricula TEXT NOT NULL,
    senha TEXT NOT NULL,
    turma TEXT,
    turma_id INTEGER
);

-- Tabela de professores
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    password TEXT NOT NULL
);

-- Tabela de disciplinas
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);

-- Tabela de notas
CREATE TABLE grades (
    student_id INTEGER,
    subject_id INTEGER,
    nota1 TEXT DEFAULT '-',
    nota2 TEXT DEFAULT '-',
    nota3 TEXT DEFAULT '-',
    nota4 TEXT DEFAULT '-',
    PRIMARY KEY (student_id, subject_id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);

-- Tabela de presença
CREATE TABLE presenca (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    turma_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    status TEXT NOT NULL,  -- Adicionando o campo 'status'
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (turma_id) REFERENCES classes (id)
);

CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);