import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from datetime import datetime

class TigerBankGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🐯 Tiger Bank")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        self.current_user = None
        self.init_database()
        self.setup_gui()
    
    def hash_password(self, password):
        """Hash simples usando SHA256 - não precisa de bcrypt"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def check_password(self, password, hashed):
        """Verifica senha com hash SHA256"""
        return self.hash_password(password) == hashed
    
    def init_database(self):
        conn = sqlite3.connect('tiger_bank.db')
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de contas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tipo TEXT DEFAULT 'corrente',
                saldo REAL DEFAULT 1000.00,
                numero TEXT UNIQUE NOT NULL,
                agencia TEXT DEFAULT '0001',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabela de transações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                valor REAL NOT NULL,
                descricao TEXT NOT NULL,
                categoria TEXT DEFAULT 'outros',
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                destinatario TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Banco de dados inicializado!")
    
    def setup_gui(self):
        # Configurar estilo
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        
        self.show_login_screen()
    
    def show_login_screen(self):
        self.clear_screen()
        
        # Container principal
        main_container = ttk.Frame(self.main_frame)
        main_container.pack(expand=True, pady=50)
        
        # Logo e título
        title_frame = ttk.Frame(main_container)
        title_frame.pack(pady=30)
        
        ttk.Label(title_frame, text="🐯", font=('Arial', 40)).pack()
        ttk.Label(title_frame, text="Tiger Bank", style='Title.TLabel').pack()
        ttk.Label(title_frame, text="Sua vida financeira simplificada").pack(pady=5)
        
        # Formulário de login
        form_frame = ttk.LabelFrame(main_container, text=" Login ", padding=20)
        form_frame.pack(pady=20, padx=50, fill='x')
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=0, column=0, sticky='w', pady=10)
        self.email_entry = ttk.Entry(form_frame, width=30, font=('Arial', 11))
        self.email_entry.grid(row=0, column=1, pady=10, padx=10)
        self.email_entry.focus()
        
        # Senha
        ttk.Label(form_frame, text="Senha:").grid(row=1, column=0, sticky='w', pady=10)
        self.senha_entry = ttk.Entry(form_frame, width=30, show='•', font=('Arial', 11))
        self.senha_entry.grid(row=1, column=1, pady=10, padx=10)
        self.senha_entry.bind('<Return>', lambda e: self.login())
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="🚀 Entrar", 
                  command=self.login, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📝 Cadastrar", 
                  command=self.show_register_screen, width=15).pack(side=tk.LEFT, padx=5)
        
        # Dados de teste
        test_frame = ttk.Frame(main_container)
        test_frame.pack(pady=10)
        ttk.Label(test_frame, text="💡 Teste: admin@tiger.com / senha123", 
                 font=('Arial', 9), foreground='gray').pack()
    
    def show_register_screen(self):
        self.clear_screen()
        
        main_container = ttk.Frame(self.main_frame)
        main_container.pack(expand=True, pady=30)
        
        ttk.Label(main_container, text="📝 Criar Nova Conta", style='Title.TLabel').pack(pady=20)
        
        form_frame = ttk.LabelFrame(main_container, text=" Dados Pessoais ", padding=20)
        form_frame.pack(pady=10, padx=50, fill='x')
        
        # Campos do formulário
        fields = [
            ("Nome completo:", "nome_entry"),
            ("CPF:", "cpf_entry"),
            ("Email:", "email_reg_entry"),
            ("Senha:", "senha_reg_entry"),
            ("Confirmar senha:", "senha_conf_entry")
        ]
        
        self.entries = {}
        for i, (label, name) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky='w', pady=8)
            entry = ttk.Entry(form_frame, width=30, font=('Arial', 11))
            
            if 'senha' in name:
                entry.configure(show='•')
            
            entry.grid(row=i, column=1, pady=8, padx=10)
            self.entries[name] = entry
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="✅ Cadastrar", 
                  command=self.register_user, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="↩️ Voltar", 
                  command=self.show_login_screen, width=15).pack(side=tk.LEFT, padx=5)
    
    def show_dashboard(self):
        self.clear_screen()
        
        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=10, padx=20)
        
        ttk.Label(header_frame, text=f"👋 Bem-vindo, {self.current_user['nome']}!", 
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="🚪 Sair", 
                  command=self.logout).pack(side=tk.RIGHT)
        
        # Saldo
        saldo = self.get_saldo()
        saldo_frame = ttk.LabelFrame(self.main_frame, text=" Saldo Disponível ", padding=15)
        saldo_frame.pack(fill=tk.X, pady=15, padx=20)
        
        ttk.Label(saldo_frame, text=f"R$ {saldo:,.2f}", 
                 font=('Arial', 24, 'bold'), 
                 foreground='#2ecc71').pack()
        
        # Menu de ações
        actions_frame = ttk.LabelFrame(self.main_frame, text=" Ações Rápidas ", padding=15)
        actions_frame.pack(fill=tk.X, pady=10, padx=20)
        
        actions = [
            ("📊 Extrato", self.show_extrato),
            ("💸 Fazer PIX", self.show_pix),
            ("💰 Depositar", self.show_deposito),
            ("💳 Sacar", self.show_saque),
            ("📈 Relatórios", self.show_relatorios)
        ]
        
        for text, command in actions:
            ttk.Button(actions_frame, text=text, 
                      command=command, width=15).pack(side=tk.LEFT, padx=5)
        
        # Últimas transações
        self.show_ultimas_transacoes()
    
    def show_ultimas_transacoes(self):
        trans_frame = ttk.LabelFrame(self.main_frame, text=" Últimas Transações ", padding=10)
        trans_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        # Treeview (tabela)
        columns = ('Data', 'Tipo', 'Valor', 'Descrição', 'Categoria')
        tree = ttk.Treeview(trans_frame, columns=columns, show='headings', height=8)
        
        # Configurar colunas
        tree.heading('Data', text='Data')
        tree.heading('Tipo', text='Tipo')
        tree.heading('Valor', text='Valor (R$)')
        tree.heading('Descrição', text='Descrição')
        tree.heading('Categoria', text='Categoria')
        
        tree.column('Data', width=120)
        tree.column('Tipo', width=80)
        tree.column('Valor', width=100)
        tree.column('Descrição', width=200)
        tree.column('Categoria', width=100)
        
        # Buscar transações
        conn = sqlite3.connect('tiger_bank.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT strftime('%d/%m/%Y %H:%M', data), tipo, valor, descricao, categoria 
            FROM transactions WHERE user_id = ? ORDER BY data DESC LIMIT 15
        ''', (self.current_user['id'],))
        
        for trans in cursor.fetchall():
            tree.insert('', tk.END, values=trans)
        
        conn.close()
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(trans_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def show_pix(self):
        pix_window = tk.Toplevel(self.root)
        pix_window.title("💸 Transferência PIX")
        pix_window.geometry("400x350")
        pix_window.configure(bg='#f0f0f0')
        pix_window.transient(self.root)
        pix_window.grab_set()
        
        # Centralizar janela
        pix_window.update_idletasks()
        x = (pix_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (pix_window.winfo_screenheight() // 2) - (350 // 2)
        pix_window.geometry(f"400x350+{x}+{y}")
        
        ttk.Label(pix_window, text="Transferência via PIX", 
                 style='Title.TLabel').pack(pady=20)
        
        form_frame = ttk.Frame(pix_window, padding=20)
        form_frame.pack(fill='both', expand=True)
        
        # Campos do PIX
        fields = [
            ("Chave PIX (CPF, email ou telefone):", "chave_pix"),
            ("Valor R$:", "valor_pix"),
            ("Descrição:", "desc_pix")
        ]
        
        entries = {}
        for i, (label, name) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky='w', pady=10)
            entry = ttk.Entry(form_frame, width=30, font=('Arial', 11))
            entry.grid(row=i, column=1, pady=10, padx=10)
            entries[name] = entry
        
        # Mostrar saldo atual
        saldo = self.get_saldo()
        ttk.Label(form_frame, text=f"Saldo disponível: R$ {saldo:,.2f}",
                 foreground='green').grid(row=3, column=0, columnspan=2, pady=10)
        
        def realizar_pix():
            try:
                chave = entries['chave_pix'].get()
                valor = float(entries['valor_pix'].get())
                descricao = entries['desc_pix'].get()
                
                if not chave or valor <= 0:
                    messagebox.showerror("Erro", "Preencha todos os campos corretamente!")
                    return
                
                if valor > saldo:
                    messagebox.showerror("Erro", "Saldo insuficiente!")
                    return
                
                # Realizar PIX
                conn = sqlite3.connect('tiger_bank.db')
                cursor = conn.cursor()
                
                # Atualizar saldo
                cursor.execute(
                    'UPDATE accounts SET saldo = saldo - ? WHERE user_id = ?',
                    (valor, self.current_user['id'])
                )
                
                # Registrar transação
                cursor.execute('''
                    INSERT INTO transactions (user_id, tipo, valor, descricao, categoria, destinatario)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (self.current_user['id'], 'saida', valor, descricao, 'transferencia', chave))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Sucesso", f"PIX de R$ {valor:,.2f} realizado!\nPara: {chave}")
                pix_window.destroy()
                self.show_dashboard()
                
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao realizar PIX: {e}")
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="✅ Transferir", 
                  command=realizar_pix, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Cancelar", 
                  command=pix_window.destroy, width=15).pack(side=tk.LEFT, padx=5)
    
    def show_extrato(self):
        # Implementar tela de extrato completo
        messagebox.showinfo("Em Desenvolvimento", "Extrato completo em desenvolvimento!")
    
    def show_deposito(self):
        # Implementar depósito
        messagebox.showinfo("Em Desenvolvimento", "Depósito em desenvolvimento!")
    
    def show_saque(self):
        # Implementar saque
        messagebox.showinfo("Em Desenvolvimento", "Saque em desenvolvimento!")
    
    def show_relatorios(self):
        # Implementar relatórios
        messagebox.showinfo("Em Desenvolvimento", "Relatórios em desenvolvimento!")
    
    def clear_screen(self):
        """Limpa a tela atual"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def login(self):
        email = self.email_entry.get()
        senha = self.senha_entry.get()
        
        if not email or not senha:
            messagebox.showerror("Erro", "Preencha email e senha!")
            return
        
        conn = sqlite3.connect('tiger_bank.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user and self.check_password(senha, user[4]):
            self.current_user = {
                'id': user[0],
                'nome': user[1],
                'email': user[3]
            }
            self.show_dashboard()
        else:
            messagebox.showerror("Erro", "Email ou senha incorretos!")
        
        conn.close()
    
    def register_user(self):
        nome = self.entries['nome_entry'].get()
        cpf = self.entries['cpf_entry'].get()
        email = self.entries['email_reg_entry'].get()
        senha = self.entries['senha_reg_entry'].get()
        senha_conf = self.entries['senha_conf_entry'].get()
        
        # Validações
        if not all([nome, cpf, email, senha, senha_conf]):
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        if senha != senha_conf:
            messagebox.showerror("Erro", "Senhas não coincidem!")
            return
        
        if len(senha) < 6:
            messagebox.showerror("Erro", "Senha deve ter pelo menos 6 caracteres!")
            return
        
        try:
            conn = sqlite3.connect('tiger_bank.db')
            cursor = conn.cursor()
            
            senha_hash = self.hash_password(senha)
            
            cursor.execute(
                'INSERT INTO users (nome, cpf, email, senha_hash) VALUES (?, ?, ?, ?)',
                (nome, cpf, email, senha_hash)
            )
            
            user_id = cursor.lastrowid
            numero_conta = f"{user_id:08d}"
            
            cursor.execute(
                'INSERT INTO accounts (user_id, numero, saldo) VALUES (?, ?, ?)',
                (user_id, numero_conta, 1000.00)
            )
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Sucesso", 
                                f"✅ Cadastro realizado!\n\n"
                                f"📧 Email: {email}\n"
                                f"🏦 Agência: 0001\n"
                                f"📊 Conta: {numero_conta}\n"
                            f"💰 Saldo inicial: R$ 1.000,00")
            
            self.show_login_screen()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Email ou CPF já cadastrado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no cadastro: {e}")
    
    def logout(self):
        self.current_user = None
        self.show_login_screen()
    
    def get_saldo(self):
        if not self.current_user:
            return 0.0
        
        conn = sqlite3.connect('tiger_bank.db')
        cursor = conn.cursor()
        cursor.execute('SELECT saldo FROM accounts WHERE user_id = ?', (self.current_user['id'],))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0.0

if __name__ == "__main__":
    root = tk.Tk()
    app = TigerBankGUI(root)
    root.mainloop()