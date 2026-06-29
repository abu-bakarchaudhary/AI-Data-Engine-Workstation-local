import tkinter as tk
from tkinter import ttk, messagebox
import setup_wizard
import intent_enhancer
import sql_compiler
import schema_manager
import linter_agent

BG_MAIN = "#F8FAFC"          
BG_CARD = "#FFFFFF"          
COLOR_TEXT_MAIN = "#0F172A"  
COLOR_TEXT_MUTED = "#64748B" 
COLOR_BRAND = "#6366F1"      
COLOR_BRAND_HOVER = "#4F46E5"
COLOR_BORDER = "#E2E8F0"     
COLOR_CONSOLE_BG = "#0F172A" 
COLOR_ACCENT_GREEN = "#10B981" 

FONT_UI_REGULAR = "Segoe UI"
FONT_UI_CODE = "Consolas"

class DataEngineWorkstation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Universal AI Data Engine Workstation")
        self.root.geometry("1150x780")
        self.root.configure(bg=BG_MAIN)
        
        self.active_config = setup_wizard.load_config()
        self.saved_dialect = self.active_config.get("sql_dialect", "Microsoft SQL Server") if self.active_config else "Microsoft SQL Server"
        
        self.apply_styles()
        self.build_ui()
        
    def apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=BG_MAIN, foreground=COLOR_TEXT_MAIN)
        style.configure("TFrame", background=BG_MAIN)
        style.configure("TCombobox", fieldbackground=BG_MAIN, background=BG_CARD, foreground=COLOR_TEXT_MAIN, arrowcolor=COLOR_BRAND, borderwidth=0)
        style.map("TCombobox", fieldbackground=[("readonly", BG_MAIN)], foreground=[("readonly", COLOR_TEXT_MAIN)])
        style.configure("Treeview", background=BG_CARD, fieldbackground=BG_CARD, foreground=COLOR_TEXT_MAIN, font=(FONT_UI_REGULAR, 10), rowheight=30, borderwidth=0)
        style.configure("Treeview.Heading", background=BG_MAIN, foreground=COLOR_TEXT_MAIN, font=(FONT_UI_REGULAR, 10, "bold"), borderwidth=1, relief="flat")
        style.map("Treeview", background=[("selected", COLOR_BRAND)], foreground=[("selected", BG_CARD)])

    def create_pill_btn(self, parent, text, cmd, accent=True):
        bg = COLOR_BRAND if accent else "#64748B"
        hov = COLOR_BRAND_HOVER if accent else "#475569"
        btn = tk.Button(parent, text=text, command=cmd, font=(FONT_UI_REGULAR, 10, "bold"), fg=BG_CARD, bg=bg, relief="flat", bd=0, cursor="hand2", padx=18, pady=7)
        btn.bind("<Enter>", lambda e: btn.config(bg=hov))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    def build_ui(self):
        frame_header = tk.Frame(self.root, bg=BG_MAIN, padx=30, pady=15)
        frame_header.pack(fill="x")
        tk.Label(frame_header, text="? OFFLINE LOCAL AI DATA WORKSTATION", font=(FONT_UI_REGULAR, 12, "bold"), fg=COLOR_TEXT_MAIN, bg=BG_MAIN).pack(side="left")
        
        frame_ctrls = tk.Frame(frame_header, bg=BG_MAIN)
        frame_ctrls.pack(side="right")
        tk.Label(frame_ctrls, text="SQL Dialect Target:", font=(FONT_UI_REGULAR, 9, "bold"), fg=COLOR_TEXT_MUTED, bg=BG_MAIN).pack(side="left", padx=5)
        
        dialects = ["Microsoft SQL Server", "MySQL", "PostgreSQL", "Oracle", "SQLite", "Custom / Unlisted..."]
        self.combo_dialect = ttk.Combobox(frame_ctrls, values=dialects, state="readonly", width=22, font=(FONT_UI_REGULAR, 9))
        self.combo_dialect.set(self.saved_dialect)
        self.combo_dialect.pack(side="left", padx=5)
        self.combo_dialect.bind("<<ComboboxSelected>>", self.handle_dialect_change)
        
        self.entry_custom_dialect = tk.Entry(frame_ctrls, font=(FONT_UI_REGULAR, 9), bg=BG_CARD, fg=COLOR_TEXT_MAIN, relief="flat", bd=1, highlightthickness=1, highlightbackground=COLOR_BORDER, highlightcolor=COLOR_BRAND)
        if self.saved_dialect == "Custom / Unlisted..." and self.active_config:
            self.entry_custom_dialect.insert(0, self.active_config.get("custom_dialect_name", ""))
            self.entry_custom_dialect.pack(side="left", padx=10, ipady=3)

        frame_input = tk.Frame(self.root, bg=BG_MAIN, padx=30, pady=5)
        frame_input.pack(fill="x")
        self.canvas_bg = tk.Canvas(frame_input, height=90, bg=BG_MAIN, highlightthickness=0)
        self.canvas_bg.pack(fill="x", expand=True)
        self.root.update()
        
        w_width = self.canvas_bg.winfo_width()
        setup_wizard.draw_rounded_base(self.canvas_bg, 2, 2, w_width-2, 85, 12, BG_CARD)
        self.canvas_bg.create_text(20, 24, text="Natural Language Context Request Input Channel", font=(FONT_UI_REGULAR, 10, "bold"), fill=COLOR_BRAND, anchor="w")
        
        self.entry_question = tk.Entry(frame_input, font=(FONT_UI_REGULAR, 11), bg=BG_MAIN, fg=COLOR_TEXT_MAIN, insertbackground=COLOR_TEXT_MAIN, relief="flat", bd=0, highlightthickness=1, highlightbackground=COLOR_BORDER, highlightcolor=COLOR_BRAND)
        self.canvas_bg.create_window(20, 52, window=self.entry_question, width=w_width-220, height=34, anchor="w")
        self.entry_question.bind("<Return>", lambda e: self.process_pipeline())
        
        btn_run = self.create_pill_btn(frame_input, "? EXECUTE PIPELINE", self.process_pipeline, True)
        self.canvas_bg.create_window(w_width-20, 52, window=btn_run, anchor="e")
        
        self.lbl_status = tk.Label(self.root, text="Agnostic semantic caching pipeline synchronized. Standing by...", font=(FONT_UI_REGULAR, 9, "italic"), fg=COLOR_TEXT_MUTED, bg=BG_MAIN)
        self.lbl_status.pack(anchor="w", padx=30, pady=2)

        frame_term = tk.Frame(self.root, bg=BG_MAIN, padx=30, pady=5)
        frame_term.pack(fill="x")
        tk.Label(frame_term, text="? Compiled SQL Translation Engine Output Verification Block View", font=(FONT_UI_REGULAR, 9, "bold"), fg=COLOR_TEXT_MUTED, bg=BG_MAIN).pack(anchor="w", pady=(5, 4))
        self.text_sql = tk.Text(frame_term, height=5, font=(FONT_UI_CODE, 10), bg=COLOR_CONSOLE_BG, fg=COLOR_BRAND, wrap="word", relief="flat", bd=0, padx=15, pady=12)
        self.text_sql.pack(fill="x")

        frame_grid = tk.Frame(self.root, bg=BG_MAIN, padx=30, pady=15)
        frame_grid.pack(fill="both", expand=True)
        sy = ttk.Scrollbar(frame_grid, orient="vertical")
        sx = ttk.Scrollbar(frame_grid, orient="horizontal")
        self.tree = ttk.Treeview(frame_grid, yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.config(command=self.tree.yview); sx.config(command=self.tree.xview)
        sy.pack(side="right", fill="y"); sx.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

    def handle_dialect_change(self, event):
        sel = self.combo_dialect.get()
        if sel == "Custom / Unlisted...":
            self.entry_custom_dialect.pack(side="left", padx=10, ipady=3)
        else:
            self.entry_custom_dialect.pack_forget()
        cfg = setup_wizard.load_config()
        if cfg:
            cfg["sql_dialect"] = sel
            cfg["custom_dialect_name"] = self.entry_custom_dialect.get().strip()
            setup_wizard.save_config(cfg)

    def get_dialect(self):
        sel = self.combo_dialect.get()
        return self.entry_custom_dialect.get().strip() if sel == "Custom / Unlisted..." else sel

    def process_pipeline(self):
        raw_prompt = self.entry_question.get().strip()
        if not raw_prompt: return
            
        try:
            self.lbl_status.config(text="? PASS 0: Compiling local index candidate options...", fg=COLOR_BRAND)
            self.root.update()
            
            enhanced_spec = intent_enhancer.enhance_user_prompt(raw_prompt)
            is_verified, approved_text = self.launch_gate_modal(raw_prompt, enhanced_spec)
            if not is_verified or not approved_text:
                self.lbl_status.config(text="? TRANSACTION HALTED: Request dropped.", fg=COLOR_TEXT_MUTED)
                return
                
            dialect = self.get_dialect()
            self.lbl_status.config(text=f"?? COMPILING: Generating secure {dialect} values...", fg=COLOR_BRAND)
            self.root.update()
            
            generated_sql = sql_compiler.translate_english_to_sql(approved_text, dialect)
            if not generated_sql:
                self.lbl_status.config(text="? GENERATOR ERROR: Mapping failed.", fg="#EF4444")
                return

            is_valid, lint_error = linter_agent.offline_syntax_check(generated_sql, dialect)
            if not is_valid:
                self.lbl_status.config(text="?? LINTER WARNING: Activating Agentic Auto-Heal Loop...", fg=COLOR_BRAND)
                self.root.update()
                generated_sql = linter_agent.execute_auto_heal_loop(approved_text, generated_sql, lint_error, dialect)

            self.text_sql.config(state="normal")
            self.text_sql.delete("1.0", tk.END)
            self.text_sql.insert("1.0", generated_sql)
            self.text_sql.config(state="disabled")
            
            try:
                columns, data = schema_manager.execute_raw_sql(generated_sql)
            except Exception as db_err:
                self.lbl_status.config(text="?? DB EXCEPTION: Re-triggering Auto-Heal Loop...", fg=COLOR_BRAND)
                self.root.update()
                healed_sql = linter_agent.execute_auto_heal_loop(approved_text, generated_sql, str(db_err), dialect)
                
                self.text_sql.config(state="normal")
                self.text_sql.delete("1.0", tk.END)
                self.text_sql.insert("1.0", healed_sql)
                self.text_sql.config(state="disabled")
                columns, data = schema_manager.execute_raw_sql(healed_sql)

            if columns and data is not None:
                for item in self.tree.get_children(): self.tree.delete(item)
                self.tree["columns"] = columns
                self.tree["show"] = "headings"
                for col in columns:
                    self.tree.heading(col, text=f"  {col}")
                    self.tree.column(col, width=150, anchor="w", stretch=False)
                for row in data: self.tree.insert("", "end", values=row)
                self.lbl_status.config(text=f"? VERIFIED SUCCESS: Pulled {len(data)} matrix row variants.", fg=COLOR_ACCENT_GREEN)
                
        except Exception as global_err:
            self.lbl_status.config(text="? COMPILER PIPELINE RUNTIME CRASH.", fg="#EF4444")
            messagebox.showerror("Pipeline Failure", f"Fatal engine exception handled:\n\n{global_err}")

    def launch_gate_modal(self, raw, enhanced):
        gate = tk.Toplevel(self.root)
        gate.title("Intent Clarification Workspace Gate")
        gate.geometry("950x520")
        gate.configure(bg=BG_MAIN)
        gate.transient(self.root)
        gate.grab_set()
        
        state = {"verified": False, "text": ""}
        tk.Label(gate, text="? INTENT CLARIFICATION ENGINE WORKSPACE", font=(FONT_UI_REGULAR, 12, "bold"), fg=COLOR_BRAND, bg=BG_MAIN).pack(anchor="w", padx=30, pady=(20, 5))
        
        frame_actions = tk.Frame(gate, bg=BG_MAIN, pady=15)
        frame_actions.pack(side="bottom", fill="x", padx=30)
        
        frame_cards = tk.Frame(gate, bg=BG_MAIN)
        frame_cards.pack(side="top", fill="both", expand=True, padx=30, pady=10)
        
        c_left = tk.Frame(frame_cards, bg=BG_CARD, bd=1, highlightbackground=COLOR_BORDER, highlightthickness=1)
        c_left.pack(side="left", fill="both", expand=True, padx=(0, 15))
        tk.Label(c_left, text="Your Original Raw Instruction:", font=(FONT_UI_REGULAR, 10, "bold"), fg=COLOR_TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=15, pady=10)
        tk.Label(c_left, text=raw, font=(FONT_UI_REGULAR, 11, "italic"), fg=COLOR_TEXT_MAIN, bg=BG_CARD, wrap=380, justify="left").pack(fill="both", expand=True, padx=15) # pyright: ignore[reportCallIssue]
        
        c_right = tk.Frame(frame_cards, bg=BG_CARD, bd=1, highlightbackground=COLOR_BRAND, highlightthickness=1)
        c_right.pack(side="right", fill="both", expand=True, padx=(15, 0))
        tk.Label(c_right, text="Optimized Analytical Specification Blueprint (Editable):", font=(FONT_UI_REGULAR, 10, "bold"), fg=COLOR_BRAND, bg=BG_CARD).pack(anchor="w", padx=15, pady=10)
        
        txt_editor = tk.Text(c_right, font=(FONT_UI_REGULAR, 11), bg=BG_MAIN, fg=COLOR_TEXT_MAIN, relief="flat", wrap="word", padx=10, pady=10)
        txt_editor.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        txt_editor.insert("1.0", enhanced)
        
        def approve():
            state["verified"] = True
            state["text"] = txt_editor.get("1.0", tk.END).strip()
            gate.destroy()
            
        def regenerate():
            current_raw = txt_editor.get("1.0", tk.END).strip() or raw
            self.lbl_status.config(text="? RE-COMPILING: Fetching updated semantic optimization...", fg=COLOR_BRAND)
            self.root.update()
            fresh_spec = intent_enhancer.enhance_user_prompt(current_raw)
            txt_editor.delete("1.0", tk.END)
            txt_editor.insert("1.0", fresh_spec)
            self.lbl_status.config(text="? Optimization refreshed.", fg=COLOR_TEXT_MUTED)

        self.create_pill_btn(frame_actions, "? CONFIRM & COMPILE CODE", approve, True).pack(side="right", padx=(15, 0))
        self.create_pill_btn(frame_actions, "?? REGENERATE SPEC", regenerate, False).pack(side="right", padx=(15, 0))
        self.create_pill_btn(frame_actions, "ABORT TRANSACTION", gate.destroy, False).pack(side="right")
        
        self.root.wait_window(gate)
        return state["verified"], state["text"]

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    saved_profile = setup_wizard.load_config()
    if saved_profile:
        root_init = tk.Tk(); root_init.withdraw()
        use_saved = messagebox.askyesnocancel("System Session Active", "Sync and reload active configuration space parameters?")
        root_init.destroy()
        if use_saved is True:
            DataEngineWorkstation().run()
        elif use_saved is False:
            setup_wizard.SetupWizard(lambda: DataEngineWorkstation().run()).run()
    else:
        setup_wizard.SetupWizard(lambda: DataEngineWorkstation().run()).run()