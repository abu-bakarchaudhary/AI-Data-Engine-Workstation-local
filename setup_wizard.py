import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import pyodbc
import socket

CONFIG_FILE = "db_config.json"
BG_MAIN = "#F8FAFC"          
BG_CARD = "#FFFFFF"          
COLOR_TEXT_MAIN = "#0F172A"  
COLOR_TEXT_MUTED = "#64748B" 
COLOR_BRAND = "#6366F1"      
COLOR_BORDER = "#E2E8F0"     

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def get_available_drivers():
    try:
        all_drivers = pyodbc.drivers()
        sql_drivers = [d for d in all_drivers if "SQL Server" in d]
        return sql_drivers if sql_drivers else all_drivers
    except Exception: 
        return ["{ODBC Driver 17 for SQL Server}"]

def scan_server_databases(driver, server, auth_type, username, password):
    conn_str = f"Driver={driver};Server={server};Database=master;"
    if auth_type == "Windows": 
        conn_str += "Trusted_Connection=yes;"
    else: 
        conn_str += f"UID={username};PWD={password};"
    
    conn = pyodbc.connect(conn_str, timeout=3)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.databases WHERE name NOT IN ('master','tempdb','model','msdb') AND HAS_DBACCESS(name)=1 ORDER BY name;")
    databases = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return databases

def draw_rounded_base(canvas, x1, y1, x2, y2, r, color):
    canvas.create_oval(x1, y1, x1+2*r, y1+2*r, fill=color, outline=color)
    canvas.create_oval(x2-2*r, y1, x2, y1+2*r, fill=color, outline=color)
    canvas.create_oval(x1, y2-2*r, x1+2*r, y2, fill=color, outline=color)
    canvas.create_oval(x2-2*r, y2-2*r, x2, y2, fill=color, outline=color)
    canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=color, outline=color)
    canvas.create_rectangle(x1, y1+r, x2, y2-r, fill=color, outline=color)

