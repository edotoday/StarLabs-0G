import customtkinter as ctk
import yaml
import os


class ConfigUI:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Define color scheme
        self.colors = {
            "bg": "#121212",  # Slightly lighter black background
            "frame_bg": "#1e1e1e",  # Slightly lighter frame background
            "accent": "#B8860B",  # More muted gold/yellow (DarkGoldenrod)
            "text": "#ffffff",  # White text
            "entry_bg": "#1e1e1e",  # Dark input background
            "hover": "#8B6914",  # Darker muted yellow for hover
        }

        # Standardize input widths
        self.input_sizes = {
            "tiny": 70,  # For small numbers (1-2 digits)
            "small": 115,  # For short text/numbers
            "medium": 180,  # For medium length text
            "large": 250,  # For long text
            "extra_large": 350,  # For very long text/lists
        }

        self.root = ctk.CTk()
        self.root.title("StarLabs Configuration")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)  # Set minimum window size
        self.root.configure(fg_color=self.colors["bg"])

        # Create header frame
        header_frame = ctk.CTkFrame(self.root, fg_color=self.colors["bg"])
        header_frame.pack(fill="x", padx=50, pady=(20, 0))

        # Header on the left
        header = ctk.CTkLabel(
            header_frame,
            text="🌟 StarLabs Configuration",
            font=("Helvetica", 24, "bold"),
            text_color=self.colors["accent"],
            anchor="w",
        )
        header.pack(side="left", padx=5)

        # Save button in the top right
        self.save_button = ctk.CTkButton(
            header_frame,
            text="⚡ SAVE",
            command=self._save_and_close,
            font=("Helvetica", 18, "bold"),
            height=45,
            width=160,
            fg_color=self.colors["accent"],
            hover_color=self.colors["hover"],
            text_color=self.colors["text"],
            corner_radius=10,
        )
        self.save_button.pack(side="right", padx=5)

        # Create main frame with scrollbar
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.colors["bg"])
        self.main_frame.pack(fill="both", expand=True, padx=5)

        # Add canvas and scrollbar
        self.canvas = ctk.CTkCanvas(
            self.main_frame, bg=self.colors["bg"], highlightthickness=0
        )
        self.scrollbar = ctk.CTkScrollbar(
            self.main_frame,
            orientation="vertical",
            command=self.canvas.yview,
            fg_color=self.colors["frame_bg"],
            button_color=self.colors["accent"],
            button_hover_color=self.colors["hover"],
        )
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color=self.colors["bg"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        # Pack scrollbar components
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Create window in canvas with proper width
        self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            width=self.canvas.winfo_width(),
        )

        # Update canvas width when window is resized
        def update_canvas_width(event):
            self.canvas.itemconfig(
                self.canvas.find_withtag("all")[0], width=event.width
            )

        self.canvas.bind("<Configure>", update_canvas_width)

        # Configure scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.load_config()
        self.create_widgets()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
        with open(config_path, "r") as file:
            self.config = yaml.safe_load(file)

    def create_range_inputs(self, parent, label, config_value, width=120):
        frame = ctk.CTkFrame(parent, fg_color=self.colors["frame_bg"])
        frame.pack(fill="x", pady=5)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame,
            text=f"{label}:",
            width=200,
            anchor="w",
            font=("Helvetica", 12, "bold"),
            text_color=self.colors["text"],
        ).grid(row=0, column=0, padx=(10, 10), sticky="w")

        input_frame = ctk.CTkFrame(frame, fg_color=self.colors["frame_bg"])
        input_frame.grid(row=0, column=1, sticky="e", padx=(0, 10))

        min_entry = ctk.CTkEntry(
            input_frame,
            width=width,
            font=("Helvetica", 12, "bold"),
            fg_color=self.colors["entry_bg"],
            text_color=self.colors["text"],
            border_color=self.colors["accent"],
        )
        min_entry.pack(side="left", padx=(0, 5))
        min_entry.insert(0, str(config_value[0]))

        ctk.CTkLabel(
            input_frame,
            text=" - ",
            font=("Helvetica", 12, "bold"),
            text_color=self.colors["text"],
        ).pack(side="left", padx=5)

        max_entry = ctk.CTkEntry(
            input_frame,
            width=width,
            font=("Helvetica", 12, "bold"),
            fg_color=self.colors["entry_bg"],
            text_color=self.colors["text"],
            border_color=self.colors["accent"],
        )
        max_entry.pack(side="left", padx=(5, 0))
        max_entry.insert(0, str(config_value[1]))

        return min_entry, max_entry

    def create_single_input(self, parent, label, config_value, width=300):
        frame = ctk.CTkFrame(parent, fg_color=self.colors["frame_bg"])
        frame.pack(fill="x", pady=5)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame,
            text=f"{label}:",
            width=200,
            anchor="w",
            font=("Helvetica", 12, "bold"),
            text_color=self.colors["text"],
        ).grid(row=0, column=0, padx=(10, 10), sticky="w")

        entry = ctk.CTkEntry(
            frame,
            width=width,
            font=("Helvetica", 12, "bold"),
            fg_color=self.colors["entry_bg"],
            text_color=self.colors["text"],
            border_color=self.colors["accent"],
        )
        entry.grid(row=0, column=1, padx=(0, 10), sticky="e")
        entry.insert(0, str(config_value))

        return entry

    def create_section(self, parent, title):
        frame = ctk.CTkFrame(parent, fg_color=self.colors["frame_bg"])
        frame.pack(fill="x", padx=5, pady=5)

        label = ctk.CTkLabel(
            frame,
            text=title,
            font=("Helvetica", 14, "bold"),
            text_color=self.colors["accent"],
        )
        label.pack(anchor="w", padx=10, pady=10)

        return frame

    def create_category_header(self, parent, title):
        header = ctk.CTkLabel(
            parent,
            text=title,
            font=("Helvetica", 18, "bold"),
            text_color=self.colors["accent"],
        )
        header.pack(fill="x", pady=(20, 10), padx=5)

    def create_widgets(self):
        # General Settings Category
        self.create_category_header(self.scrollable_frame, "⚙️ SETTINGS")
        settings = self.create_section(self.scrollable_frame, "SETTINGS")

        self.threads_entry = self.create_single_input(
            settings,
            "THREADS",
            self.config["SETTINGS"]["THREADS"],
            width=self.input_sizes["tiny"],
        )
        self.attempts_entry = self.create_single_input(
            settings,
            "ATTEMPTS",
            self.config["SETTINGS"]["ATTEMPTS"],
            width=self.input_sizes["tiny"],
        )
        self.acc_range_start, self.acc_range_end = self.create_range_inputs(
            settings,
            "ACCOUNTS_RANGE",
            self.config["SETTINGS"]["ACCOUNTS_RANGE"],
            width=self.input_sizes["tiny"],
        )

        # Add EXACT_ACCOUNTS_TO_USE
        self.exact_accounts = self.create_single_input(
            settings,
            "EXACT_ACCOUNTS_TO_USE",
            ", ".join(map(str, self.config["SETTINGS"]["EXACT_ACCOUNTS_TO_USE"])),
            width=self.input_sizes["large"],
        )

        self.pause_attempts_min, self.pause_attempts_max = self.create_range_inputs(
            settings,
            "PAUSE_BETWEEN_ATTEMPTS",
            self.config["SETTINGS"]["PAUSE_BETWEEN_ATTEMPTS"],
            width=self.input_sizes["small"],
        )
        self.pause_swaps_min, self.pause_swaps_max = self.create_range_inputs(
            settings,
            "PAUSE_BETWEEN_SWAPS",
            self.config["SETTINGS"]["PAUSE_BETWEEN_SWAPS"],
            width=self.input_sizes["small"],
        )
        self.pause_accounts_min, self.pause_accounts_max = self.create_range_inputs(
            settings,
            "RANDOM_PAUSE_BETWEEN_ACCOUNTS",
            self.config["SETTINGS"]["RANDOM_PAUSE_BETWEEN_ACCOUNTS"],
            width=self.input_sizes["small"],
        )
        self.pause_actions_min, self.pause_actions_max = self.create_range_inputs(
            settings,
            "RANDOM_PAUSE_BETWEEN_ACTIONS",
            self.config["SETTINGS"]["RANDOM_PAUSE_BETWEEN_ACTIONS"],
            width=self.input_sizes["small"],
        )
        self.init_pause_min, self.init_pause_max = self.create_range_inputs(
            settings,
            "RANDOM_INITIALIZATION_PAUSE",
            self.config["SETTINGS"]["RANDOM_INITIALIZATION_PAUSE"],
            width=self.input_sizes["small"],
        )

        # Add Telegram settings
        self.telegram_ids = self.create_single_input(
            settings,
            "TELEGRAM_USERS_IDS",
            ", ".join(map(str, self.config["SETTINGS"]["TELEGRAM_USERS_IDS"])),
            width=self.input_sizes["large"],
        )
        self.telegram_token = self.create_single_input(
            settings,
            "TELEGRAM_BOT_TOKEN",
            self.config["SETTINGS"]["TELEGRAM_BOT_TOKEN"],
            width=self.input_sizes["extra_large"],
        )

        # Add new settings fields
        self.send_telegram_logs = ctk.CTkCheckBox(
            settings,
            text="SEND_TELEGRAM_LOGS",
            font=("Helvetica", 12, "bold"),
            text_color=self.colors["text"],
            fg_color=self.colors["accent"],
            hover_color=self.colors["hover"],
        )
        self.send_telegram_logs.pack(padx=10, pady=5, anchor="w")
        (
            self.send_telegram_logs.select()
            if self.config["SETTINGS"]["SEND_TELEGRAM_LOGS"]
            else self.send_telegram_logs.deselect()
        )

        self.shuffle_wallets = ctk.CTkCheckBox(
            settings,
            text="SHUFFLE_WALLETS",
            font=("Helvetica", 12, "bold"),
            text_color=self.colors["text"],
            fg_color=self.colors["accent"],
            hover_color=self.colors["hover"],
        )
        self.shuffle_wallets.pack(padx=10, pady=5, anchor="w")
        (
            self.shuffle_wallets.select()
            if self.config["SETTINGS"].get("SHUFFLE_WALLETS", True)
            else self.shuffle_wallets.deselect()
        )

        # Flow Category
        self.create_category_header(self.scrollable_frame, "🔄 FLOW")
        flow = self.create_section(self.scrollable_frame, "FLOW")

        self.skip_failed_tasks = ctk.CTkCheckBox(
            flow,
            text="SKIP_FAILED_TASKS",
            font=("Helvetica", 12, "bold"),
            text_color=self.colors["text"],
            fg_color=self.colors["accent"],
            hover_color=self.colors["hover"],
        )
        self.skip_failed_tasks.pack(padx=10, pady=5, anchor="w")
        (
            self.skip_failed_tasks.select()
            if self.config["FLOW"]["SKIP_FAILED_TASKS"]
            else self.skip_failed_tasks.deselect()
        )

        # Hub 0G Swaps Category
        self.create_category_header(self.scrollable_frame, "💱 HUB 0G SWAPS")
        swaps = self.create_section(self.scrollable_frame, "HUB_0G_SWAPS")

        self.balance_percent_min, self.balance_percent_max = self.create_range_inputs(
            swaps,
            "BALANCE_PERCENT_TO_SWAP",
            self.config["HUB_0G_SWAPS"]["BALANCE_PERCENT_TO_SWAP"],
            width=self.input_sizes["tiny"],
        )

        self.number_of_swaps_min, self.number_of_swaps_max = self.create_range_inputs(
            swaps,
            "NUMBER_OF_SWAPS",
            self.config["HUB_0G_SWAPS"]["NUMBER_OF_SWAPS"],
            width=self.input_sizes["tiny"],
        )

        # Captcha Category
        self.create_category_header(self.scrollable_frame, "🤖 CAPTCHA")
        captcha = self.create_section(self.scrollable_frame, "CAPTCHA")

        self.nocaptcha_api_key = self.create_single_input(
            captcha,
            "NOCAPTCHA_API_KEY",
            self.config["CAPTCHA"]["NOCAPTCHA_API_KEY"],
            width=self.input_sizes["extra_large"],
        )

        # RPCs Category
        self.create_category_header(self.scrollable_frame, "🌐 RPCS")
        rpcs = self.create_section(self.scrollable_frame, "RPCS")

        self.zerog_rpcs = self.create_single_input(
            rpcs,
            "ZEROG",
            ", ".join(self.config["RPCS"]["ZEROG"]),
            width=self.input_sizes["extra_large"],
        )

        # Others Category
        self.create_category_header(self.scrollable_frame, "⚡ OTHERS")
        others = self.create_section(self.scrollable_frame, "OTHERS")

        self.skip_ssl = ctk.CTkCheckBox(
            others,
            text="SKIP_SSL_VERIFICATION",
            font=("Helvetica", 12, "bold"),
            text_color=self.colors["text"],
            fg_color=self.colors["accent"],
            hover_color=self.colors["hover"],
        )
        self.skip_ssl.pack(padx=10, pady=5, anchor="w")
        (
            self.skip_ssl.select()
            if self.config["OTHERS"]["SKIP_SSL_VERIFICATION"]
            else self.skip_ssl.deselect()
        )

        self.use_proxy = ctk.CTkCheckBox(
            others,
            text="USE_PROXY_FOR_RPC",
            font=("Helvetica", 12, "bold"),
            text_color=self.colors["text"],
            fg_color=self.colors["accent"],
            hover_color=self.colors["hover"],
        )
        self.use_proxy.pack(padx=10, pady=5, anchor="w")
        (
            self.use_proxy.select()
            if self.config["OTHERS"]["USE_PROXY_FOR_RPC"]
            else self.use_proxy.deselect()
        )

    def _save_and_close(self):
        """Save config and close the window"""
        self.save_config()
        self.root.destroy()

    def save_config(self):
        # Update config dictionary with new values
        # SETTINGS
        self.config["SETTINGS"]["THREADS"] = int(self.threads_entry.get())
        self.config["SETTINGS"]["ATTEMPTS"] = int(self.attempts_entry.get())
        self.config["SETTINGS"]["ACCOUNTS_RANGE"] = [
            int(self.acc_range_start.get()),
            int(self.acc_range_end.get()),
        ]

        # Add new SETTINGS fields
        self.config["SETTINGS"]["EXACT_ACCOUNTS_TO_USE"] = [
            int(x.strip()) for x in self.exact_accounts.get().split(",") if x.strip()
        ]

        # Паузы в секундах (целые числа)
        self.config["SETTINGS"]["PAUSE_BETWEEN_ATTEMPTS"] = [
            int(float(self.pause_attempts_min.get())),
            int(float(self.pause_attempts_max.get())),
        ]
        self.config["SETTINGS"]["PAUSE_BETWEEN_SWAPS"] = [
            int(float(self.pause_swaps_min.get())),
            int(float(self.pause_swaps_max.get())),
        ]
        self.config["SETTINGS"]["RANDOM_PAUSE_BETWEEN_ACCOUNTS"] = [
            int(float(self.pause_accounts_min.get())),
            int(float(self.pause_accounts_max.get())),
        ]
        self.config["SETTINGS"]["RANDOM_PAUSE_BETWEEN_ACTIONS"] = [
            int(float(self.pause_actions_min.get())),
            int(float(self.pause_actions_max.get())),
        ]
        self.config["SETTINGS"]["RANDOM_INITIALIZATION_PAUSE"] = [
            int(float(self.init_pause_min.get())),
            int(float(self.init_pause_max.get())),
        ]

        self.config["SETTINGS"]["TELEGRAM_USERS_IDS"] = [
            int(x.strip()) for x in self.telegram_ids.get().split(",") if x.strip()
        ]
        self.config["SETTINGS"]["TELEGRAM_BOT_TOKEN"] = self.telegram_token.get()

        # Add new settings
        self.config["SETTINGS"]["SEND_TELEGRAM_LOGS"] = self.send_telegram_logs.get()
        self.config["SETTINGS"]["SHUFFLE_WALLETS"] = self.shuffle_wallets.get()

        # Flow settings
        self.config["FLOW"]["SKIP_FAILED_TASKS"] = self.skip_failed_tasks.get()

        # Hub 0G Swaps settings
        self.config["HUB_0G_SWAPS"]["BALANCE_PERCENT_TO_SWAP"] = [
            int(self.balance_percent_min.get()),
            int(self.balance_percent_max.get()),
        ]
        self.config["HUB_0G_SWAPS"]["NUMBER_OF_SWAPS"] = [
            int(self.number_of_swaps_min.get()),
            int(self.number_of_swaps_max.get()),
        ]

        # Captcha settings
        self.config["CAPTCHA"]["NOCAPTCHA_API_KEY"] = self.nocaptcha_api_key.get()

        # RPCs settings
        self.config["RPCS"]["ZEROG"] = [
            x.strip() for x in self.zerog_rpcs.get().split(",") if x.strip()
        ]

        # Others settings
        self.config["OTHERS"]["SKIP_SSL_VERIFICATION"] = bool(self.skip_ssl.get())
        self.config["OTHERS"]["USE_PROXY_FOR_RPC"] = bool(self.use_proxy.get())

        # Save to file with improved formatting
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
        with open(config_path, "w") as file:
            yaml.dump(self.config, file, default_flow_style=False, sort_keys=False)

    def run(self):
        """Run the configuration UI"""
        self.root.mainloop()
