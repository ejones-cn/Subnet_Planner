import ipaddress
import tkinter as tk
from tkinter import ttk
from collections import deque

from i18n import _
from style_manager import get_current_font_settings, get_style_manager
from services.table_column_manager import TableColumnManager


class SubnetPlannerUIBuilder:
    def __init__(self, app):
        self.app = app

    def build_all(self):
        self.app.create_top_level_notebook()
        self.app.create_about_link()

    def create_split_input_section(self):
        app = self.app
        app.split_frame.grid_columnconfigure(0, weight=1, uniform="equal")
        app.split_frame.grid_columnconfigure(1, weight=1, uniform="equal")
        app.split_frame.grid_rowconfigure(0, weight=0)
        app.split_frame.grid_rowconfigure(1, weight=1)

        input_frame = ttk.LabelFrame(
            app.split_frame, text=_("input_parameters"), padding=(10, 10, 10, 10)
        )
        input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 10))

        history_frame = ttk.LabelFrame(app.split_frame, text=_("history"), padding=(10, 10, 10, 10))
        history_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 10))

        ip_version_frame = ttk.Frame(input_frame)
        ip_version_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=0)

        app.split_ip_version_var = tk.StringVar(value="IPv4")

        ipv4_btn = ttk.Radiobutton(ip_version_frame, text="IPv4", variable=app.split_ip_version_var, value="IPv4",
                                   command=app.on_split_ip_version_change, style="IpVersion.TRadiobutton")
        ipv4_btn.pack(side=tk.LEFT, padx=(10, 10))

        ipv6_btn = ttk.Radiobutton(ip_version_frame, text="IPv6", variable=app.split_ip_version_var, value="IPv6",
                                   command=app.on_split_ip_version_change, style="IpVersion.TRadiobutton")
        ipv6_btn.pack(side=tk.LEFT)

        input_frame.grid_columnconfigure(0, minsize=30, weight=0)
        input_frame.grid_columnconfigure(1, minsize=0, weight=1)
        input_frame.grid_columnconfigure(2, weight=0)
        input_frame.grid_rowconfigure(0, weight=0, minsize=0)
        input_frame.grid_rowconfigure(1, weight=0)
        input_frame.grid_rowconfigure(2, weight=0)
        input_frame.grid_rowconfigure(3, weight=0, minsize=0)
        input_frame.grid_rowconfigure(4, weight=0, minsize=0)

        font_family, font_size = get_current_font_settings()

        ttk.Label(input_frame, text=_("parent_network"), anchor="w", font=(font_family, font_size)).grid(
            row=1, column=0, sticky=tk.W + tk.N + tk.S, pady=4, padx=(10, 0)
        )

        app.split_parent_networks_v4 = deque(["10.0.0.0/8", "172.16.0.0/12"], maxlen=100)
        app.split_parent_networks_v6 = deque(["2001:0db8::/32", "fe80::/10"], maxlen=100)
        app.split_networks_v4 = deque(["10.21.50.0/23", "172.20.180.0/24"], maxlen=100)
        app.split_networks_v6 = deque(["2001:0db8::/64", "fe80::1/128"], maxlen=100)

        ip_version = app.split_ip_version_var.get()
        if ip_version == "IPv4":
            app.split_parent_networks = app.split_parent_networks_v4
            app.split_networks = app.split_networks_v4
            default_parent = "10.0.0.0/8"
            default_split = "10.21.50.0/23"
        else:
            app.split_parent_networks = app.split_parent_networks_v6
            app.split_networks = app.split_networks_v6
            default_parent = "2001:0db8::/32"
            default_split = "2001:0db8::/64"

        vcmd = (app.root.register(lambda p: app.validate_cidr(p, app.parent_entry, ip_version=app.split_ip_version_var.get())), '%P')
        app.parent_entry = ttk.Combobox(
            input_frame,
            values=app.split_parent_networks,
            font=(font_family, font_size),
            validate='all',
            validatecommand=vcmd,
        )
        app.parent_entry.grid(row=1, column=1, padx=10, pady=4, sticky=tk.EW + tk.N + tk.S)
        app.parent_entry.insert(0, default_parent)
        app.parent_entry.config(state="normal")
        app.parent_entry.bind('<KeyRelease>', app.autocomplete_ipv6)

        ttk.Label(input_frame, text=_("split_segments"), anchor="w", font=(font_family, font_size)).grid(
            row=2, column=0, sticky=tk.W + tk.N + tk.S, pady=4, padx=(10, 0)
        )
        vcmd = (app.root.register(lambda text: app.validate_cidr(text, app.split_entry, ip_version=app.split_ip_version_var.get())), '%P')
        app.split_entry = ttk.Combobox(
            input_frame,
            values=app.split_networks,
            font=(font_family, font_size),
            validate='all',
            validatecommand=vcmd,
        )
        app.split_entry.grid(row=2, column=1, padx=10, pady=4, sticky=tk.EW + tk.N + tk.S)
        app.split_entry.insert(0, default_split)
        app.split_entry.config(state="normal")
        app.split_entry.bind('<KeyRelease>', app.autocomplete_ipv6)

        app.execute_btn = ttk.Button(input_frame, text=_("execute_split"), command=app.execute_split, width=10)
        app.execute_btn.grid(row=0, column=2, rowspan=4, padx=(0, 0), pady=0, sticky=tk.NSEW)

        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_rowconfigure(1, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_columnconfigure(1, weight=0)
        history_frame.grid_columnconfigure(2, weight=0)

        app.history_listbox = tk.Listbox(
            history_frame, height=3, font=(font_family, font_size),
            highlightthickness=1, highlightbackground="#999999", highlightcolor="#999999",
            bd=0, selectbackground="#0078D7", selectforeground="white", takefocus=False
        )
        app.history_listbox.configure(activestyle="none")
        app.history_listbox.grid(row=0, column=0, sticky="nsew", rowspan=2)

        history_scroll = ttk.Scrollbar(history_frame, orient=tk.VERTICAL)
        app._setup_scrollbar(history_scroll, app.history_listbox, initial_hidden=True)
        app.bind_listbox_right_click(app.history_listbox)

        app.reexecute_btn = ttk.Button(
            history_frame, text=_("reexecute_split"), command=app.reexecute_split, width=10
        )
        app.reexecute_btn.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(5, 0))
