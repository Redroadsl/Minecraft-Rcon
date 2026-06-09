"""
Minecraft RCON GUI 控制台
基于 tkinter 的图形界面 RCON 客户端，提供登录、会话管理、消息自动滚动等功能。
将 rcon.py 作为库导入，使用 MCRcon 类管理 RCON 连接。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import os
import threading
from rcon import MCRcon

CONFIG_FILE = './mcrcon.ini'


def load_config():
    """加载保存的配置，返回 (ip, port, password) 或 None"""
    if not os.path.exists(CONFIG_FILE):
        return None
    config = configparser.ConfigParser()
    try:
        config.read(CONFIG_FILE, encoding='utf-8')
        if 'RCON' in config:
            return (
                config['RCON'].get('ip', ''),
                config['RCON'].get('port', ''),
                config['RCON'].get('password', '')
            )
    except Exception:
        pass
    return None


def save_config(ip, port, password):
    """保存配置到 mcrcon.ini 文件"""
    config = configparser.ConfigParser()
    config['RCON'] = {'ip': ip, 'port': port, 'password': password}
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
        return True
    except Exception:
        return False


class ConfigDialog(tk.Toplevel):
    """配置修改对话框 —— 允许用户在会话中修改 RCON 连接信息"""

    def __init__(self, parent, host, port, password, tlsmode, on_save):
        super().__init__(parent)
        self.title("修改 RCON 配置")
        self.geometry("370x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.on_save = on_save

        self._create_widgets(host, port, password, tlsmode)

    def _create_widgets(self, host, port, password, tlsmode):
        form = ttk.Frame(self, padding=15)
        form.pack(fill='both', expand=True)

        ttk.Label(form, text="IP 地址:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.ip_var = tk.StringVar(value=host)
        ttk.Entry(form, textvariable=self.ip_var, width=28).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="端口:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.port_var = tk.StringVar(value=str(port))
        ttk.Entry(form, textvariable=self.port_var, width=28).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="RCON 密码:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.pw_var = tk.StringVar(value=password)
        ttk.Entry(form, textvariable=self.pw_var, width=28, show='*').grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form, text="TLS 模式:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        tls_frame = ttk.Frame(form)
        tls_frame.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        self.tls_var = tk.IntVar(value=tlsmode)
        ttk.Radiobutton(tls_frame, text="关闭", variable=self.tls_var, value=0).pack(side='left', padx=2)
        ttk.Radiobutton(tls_frame, text="TLS", variable=self.tls_var, value=1).pack(side='left', padx=2)
        ttk.Radiobutton(tls_frame, text="免验证", variable=self.tls_var, value=2).pack(side='left', padx=2)

        ttk.Separator(form, orient='horizontal').grid(
            row=4, column=0, columnspan=2, sticky='ew', pady=10)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=5)
        ttk.Button(btn_frame, text="保存", command=self._do_save, width=10).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="取消", command=self.destroy, width=10).pack(side='left', padx=5)

    def _do_save(self):
        ip = self.ip_var.get().strip()
        port_str = self.port_var.get().strip()
        pw = self.pw_var.get()

        if not ip:
            messagebox.showerror("错误", "请输入 IP 地址", parent=self)
            return
        if not port_str:
            messagebox.showerror("错误", "请输入端口", parent=self)
            return
        try:
            int(port_str)
        except ValueError:
            messagebox.showerror("错误", "端口必须是数字", parent=self)
            return
        if not pw:
            messagebox.showerror("错误", "请输入 RCON 密码", parent=self)
            return

        save_config(ip, port_str, pw)
        self.on_save(ip, pw, int(port_str), self.tls_var.get())
        self.destroy()


class LoginFrame(ttk.Frame):
    """登录界面 —— 填写连接信息并连接到 Minecraft 服务器"""

    def __init__(self, parent, on_login):
        super().__init__(parent)
        self.on_login = on_login
        self._create_widgets()
        self._load_config()
        self.bind('<Return>', lambda e: self._connect())

    def _create_widgets(self):
        header = ttk.Frame(self)
        header.pack(pady=(40, 10))
        ttk.Label(header, text="Minecraft RCON 控制台", font=('', 16, 'bold')).pack()
        ttk.Label(header, text="远程服务器管理工具", foreground='gray').pack()

        form = ttk.Frame(self)
        form.pack(pady=10)

        ttk.Label(form, text="IP 地址:", width=10).grid(row=0, column=0, sticky='e', padx=5, pady=6)
        self.ip_var = tk.StringVar(value='127.0.0.1')
        ttk.Entry(form, textvariable=self.ip_var, width=30).grid(row=0, column=1, padx=5, pady=6)

        ttk.Label(form, text="端口:", width=10).grid(row=1, column=0, sticky='e', padx=5, pady=6)
        self.port_var = tk.StringVar(value='25575')
        ttk.Entry(form, textvariable=self.port_var, width=30).grid(row=1, column=1, padx=5, pady=6)

        ttk.Label(form, text="RCON 密码:", width=10).grid(row=2, column=0, sticky='e', padx=5, pady=6)
        self.pw_var = tk.StringVar()
        self.pw_entry = ttk.Entry(form, textvariable=self.pw_var, width=30, show='*')
        self.pw_entry.grid(row=2, column=1, padx=5, pady=6)

        self.show_pw_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(form, text="显示密码", variable=self.show_pw_var,
                        command=self._toggle_pw).grid(row=3, column=1, sticky='w', padx=5)

        ttk.Label(form, text="TLS 模式:", width=10).grid(row=4, column=0, sticky='e', padx=5, pady=6)
        tls_frame = ttk.Frame(form)
        tls_frame.grid(row=4, column=1, sticky='w', padx=5, pady=6)
        self.tls_var = tk.IntVar(value=0)
        ttk.Radiobutton(tls_frame, text="关闭", variable=self.tls_var, value=0).pack(side='left', padx=3)
        ttk.Radiobutton(tls_frame, text="TLS", variable=self.tls_var, value=1).pack(side='left', padx=3)
        ttk.Radiobutton(tls_frame, text="免验证", variable=self.tls_var, value=2).pack(side='left', padx=3)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=15)
        self._connect_btn = ttk.Button(btn_frame, text="连接服务器", command=self._connect, width=14)
        self._connect_btn.pack(side='left', padx=5)
        ttk.Button(btn_frame, text="保存配置", command=self._save_config, width=14).pack(side='left', padx=5)

        self._status_var = tk.StringVar()
        ttk.Label(self, textvariable=self._status_var, foreground='gray').pack()

    def _toggle_pw(self):
        self.pw_entry.configure(show='' if self.show_pw_var.get() else '*')

    def _load_config(self):
        cfg = load_config()
        if cfg:
            self.ip_var.set(cfg[0])
            self.port_var.set(cfg[1])
            self.pw_var.set(cfg[2])
            self._status_var.set("已加载保存的配置")
        else:
            self._status_var.set("首次使用，请填写连接信息")

    def _save_config(self):
        ip = self.ip_var.get().strip()
        port = self.port_var.get().strip()
        pw = self.pw_var.get()
        if save_config(ip, port, pw):
            self._status_var.set("配置已保存到 mcrcon.ini")
        else:
            messagebox.showerror("错误", "保存配置失败")

    def _connect(self):
        ip = self.ip_var.get().strip()
        port_str = self.port_var.get().strip()
        pw = self.pw_var.get()

        if not ip:
            messagebox.showerror("错误", "请输入 IP 地址")
            return
        if not port_str:
            messagebox.showerror("错误", "请输入端口")
            return
        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("错误", "端口必须是数字")
            return
        if not pw:
            messagebox.showerror("错误", "请输入 RCON 密码")
            return

        save_config(ip, port_str, pw)

        self._connect_btn.configure(state='disabled')
        self._status_var.set("正在连接...")

        tlsmode = self.tls_var.get()

        def do_connect():
            try:
                mcr = MCRcon(ip, pw, port, tlsmode)
                mcr.connect()
                self.after(0, lambda: self._on_connect_success(mcr))
            except Exception as e:
                err = str(e)
                self.after(0, lambda: self._on_connect_failed(err))

        threading.Thread(target=do_connect, daemon=True).start()

    def _on_connect_success(self, mcr):
        self._connect_btn.configure(state='normal')
        self._status_var.set("连接成功")
        self.unbind('<Return>')
        self.on_login(mcr)

    def _on_connect_failed(self, error):
        self._connect_btn.configure(state='normal')
        self._status_var.set("")
        messagebox.showerror("连接失败", f"无法连接到服务器:\n{error}")


class SessionFrame(ttk.Frame):
    """RCON 会话界面 —— 发送命令、查看响应、管理连接状态"""

    def __init__(self, parent, mcr, on_logout):
        super().__init__(parent)
        self.mcr = mcr
        self.host = mcr.host
        self.port = mcr.port
        self.password = mcr.password
        self.tlsmode = mcr.tlsmode
        self.on_logout = on_logout
        self.connected = True
        self._history = []
        self._history_pos = 0

        self._create_widgets()
        self._log(f"已连接到 {self.host}:{self.port}", 'info')
        self._cmd_entry.focus_set()

    def _create_widgets(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=5, pady=(5, 2))

        self._server_label = ttk.Label(toolbar, text=f"{self.host}:{self.port}",
                                       font=('', 10, 'bold'))
        self._server_label.pack(side='left')

        self._status_var = tk.StringVar(value="● 已连接")
        self._status_label = ttk.Label(toolbar, textvariable=self._status_var,
                                       foreground='green')
        self._status_label.pack(side='right', padx=(10, 5))

        ttk.Button(toolbar, text="修改配置", command=self._open_config, width=10).pack(
            side='right', padx=2)
        ttk.Button(toolbar, text="重新连接", command=self._reconnect, width=10).pack(
            side='right', padx=2)
        ttk.Button(toolbar, text="断开连接", command=self._disconnect, width=10).pack(
            side='right', padx=2)
        ttk.Button(toolbar, text="退出登录", command=self._logout, width=10).pack(
            side='right', padx=2)

        msg_container = ttk.Frame(self)
        msg_container.pack(fill='both', expand=True, padx=5, pady=2)

        self._msg_text = tk.Text(msg_container, state='disabled', wrap='word',
                                 font=('Consolas', 10),
                                 bg='#1e1e1e', fg='#d4d4d4',
                                 insertbackground='white',
                                 selectbackground='#264f78')
        self._msg_text.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(msg_container, orient='vertical',
                                  command=self._msg_text.yview)
        scrollbar.pack(side='right', fill='y')
        self._msg_text.configure(yscrollcommand=scrollbar.set)

        self._msg_text.tag_config('info', foreground='#569cd6')
        self._msg_text.tag_config('sent', foreground='#4ec9b0')
        self._msg_text.tag_config('response', foreground='#d4d4d4')
        self._msg_text.tag_config('error', foreground='#f44747')
        self._msg_text.tag_config('system', foreground='#6a9955')

        cmd_frame = ttk.Frame(self)
        cmd_frame.pack(fill='x', padx=5, pady=(2, 5))

        ttk.Label(cmd_frame, text=">").pack(side='left', padx=(0, 5))

        self._cmd_var = tk.StringVar()
        self._cmd_entry = ttk.Entry(cmd_frame, textvariable=self._cmd_var,
                                    font=('Consolas', 10))
        self._cmd_entry.pack(side='left', fill='x', expand=True)
        self._cmd_entry.bind('<Return>', lambda e: self._send_command())
        self._cmd_entry.bind('<Up>', self._history_prev)
        self._cmd_entry.bind('<Down>', self._history_next)

        self._send_btn = ttk.Button(cmd_frame, text="发送", command=self._send_command, width=8)
        self._send_btn.pack(side='right', padx=(5, 0))

    def _log(self, text, tag='response'):
        """在消息区域追加文本并自动滚动到底部"""
        self._msg_text.configure(state='normal')
        self._msg_text.insert('end', text + '\n', tag)
        self._msg_text.see('end')
        self._msg_text.configure(state='disabled')

    def _send_command(self):
        if not self.connected or self.mcr is None:
            self._log("未连接到服务器", 'error')
            return

        cmd = self._cmd_var.get().strip()
        if not cmd:
            return

        self._log(f"> {cmd}", 'sent')
        self._history.append(cmd)
        self._history_pos = len(self._history)
        self._cmd_var.set('')

        self._send_btn.configure(state='disabled')
        self._cmd_entry.configure(state='disabled')

        def do_send():
            try:
                resp = self.mcr.command(cmd)
                self.after(0, lambda: self._on_response(resp))
            except Exception as e:
                err = str(e)
                self.after(0, lambda: self._on_error(err))

        threading.Thread(target=do_send, daemon=True).start()

    def _on_response(self, resp):
        if resp:
            self._log(resp, 'response')
        self._send_btn.configure(state='normal')
        self._cmd_entry.configure(state='normal')
        self._cmd_entry.focus_set()

    def _on_error(self, error_msg):
        self._log(f"错误: {error_msg}", 'error')
        self._send_btn.configure(state='normal')
        self._cmd_entry.configure(state='normal')
        self._cmd_entry.focus_set()

        if any(kw in error_msg.lower() for kw in
               ['connection', 'socket', 'broken pipe', 'reset', 'closed']):
            self._update_connection_state(False)
            self._log("与服务器的连接已断开", 'system')

    def _disconnect(self):
        if self.mcr:
            try:
                self.mcr.disconnect()
            except Exception:
                pass
        self._update_connection_state(False)
        self._log("已断开连接", 'system')

    def _reconnect(self):
        self._log(f"正在重新连接 {self.host}:{self.port} ...", 'system')
        self._send_btn.configure(state='disabled')

        def do_reconnect():
            try:
                if self.mcr:
                    self.mcr.disconnect()
                self.mcr = MCRcon(self.host, self.password, self.port, self.tlsmode)
                self.mcr.connect()
                self.after(0, self._on_reconnect_success)
            except Exception as e:
                err = str(e)
                self.after(0, lambda: self._on_reconnect_failed(err))

        threading.Thread(target=do_reconnect, daemon=True).start()

    def _on_reconnect_success(self):
        self._update_connection_state(True)
        self._log(f"已连接到 {self.host}:{self.port}", 'info')
        self._send_btn.configure(state='normal')
        self._cmd_entry.focus_set()

    def _on_reconnect_failed(self, error):
        self._log(f"重新连接失败: {error}", 'error')
        self._send_btn.configure(state='normal')

    def _open_config(self):
        """打开配置修改对话框"""

        def on_config_saved(host, password, port, tlsmode):
            self.host = host
            self.password = password
            self.port = port
            self.tlsmode = tlsmode
            self._server_label.configure(text=f"{host}:{port}")
            self._log("配置已更新，请使用「重新连接」以应用新配置", 'system')

        ConfigDialog(self, self.host, self.port, self.password, self.tlsmode,
                     on_config_saved)

    def _logout(self):
        if self.mcr:
            try:
                self.mcr.disconnect()
            except Exception:
                pass
        self.on_logout()

    def _update_connection_state(self, connected):
        self.connected = connected
        if connected:
            self._status_var.set("● 已连接")
            self._status_label.configure(foreground='green')
        else:
            self._status_var.set("● 未连接")
            self._status_label.configure(foreground='red')

    def _history_prev(self, event):
        if self._history:
            self._history_pos = max(0, self._history_pos - 1)
            self._cmd_var.set(self._history[self._history_pos])

    def _history_next(self, event):
        if self._history:
            self._history_pos = min(len(self._history), self._history_pos + 1)
            if self._history_pos < len(self._history):
                self._cmd_var.set(self._history[self._history_pos])
            else:
                self._cmd_var.set('')


class App(tk.Tk):
    """主应用程序 —— 管理登录与会话界面的切换"""

    def __init__(self):
        super().__init__()
        self.title("Minecraft RCON 控制台")
        self.geometry("750x550")
        self.minsize(500, 380)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._session_frame = None

        self._create_menu()

        self._container = ttk.Frame(self)
        self._container.pack(fill='both', expand=True)

        self._show_login()

    def _create_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="退出", command=self._on_close)
        menubar.add_cascade(label="文件", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.config(menu=menubar)

    def _show_about(self):
        messagebox.showinfo("关于",
                            "Minecraft RCON 控制台\n\n"
                            "基于 mcrcon 库的图形界面客户端\n"
                            "用于远程管理 Minecraft 服务器\n\n"
                            "原始项目: github.com/laomie233/Minecraft-Rcon")

    def _show_login(self):
        for w in self._container.winfo_children():
            w.destroy()
        self._session_frame = None
        LoginFrame(self._container, self._on_login).pack(
            fill='both', expand=True, padx=20, pady=20)

    def _on_login(self, mcr):
        for w in self._container.winfo_children():
            w.destroy()
        self._session_frame = SessionFrame(self._container, mcr, on_logout=self._show_login)
        self._session_frame.pack(fill='both', expand=True)

    def _on_close(self):
        if self._session_frame and self._session_frame.mcr:
            try:
                self._session_frame.mcr.disconnect()
            except Exception:
                pass
        self.destroy()


if __name__ == '__main__':
    app = App()
    app.mainloop()
