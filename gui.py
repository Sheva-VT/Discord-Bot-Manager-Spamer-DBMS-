import customtkinter as ctk
import json
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog

# ======================================================
# PATH CONFIG & MAIN
# ======================================================
BASE = Path(__file__).resolve().parent

CONFIG_DIR = BASE / "config"
CONFIG_DIR.mkdir(exist_ok=True)

CONFIG_PATH = CONFIG_DIR / "config.json"

MAIN_DIR = BASE / "main"
MAIN_PATH = MAIN_DIR / "main.py"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ======================================================
# CONFIG HELPERS
# ======================================================
def ensure_config_exists():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        default = {"Config": [], "RUN": False}
        CONFIG_PATH.write_text(json.dumps(default, indent=4), encoding="utf-8")


def load_config():
    ensure_config_exists()
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"Config": [], "RUN": False}


def save_config(cfg):
    ensure_config_exists()
    CONFIG_PATH.write_text(json.dumps(cfg, indent=4, ensure_ascii=False), encoding="utf-8")


# ======================================================
# MAIN GUI CLASS
# ======================================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Discord Bot Manager")
        self.geometry("1200x650")
        self.minsize(980, 600)

        self.cfg = load_config()
        self.selected_acc_index = 0 if self.cfg.get("Config") else -1
        self.channel_edit_mode = None
        self.channel_edit_index = None

        sidebar = ctk.CTkFrame(self, width=160)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkButton(sidebar, text="Accounts", command=self.show_accounts).pack(fill="x", pady=5)
        ctk.CTkButton(sidebar, text="Run Bot", command=self.show_run).pack(fill="x", pady=5)

        self.content = ctk.CTkFrame(self)
        self.content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.show_accounts()

    def clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ======================================================
    # PAGE: ACCOUNTS
    # ======================================================
    def show_accounts(self):
        self.clear()
        self.cfg = load_config()

        if not self.cfg.get("Config"):
            self.selected_acc_index = -1
        else:
            if self.selected_acc_index < 0 or self.selected_acc_index >= len(self.cfg["Config"]):
                self.selected_acc_index = 0

        left = ctk.CTkFrame(self.content, width=260)
        center = ctk.CTkFrame(self.content)
        right = ctk.CTkFrame(self.content)

        left.pack(side="left", fill="y", padx=10)
        center.pack(side="left", fill="both", expand=True)
        right.pack(side="right", fill="both", expand=True)

        self.acc_left = left
        self.acc_center = center
        self.acc_right = right

        self.draw_account_list()
        self.draw_account_editor()
        self.draw_channel_list()

    # LEFT PANEL — ACCOUNT LIST
    def draw_account_list(self):
        for w in self.acc_left.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.acc_left, text="Accounts", font=("Arial", 18)).pack(pady=10)

        self.acc_check_vars = []

        self.acc_select_all_var = tk.BooleanVar(value=False)

        def toggle_all():
            for _, var in self.acc_check_vars:
                var.set(self.acc_select_all_var.get())

        ctk.CTkCheckBox(self.acc_left, text="Select All Accounts",
                        variable=self.acc_select_all_var,
                        command=toggle_all).pack(anchor="w", pady=5)

        for i, acc in enumerate(self.cfg.get("Config", [])):
            frame = ctk.CTkFrame(self.acc_left)
            frame.pack(fill="x", pady=3)

            var = tk.BooleanVar(value=False)
            self.acc_check_vars.append((i, var))

            ctk.CTkCheckBox(frame, text=acc.get("name", f"Acc {i}"), variable=var).pack(side="left")
            ctk.CTkButton(frame, text="Open", width=60,
                          command=lambda idx=i: self.select_account(idx)).pack(side="right", padx=5)

        ctk.CTkButton(self.acc_left, text="+ Add Account",
                      command=self.add_account).pack(fill="x", pady=10)

        ctk.CTkButton(self.acc_left, text="Delete Selected",
                      fg_color="#b32d2d", hover_color="#8a1f1f",
                      command=self.delete_selected_accounts).pack(fill="x", pady=15)

    def select_account(self, idx):
        self.selected_acc_index = idx
        self.channel_edit_mode = None
        self.draw_account_editor()
        self.draw_channel_list()

    def add_account(self):
        self.cfg.setdefault("Config", []).append({
            "name": "New Account",
            "token": "",
            "webhook": "",
            "selected": False,
            "world": [],
            "channels": []
        })
        save_config(self.cfg)
        self.selected_acc_index = len(self.cfg["Config"]) - 1
        self.show_accounts()

    def delete_selected_accounts(self):
        selected = [i for i, var in self.acc_check_vars if var.get()]
        if not selected:
            messagebox.showerror("Error", "Tidak ada akun dipilih.")
            return

        for i in sorted(selected, reverse=True):
            self.cfg["Config"].pop(i)

        save_config(self.cfg)
        self.selected_acc_index = 0 if self.cfg.get("Config") else -1
        self.show_accounts()

    # CENTER PANEL — ACCOUNT SETTINGS + WORLD
    def draw_account_editor(self):
        for w in self.acc_center.winfo_children():
            w.destroy()

        if self.selected_acc_index < 0:
            ctk.CTkLabel(self.acc_center, text="No accounts.", text_color="#777").pack()
            return

        acc = self.cfg["Config"][self.selected_acc_index]

        ctk.CTkLabel(self.acc_center, text="Account Settings",
                     font=("Arial", 18)).pack(pady=10)

        self.var_name = tk.StringVar(value=acc.get("name", ""))
        self.var_token = tk.StringVar(value=acc.get("token", ""))
        self.var_webhook = tk.StringVar(value=acc.get("webhook", ""))
        self.var_selected = tk.BooleanVar(value=acc.get("selected", False))

        ctk.CTkLabel(self.acc_center, text="Name").pack(anchor="w")
        ctk.CTkEntry(self.acc_center, textvariable=self.var_name).pack(fill="x", pady=5)

        ctk.CTkLabel(self.acc_center, text="Token").pack(anchor="w")
        ctk.CTkEntry(self.acc_center, textvariable=self.var_token).pack(fill="x", pady=5)

        ctk.CTkLabel(self.acc_center, text="Webhook").pack(anchor="w")
        ctk.CTkEntry(self.acc_center, textvariable=self.var_webhook).pack(fill="x", pady=5)

        ctk.CTkSwitch(self.acc_center, text="Run this account",
                      variable=self.var_selected).pack(anchor="w", pady=10)

        # WORLD PANEL
        ctk.CTkLabel(self.acc_center, text="World List",
                     font=("Arial", 16)).pack(pady=8)

        self.world_frame = ctk.CTkFrame(self.acc_center)
        self.world_frame.pack(fill="x")
        self.world_vars = []
        self.draw_world_items(acc)

        # WORLD CONTROLS
        ctrl = ctk.CTkFrame(self.acc_center)
        ctrl.pack(pady=10, fill="x")

        self.var_new_world = tk.StringVar()
        ctk.CTkEntry(ctrl, placeholder_text="New world",
                     textvariable=self.var_new_world).pack(side="left", fill="x", expand=True)

        ctk.CTkButton(ctrl, text="+ Add",
                      command=self.add_world).pack(side="left", padx=5)

        ctk.CTkButton(ctrl, text="Delete Selected",
                      fg_color="#b32d2d", hover_color="#8a1f1f",
                      command=self.delete_worlds).pack(side="left", padx=5)

        # SAVE/DELETE ACCOUNT
        btnf = ctk.CTkFrame(self.acc_center)
        btnf.pack(pady=12)

        ctk.CTkButton(btnf, text="Save", command=self.save_account).pack(side="left", padx=6)
        ctk.CTkButton(btnf, text="Delete",
                      fg_color="#b32d2d", hover_color="#8a1f1f",
                      command=self.delete_current_account).pack(side="left", padx=6)

    def draw_world_items(self, acc):
        for w in self.world_frame.winfo_children():
            w.destroy()

        self.world_vars = []

        for idx, wobj in enumerate(acc.get("world", [])):
            row = ctk.CTkFrame(self.world_frame)
            row.pack(fill="x", pady=2)

            var = tk.BooleanVar(value=wobj.get("active", True))
            self.world_vars.append((idx, var))

            ctk.CTkCheckBox(row, text=wobj.get("name", f"world{idx}"),
                             variable=var,
                             command=lambda i=idx, v=var: self.update_world_active(i, v)
                             ).pack(anchor="w")

    def update_world_active(self, idx, var):
        acc = self.cfg["Config"][self.selected_acc_index]
        acc["world"][idx]["active"] = bool(var.get())
        save_config(self.cfg)

    def add_world(self):
        name = self.var_new_world.get().strip()
        if not name:
            return
        acc = self.cfg["Config"][self.selected_acc_index]
        acc.setdefault("world", []).append({"name": name, "active": True})
        save_config(self.cfg)
        self.draw_account_editor()

    def delete_worlds(self):
        acc = self.cfg["Config"][self.selected_acc_index]
        selected = [i for i, v in self.world_vars if v.get()]

        for i in sorted(selected, reverse=True):
            acc["world"].pop(i)

        save_config(self.cfg)
        self.draw_account_editor()

    def save_account(self):
        acc = self.cfg["Config"][self.selected_acc_index]
        acc["name"] = self.var_name.get()
        acc["token"] = self.var_token.get()
        acc["webhook"] = self.var_webhook.get()
        acc["selected"] = bool(self.var_selected.get())

        for i, v in self.world_vars:
            acc["world"][i]["active"] = bool(v.get())

        save_config(self.cfg)
        self.draw_account_list()
        messagebox.showinfo("Saved", "Account saved.")

    def delete_current_account(self):
        acc = self.cfg["Config"][self.selected_acc_index]
        self.cfg["Config"].pop(self.selected_acc_index)
        save_config(self.cfg)
        self.selected_acc_index = 0 if self.cfg["Config"] else -1
        self.show_accounts()

    # ======================================================
    # RIGHT PANEL — CHANNEL LIST
    # ======================================================
    def draw_channel_list(self):
        for w in self.acc_right.winfo_children():
            w.destroy()

        if self.selected_acc_index < 0:
            ctk.CTkLabel(self.acc_right, text="No account selected.",
                         text_color="#888").pack(pady=20)
            return

        acc = self.cfg["Config"][self.selected_acc_index]

        if self.channel_edit_mode:
            self.draw_channel_editor(acc)
            return

        ctk.CTkLabel(self.acc_right, text="Channels", font=("Arial", 18)).pack(pady=10)

        self.channel_check_vars = []
        self.channel_select_all_var = tk.BooleanVar(value=False)

        def toggle_all():
            for _, v in self.channel_check_vars:
                v.set(self.channel_select_all_var.get())

        ctk.CTkCheckBox(self.acc_right, text="Select All Channels",
                        variable=self.channel_select_all_var,
                        command=toggle_all).pack(anchor="w", pady=5)

        ctk.CTkButton(self.acc_right, text="+ Add Channel", height=35,
                      command=self.add_channel).pack(fill="x", pady=10)

        for idx, ch in enumerate(acc.get("channels", [])):
            frame = ctk.CTkFrame(self.acc_right)
            frame.pack(fill="x", pady=3)

            var = tk.BooleanVar(value=False)
            self.channel_check_vars.append((idx, var))

            ctk.CTkCheckBox(frame, text=ch.get("channelid", f"ch-{idx}"),
                            variable=var).pack(side="left")

            ctk.CTkButton(frame, text="Edit", width=60,
                          command=lambda i=idx: self.edit_channel(i)).pack(side="left", padx=5)

            ctk.CTkButton(frame, text="Del", width=60,
                          fg_color="#aa3333", hover_color="#882222",
                          command=lambda i=idx: self.delete_channel(i)).pack(side="left", padx=5)

        ctk.CTkButton(self.acc_right, text="Delete Selected Channels",
                      fg_color="#b32d2d", hover_color="#8a1f1f",
                      command=self.delete_selected_channels).pack(fill="x", pady=10)

    def add_channel(self):
        self.channel_edit_mode = "add"
        self.draw_channel_list()

    def edit_channel(self, idx):
        self.channel_edit_index = idx
        self.channel_edit_mode = "edit"
        self.draw_channel_list()

    def delete_channel(self, idx):
        acc = self.cfg["Config"][self.selected_acc_index]
        acc["channels"].pop(idx)
        save_config(self.cfg)
        self.draw_channel_list()

    def delete_selected_channels(self):
        acc = self.cfg["Config"][self.selected_acc_index]
        selected = [i for i, v in self.channel_check_vars if v.get()]

        for i in sorted(selected, reverse=True):
            acc["channels"].pop(i)

        save_config(self.cfg)
        self.draw_channel_list()

    # CHANNEL EDITOR
    def draw_channel_editor(self, acc):
        for w in self.acc_right.winfo_children():
            w.destroy()

        if self.channel_edit_mode == "edit":
            ch = acc["channels"][self.channel_edit_index]
        else:
            ch = {"channelid": "", "message": "", "delay": [10, 20], "count": 0, "active": True}

        self.var_chid = tk.StringVar(value=ch["channelid"])
        self.var_msg = tk.StringVar(value=ch["message"])
        self.var_cnt = tk.StringVar(value=str(ch.get("count", 0)))
        d0, d1 = ch.get("delay", [10, 20])
        self.var_min = tk.StringVar(value=str(d0))
        self.var_max = tk.StringVar(value=str(d1))
        self.var_act = tk.BooleanVar(value=ch.get("active", True))

        ctk.CTkLabel(self.acc_right, text="Channel Editor",
                     font=("Arial", 18)).pack(pady=10)

        labels = ["Channel ID", "Message", "Count", "Delay Min", "Delay Max"]
        vars = [self.var_chid, self.var_msg, self.var_cnt, self.var_min, self.var_max]

        for lbl, var in zip(labels, vars):
            ctk.CTkLabel(self.acc_right, text=lbl).pack(anchor="w")
            ctk.CTkEntry(self.acc_right, textvariable=var).pack(fill="x", pady=4)

        ctk.CTkSwitch(self.acc_right, text="Active", variable=self.var_act).pack(anchor="w", pady=6)

        btn = ctk.CTkFrame(self.acc_right)
        btn.pack(pady=10)

        ctk.CTkButton(btn, text="Save", width=120,
                      command=self.save_channel).pack(side="left", padx=8)
        ctk.CTkButton(btn, text="Cancel", width=120,
                      command=self.cancel_channel_edit).pack(side="left", padx=8)

    def save_channel(self):
        try:
            dmin = int(self.var_min.get())
            dmax = int(self.var_max.get())
            cnt = int(self.var_cnt.get())
        except:
            messagebox.showerror("Error", "Delay & Count harus angka!")
            return

        acc = self.cfg["Config"][self.selected_acc_index]

        data = {
            "channelid": self.var_chid.get().strip(),
            "message": self.var_msg.get(),
            "delay": [dmin, dmax],
            "count": cnt,
            "active": bool(self.var_act.get())
        }

        if self.channel_edit_mode == "add":
            acc["channels"].append(data)
        else:
            acc["channels"][self.channel_edit_index] = data

        save_config(self.cfg)
        self.channel_edit_mode = None
        self.draw_channel_list()

    def cancel_channel_edit(self):
        self.channel_edit_mode = None
        self.draw_channel_list()

    # ======================================================
    # RUN PAGE
    # ======================================================
    def show_run(self):
        self.clear()
        cfg = load_config()

        ctk.CTkLabel(self.content, text="Run Bot",
                     font=("Arial", 20)).pack(anchor="w", pady=10)

        ctk.CTkLabel(self.content, text="Select Accounts to Run:",
                     font=("Arial", 15)).pack(anchor="w", padx=20)

        self.run_acc_vars = []

        for idx, acc in enumerate(cfg.get("Config", [])):
            frame = ctk.CTkFrame(self.content)
            frame.pack(fill="x", pady=5, padx=20)

            var = tk.BooleanVar(value=acc.get("selected", False))
            self.run_acc_vars.append((idx, var))

            ctk.CTkCheckBox(
                frame,
                text=acc.get("name", f"Acc {idx}"),
                variable=var,
                command=lambda i=idx, v=var: self.toggle_acc_selection(i, v)
            ).pack(anchor="w")

            for ch in acc.get("channels", []):
                state = "✓ active" if ch.get("active", True) else "× disabled"
                ctk.CTkLabel(
                    frame,
                    text=f"   - {ch.get('channelid')} ({state})",
                    text_color="#888"
                ).pack(anchor="w")

        # RUN / STOP BUTTON
        is_running = cfg.get("RUN", False)

        self.run_button = ctk.CTkButton(
            self.content,
            text="STOP BOT" if is_running else "RUN BOT",
            fg_color="#c92c2c" if is_running else "#1f6fb2",
            hover_color="#9c1f1f" if is_running else "#174f7c",
            height=55,
            command=self.toggle_run
        )
        self.run_button.pack(fill="x", padx=40, pady=20)

    def toggle_acc_selection(self, idx, var):
        cfg = load_config()
        cfg["Config"][idx]["selected"] = bool(var.get())
        save_config(cfg)

    def toggle_run(self):
        cfg = load_config()

        if not cfg.get("RUN"):
            cfg["RUN"] = True
            save_config(cfg)

            if MAIN_PATH.exists():
                subprocess.Popen(["python", str(MAIN_PATH)])

            self.run_button.configure(text="STOP BOT",
                                      fg_color="#c92c2c",
                                      hover_color="#9c1f1f")
            messagebox.showinfo("Running", "Bot started.")
        else:
            cfg["RUN"] = False
            save_config(cfg)

            self.run_button.configure(text="RUN BOT",
                                      fg_color="#1f6fb2",
                                      hover_color="#174f7c")
            messagebox.showinfo("Stopped", "Bot stopped.")


# ======================================================
if __name__ == "__main__":
    ensure_config_exists()
    app = App()
    app.mainloop()
