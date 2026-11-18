import secrets
import string
import customtkinter as ctk
from tkinter import messagebox, simpledialog
from .database import VaultDatabase
from .auth import AuthService, AuthError
from .vault import VaultService

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class SecureVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ALPHA Secure Vault")
        self.geometry("980x650")
        self.minsize(820, 560)
        self.configure(fg_color="#0b0f0d")
        self.db = VaultDatabase()
        self.auth = AuthService(self.db)
        self.user_id = None
        self.fernet = None
        self.vault = None
        self.show_auth()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def heading(self, parent, title, subtitle=""):
        ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(size=28, weight="bold"), text_color="#7CFF9B").pack(pady=(10, 4))
        if subtitle:
            ctk.CTkLabel(parent, text=subtitle, text_color="#a8b5ad").pack(pady=(0, 14))

    def show_auth(self):
        self.clear()
        panel = ctk.CTkFrame(self, fg_color="#121a16", corner_radius=18, border_color="#285a3b", border_width=1)
        panel.place(relx=.5, rely=.5, anchor="center", relwidth=.43, relheight=.70)
        self.heading(panel, "ALPHA SECURE VAULT", "Local encrypted password manager")
        self.username = ctk.CTkEntry(panel, placeholder_text="Username", height=42)
        self.username.pack(fill="x", padx=35, pady=8)
        self.password = ctk.CTkEntry(panel, placeholder_text="Master password (10+ characters)", show="•", height=42)
        self.password.pack(fill="x", padx=35, pady=8)
        ctk.CTkButton(panel, text="LOGIN", height=42, fg_color="#168344", hover_color="#1ca85a", command=self.login).pack(fill="x", padx=35, pady=(18, 8))
        ctk.CTkButton(panel, text="CREATE ACCOUNT", height=42, fg_color="#27352d", hover_color="#34483b", command=self.register).pack(fill="x", padx=35, pady=8)
        ctk.CTkLabel(panel, text="Your master password is never stored.", text_color="#84968a").pack(pady=15)

    def credentials(self):
        return self.username.get().strip(), self.password.get()

    def register(self):
        username, password = self.credentials()
        try:
            self.user_id, self.fernet = self.auth.register(username, password)
            self.open_vault()
        except AuthError as exc:
            messagebox.showerror("Registration", str(exc))

    def login(self):
        username, password = self.credentials()
        try:
            self.user_id, self.fernet = self.auth.login(username, password)
            self.open_vault()
        except AuthError as exc:
            messagebox.showerror("Login", str(exc))

    def open_vault(self):
        self.vault = VaultService(self.db, self.user_id, self.fernet)
        self.show_dashboard()

    def show_dashboard(self):
        self.clear()
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=24, pady=(20, 8))
        ctk.CTkLabel(top, text="ALPHA / VAULT", font=ctk.CTkFont(size=24, weight="bold"), text_color="#7CFF9B").pack(side="left")
        ctk.CTkButton(top, text="LOG OUT", width=110, fg_color="#6b3329", hover_color="#8c4032", command=self.logout).pack(side="right")
        toolbar = ctk.CTkFrame(self, fg_color="#121a16", corner_radius=12)
        toolbar.pack(fill="x", padx=24, pady=10)
        self.search = ctk.CTkEntry(toolbar, placeholder_text="Search title, username, website...", height=38)
        self.search.pack(side="left", fill="x", expand=True, padx=12, pady=12)
        self.search.bind("<KeyRelease>", lambda _e: self.refresh_entries())
        ctk.CTkButton(toolbar, text="+ ADD ENTRY", command=self.add_entry).pack(side="right", padx=12, pady=12)
        ctk.CTkButton(toolbar, text="GENERATE", fg_color="#8a5421", hover_color="#a96a2c", command=self.generate).pack(side="right", padx=0, pady=12)
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="#101612", corner_radius=12)
        self.list_frame.pack(fill="both", expand=True, padx=24, pady=(4, 20))
        self.refresh_entries()

    def refresh_entries(self):
        if not hasattr(self, "list_frame") or not self.list_frame.winfo_exists():
            return
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        try:
            entries = self.vault.all()
        except Exception as exc:
            messagebox.showerror("Vault error", f"Could not decrypt vault data: {exc}")
            return
        term = self.search.get().lower() if hasattr(self, "search") else ""
        for entry in entries:
            searchable = " ".join([entry["title"], entry["username"], entry["website"]]).lower()
            if term not in searchable:
                continue
            card = ctk.CTkFrame(self.list_frame, fg_color="#19231c", corner_radius=10)
            card.pack(fill="x", padx=8, pady=6)
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=14, pady=10)
            ctk.CTkLabel(info, text=entry["title"], font=ctk.CTkFont(size=16, weight="bold"), text_color="#a5ffb8").pack(anchor="w")
            ctk.CTkLabel(info, text=f'{entry["username"]}   •   {entry["website"]}', text_color="#b6c3ba").pack(anchor="w")
            ctk.CTkButton(card, text="SHOW", width=70, command=lambda e=entry: self.show_password(e)).pack(side="right", padx=5)
            ctk.CTkButton(card, text="EDIT", width=65, fg_color="#36503d", command=lambda e=entry: self.edit_entry(e)).pack(side="right", padx=5)
            ctk.CTkButton(card, text="DELETE", width=75, fg_color="#71392f", hover_color="#914638", command=lambda e=entry: self.delete_entry(e)).pack(side="right", padx=10)

    def show_password(self, entry):
        messagebox.showinfo(entry["title"], f'Username: {entry["username"]}\nPassword: {entry["password"]}\nWebsite: {entry["website"]}\n\nNotes: {entry["notes"]}')

    def entry_dialog(self, title, initial=None):
        initial = initial or {}
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry("470x520")
        win.transient(self)
        win.grab_set()
        fields = {}
        specs = [("title", "Title"), ("username", "Username"), ("password", "Password"), ("website", "Website / URL"), ("notes", "Notes")]
        for key, label in specs:
            ctk.CTkLabel(win, text=label).pack(anchor="w", padx=25, pady=(12, 2))
            entry = ctk.CTkEntry(win, height=38, show="•" if key == "password" else "")
            entry.pack(fill="x", padx=25)
            entry.insert(0, initial.get(key, ""))
            fields[key] = entry
        def save():
            data = {k: v.get() for k, v in fields.items()}
            if not data["title"] or not data["password"]:
                messagebox.showwarning("Missing data", "Title and password are required.", parent=win)
                return
            try:
                if initial.get("id"):
                    self.vault.update(initial["id"], **data)
                else:
                    self.vault.add(**data)
                win.destroy()
                self.refresh_entries()
            except Exception as exc:
                messagebox.showerror("Save failed", str(exc), parent=win)
        ctk.CTkButton(win, text="SAVE ENTRY", command=save, height=42).pack(fill="x", padx=25, pady=22)

    def add_entry(self):
        self.entry_dialog("Add entry")

    def edit_entry(self, entry):
        self.entry_dialog("Edit entry", entry)

    def delete_entry(self, entry):
        if messagebox.askyesno("Delete", f'Delete "{entry["title"]}"?'):
            self.vault.delete(entry["id"])
            self.refresh_entries()

    def generate(self):
        length = simpledialog.askinteger("Password generator", "Password length (12–64):", minvalue=12, maxvalue=64, initialvalue=20, parent=self)
        if length:
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
            value = "".join(secrets.choice(alphabet) for _ in range(length))
            self.clipboard_clear()
            self.clipboard_append(value)
            messagebox.showinfo("Generated", "A random password was copied to the clipboard.")

    def logout(self):
        self.user_id = self.fernet = self.vault = None
        self.show_auth()