class SetupWizard:
    def __init__(self, on_success_callback):
        self.on_success = on_success_callback
        self.window = tk.Tk()
        self.window.title("Unified Engine Config Wizard")
        self.window.geometry("540x630")
        self.window.configure(bg=BG_MAIN)
        self.window.resizable(False, False)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=BG_MAIN, foreground=COLOR_TEXT_MAIN)
        
        tk.Label(self.window, text="⚙ INITIALIZE DATA MANAGEMENT PLATFORM", font=("Segoe UI", 12, "bold"), fg=COLOR_BRAND, bg=BG_MAIN).pack(pady=(25, 15))
        self.build_ui()
        
    def build_ui(self):
        frame_block1 = tk.Frame(self.window, bg=BG_MAIN, padx=30)
        frame_block1.pack(fill="x")
        
        c1 = tk.Canvas(frame_block1, height=270, bg=BG_MAIN, highlightthickness=0)
        c1.pack(fill="x", expand=True)
        self.window.update()
        c1_w = c1.winfo_width()
        draw_rounded_base(c1, 2, 2, c1_w-2, 265, 12, BG_CARD)
        c1.create_text(20, 22, text="1. Target Database Infrastructure Config", font=("Segoe UI", 10, "bold"), fill=COLOR_BRAND, anchor="w")
        
        c1.create_text(20, 55, text="ODBC Driver:", font=("Segoe UI", 10), fill=COLOR_TEXT_MAIN, anchor="w")
        self.combo_driver = ttk.Combobox(self.window, values=get_available_drivers(), font=("Segoe UI", 10))
        c1.create_window(c1_w-20, 55, window=self.combo_driver, width=240, height=28, anchor="e")
        drivers = get_available_drivers()
        best_match = next((d for d in drivers if "Driver 17" in d or "Driver 18" in d), drivers[0] if drivers else "")
        self.combo_driver.set(best_match)
        
        c1.create_text(20, 95, text="Instance Path:", font=("Segoe UI", 10), fill=COLOR_TEXT_MAIN, anchor="w")
        try:
            pc_name = socket.gethostname()
            srv_opts = ["localhost", "(local)", ".\\SQLEXPRESS", pc_name]
        except Exception:
            srv_opts = ["localhost", "(local)"]
        self.combo_server = ttk.Combobox(self.window, values=srv_opts, font=("Segoe UI", 10))
        self.combo_server.set("localhost")
        c1.create_window(c1_w-20, 95, window=self.combo_server, width=240, height=28, anchor="e")
        
        self.auth_var = tk.StringVar(value="Windows")
        c1.create_text(20, 135, text="Auth Framework:", font=("Segoe UI", 10), fill=COLOR_TEXT_MAIN, anchor="w")
        rad_w = ttk.Radiobutton(self.window, text="Windows Trusted", variable=self.auth_var, value="Windows", command=self.toggle_fields)
        rad_s = ttk.Radiobutton(self.window, text="SQL Engine Login", variable=self.auth_var, value="SQL", command=self.toggle_fields)
        c1.create_window(c1_w-260, 135, window=rad_w, anchor="w")
        c1.create_window(c1_w-140, 135, window=rad_s, anchor="w")
        
        c1.create_text(20, 175, text="Username:", font=("Segoe UI", 10), fill=COLOR_TEXT_MUTED, anchor="w")
        self.ent_u = tk.Entry(self.window, font=("Segoe UI", 10), state="disabled", bg="#E2E8F0", fg=COLOR_TEXT_MAIN, relief="flat", bd=0, highlightthickness=1, highlightbackground=COLOR_BORDER)
        c1.create_window(c1_w-20, 175, window=self.ent_u, width=240, height=26, anchor="e")
        
        c1.create_text(20, 215, text="Password:", font=("Segoe UI", 10), fill=COLOR_TEXT_MUTED, anchor="w")
        self.ent_p = tk.Entry(self.window, font=("Segoe UI", 10), show="*", state="disabled", bg="#E2E8F0", fg=COLOR_TEXT_MAIN, relief="flat", bd=0, highlightthickness=1, highlightbackground=COLOR_BORDER)
        c1.create_window(c1_w-20, 215, window=self.ent_p, width=240, height=26, anchor="e")

        frame_discovery = tk.Frame(self.window, bg=BG_MAIN, padx=30)
        frame_discovery.pack(fill="x", pady=10)
        c_disc = tk.Canvas(frame_discovery, height=110, bg=BG_MAIN, highlightthickness=0)
        c_disc.pack(fill="x", expand=True)
        draw_rounded_base(c_disc, 2, 2, c1_w-2, 105, 12, BG_CARD)
        c_disc.create_text(20, 30, text="Active Target Catalog:", font=("Segoe UI", 10, "bold"), fill=COLOR_TEXT_MAIN, anchor="w")
        
        self.combo_db = ttk.Combobox(self.window, state="readonly", font=("Segoe UI", 10))
        c_disc.create_window(c1_w-20, 30, window=self.combo_db, width=240, height=28, anchor="e")
        
        btn_disc = tk.Button(self.window, text="⎔ DISCOVER INSTANCE CATALOGS", command=self.scan_dbs, font=("Segoe UI", 9, "bold"), fg=BG_CARD, bg="#64748B", relief="flat", bd=0, cursor="hand2")
        c_disc.create_window(20, 72, window=btn_disc, width=c1_w-40, height=34, anchor="w")

        frame_block2 = tk.Frame(self.window, bg=BG_MAIN, padx=30)
        frame_block2.pack(fill="x", pady=(5, 10))
        c2 = tk.Canvas(frame_block2, height=90, bg=BG_MAIN, highlightthickness=0)
        c2.pack(fill="x", expand=True)
        draw_rounded_base(c2, 2, 2, c1_w-2, 85, 12, BG_CARD)
        c2.create_text(20, 24, text="2. Local Offline Engine Credentials Token", font=("Segoe UI", 10, "bold"), fill=COLOR_BRAND, anchor="w")
        c2.create_text(20, 54, text="Offline API Dummy Key:", font=("Segoe UI", 10), fill=COLOR_TEXT_MAIN, anchor="w")
        
        self.ent_key = tk.Entry(self.window, font=("Segoe UI", 10), bg=BG_MAIN, fg=COLOR_TEXT_MAIN, relief="flat", bd=0, highlightthickness=1, highlightbackground=COLOR_BORDER)
        c2.create_window(c1_w-20, 54, window=self.ent_key, width=240, height=26, anchor="e")
        self.ent_key.insert(0, "local-machine-token")

        btn_run = tk.Button(self.window, text="🚀 INITIALIZE OFFLINE WORKSTATION", command=self.save_and_continue, font=("Segoe UI", 10, "bold"), fg=BG_CARD, bg=COLOR_BRAND, relief="flat", bd=0, cursor="hand2")
        btn_run.pack(side="bottom", fill="x", padx=30, pady=20)
        
    def toggle_fields(self):
        st = "normal" if self.auth_var.get() == "SQL" else "disabled"
        self.ent_u.config(state=st, bg=BG_MAIN if st=="normal" else "#E2E8F0")
        self.ent_p.config(state=st, bg=BG_MAIN if st=="normal" else "#E2E8F0")
        
    def scan_dbs(self):
        try:
            discovered = scan_server_databases(self.combo_driver.get().strip(), self.combo_server.get().strip(), self.auth_var.get(), self.ent_u.get().strip(), self.ent_p.get().strip())
            if discovered:
                self.combo_db["values"] = discovered
                self.combo_db.set(discovered[0])
                messagebox.showinfo("Scanner Success", f"Found ({len(discovered)}) database configurations natively!")
        except Exception as e:
            messagebox.showerror("Discovery Failure", f"Failed to reach server: {e}")
            
    def save_and_continue(self):
        if not self.combo_db.get():
            messagebox.showwarning("Form Error", "Please provide a valid database destination coordinate.")
            return
        
        config = {
            "driver": self.combo_driver.get().strip(), "server": self.combo_server.get().strip(), "database": self.combo_db.get(),
            "auth_type": self.auth_var.get(), "username": self.ent_u.get().strip(), "password": self.ent_p.get().strip(),
            "api_key": self.ent_key.get().strip(), "sql_dialect": "Microsoft SQL Server"
        }
        save_config(config)
        self.window.destroy()
        self.on_success()

    def run(self):
        self.window.mainloop()