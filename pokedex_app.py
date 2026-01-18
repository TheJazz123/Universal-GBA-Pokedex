import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import gba_utils

class PokedexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal GBA Pokedex v1.3 - Recursive Tree")
        self.root.geometry("1000x700")
        
        # --- THEME CONFIGURATION ---
        self.colors = {
            "bg_main":     "#1e1e1e",
            "bg_sidebar":  "#252526",
            "fg_text":     "#d4d4d4",
            "fg_header":   "#569cd6",  # Blue
            "accent":      "#007acc",  # Bright Blue
            "evo_arrow":   "#c586c0",  # Pink/Purple for arrows
            "method_txt":  "#6a9955",  # Green for methods
        }
        
        self.configure_styles()
        self.create_widgets()
        
        self.scanner = None
        self.rom_data = None
        self.item_table_offset = None
        
        # Fast Lookup Map for Recursion
        self.name_to_data = {} 

    def configure_styles(self):
        self.root.configure(bg=self.colors["bg_main"])
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TFrame", background=self.colors["bg_main"])
        style.configure("Sidebar.TFrame", background=self.colors["bg_sidebar"])
        style.configure("TLabel", background=self.colors["bg_main"], foreground=self.colors["fg_text"], font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground=self.colors["fg_header"])
        
        style.configure("Treeview", 
                        background=self.colors["bg_sidebar"],
                        foreground=self.colors["fg_text"],
                        fieldbackground=self.colors["bg_sidebar"],
                        borderwidth=0,
                        font=("Segoe UI", 10),
                        rowheight=24)
        style.map("Treeview", background=[('selected', self.colors["accent"])], foreground=[('selected', 'white')])
        
        style.configure("Treeview.Heading", background="#333333", foreground="white", relief="flat")
        style.configure("Vertical.TScrollbar", gripcount=0, background="#333333", troughcolor=self.colors["bg_sidebar"], borderwidth=0)

    def create_widgets(self):
        # Toolbar
        toolbar = ttk.Frame(self.root, padding="10 10 10 5")
        toolbar.pack(fill=tk.X)
        self.load_btn = tk.Button(toolbar, text="📂 Load ROM", command=self.load_rom, 
                                  bg=self.colors["accent"], fg="white", relief="flat", padx=10, pady=5)
        self.load_btn.pack(side=tk.LEFT)

        # Main Layout
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # LEFT PANEL
        left_panel = ttk.Frame(self.paned_window, style="Sidebar.TFrame", padding=2)
        self.paned_window.add(left_panel, weight=1)
        
        # Search
        search_frame = ttk.Frame(left_panel, style="Sidebar.TFrame", padding="5")
        search_frame.pack(fill=tk.X)
        tk.Label(search_frame, text="SEARCH", bg=self.colors["bg_sidebar"], fg="#888888", font=("Segoe UI", 8, "bold")).pack(anchor=tk.W)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_list)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                                     bg="#3c3c3c", fg="white", insertbackground="white", relief="flat")
        self.search_entry.pack(fill=tk.X, pady=(2, 5), ipady=4)
        
        # List
        list_frame = ttk.Frame(left_panel, style="Sidebar.TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(list_frame, columns=("ID", "Name"), show="headings", selectmode="browse")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Pokemon Name")
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=180, anchor="w")
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # RIGHT PANEL
        right_panel = ttk.Frame(self.paned_window, padding="10 0 0 0")
        self.paned_window.add(right_panel, weight=3)
        
        self.header_label = ttk.Label(right_panel, text="Select a Pokemon", style="Header.TLabel", font=("Segoe UI", 24, "bold"))
        self.header_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.details_text = tk.Text(right_panel, wrap=tk.WORD, 
                                    bg=self.colors["bg_main"], fg=self.colors["fg_text"], 
                                    relief="flat", font=("Consolas", 11),
                                    padx=10, pady=10, highlightthickness=0)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Text Tags
        self.details_text.tag_config("evo_header", foreground=self.colors["fg_header"], font=("Segoe UI", 14, "bold"))
        self.details_text.tag_config("arrow", foreground=self.colors["evo_arrow"], font=("Consolas", 14, "bold"))
        self.details_text.tag_config("target", foreground="white", font=("Segoe UI", 12, "bold"))
        self.details_text.tag_config("method", foreground=self.colors["method_txt"], font=("Segoe UI", 10, "italic"))

        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self.root, textvariable=self.status_var, bg=self.colors["accent"], fg="white", font=("Segoe UI", 9), pady=4).pack(side=tk.BOTTOM, fill=tk.X)

    def load_rom(self):
        filename = filedialog.askopenfilename(filetypes=[("GBA ROMs", "*.gba"), ("All Files", "*.*")])
        if not filename: return

        try:
            with open(filename, "rb") as f:
                data = f.read()
            
            self.scanner = gba_utils.GbaRomScanner(data)
            self.status_var.set("Scanning ROM data...")
            self.root.update_idletasks()
            
            name_table = self.scanner.find_name_table()
            self.item_table_offset = self.scanner.find_item_table()
            
            if name_table:
                self.rom_data = self.scanner.extract_all_data(name_table)
                # Create Lookup Map for Recursion
                self.name_to_data = {name: entry for name, entry in self.rom_data}
                
                self.update_list(self.rom_data)
                
                msg = f"✓ Loaded {len(self.rom_data)} Pokemon"
                msg += " | Items Detected" if self.item_table_offset else ""
                self.status_var.set(msg)
            else:
                messagebox.showerror("Scan Error", "Could not find Pokemon Data.")
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_list(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, (name, _) in enumerate(data):
            self.tree.insert("", tk.END, iid=i, values=(f"{i+1:03d}", name))

    def filter_list(self, *args):
        search_term = self.search_var.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, (name, _) in enumerate(self.rom_data):
            if search_term in name.lower():
                self.tree.insert("", tk.END, iid=i, values=(f"{i+1:03d}", name))

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection: return
        index = int(selection[0])
        name, entry = self.rom_data[index]
        self.header_label.config(text=f"#{index+1:03d} {name}")
        self.show_details(name, entry)

    def show_details(self, name, entry):
        self.details_text.configure(state='normal')
        self.details_text.delete(1.0, tk.END)
        
        self.details_text.insert(tk.END, "Evolution Lineage:\n\n", "evo_header")
        
        # Start Recursion
        # We pass a 'visited' set to prevent infinite loops (e.g., if a hack makes A evolve into B and B into A)
        self.print_recursive_evolution(name, depth=0, visited=set())
        
        self.details_text.configure(state='disabled')

    def print_recursive_evolution(self, pokemon_name, depth, visited):
        """
        Recursive function to print the full tree.
        """
        # Indentation based on depth
        indent = "      " * depth
        
        # Stop infinite loops
        if pokemon_name in visited:
            return
        visited.add(pokemon_name)

        # Fetch Data
        entry = self.name_to_data.get(pokemon_name)
        if not entry: return

        # Get Evolutions
        evolutions = entry.get('evolutions', [])
        
        if not evolutions and depth > 0:
            # Leaf node (Final Evolution)
            # We already printed the arrow to get here, so we do nothing extra
            pass

        for i, evo in enumerate(evolutions):
            target_name = evo['target']
            method_id = evo['method']
            param = evo['param']
            method_str = self.get_method_string(method_id, param)

            # Draw Tree Branch
            # If depth 0 (Root), we just print children.
            # If depth > 0, we are inside a branch.
            
            self.details_text.insert(tk.END, f"{indent} ➜ ", "arrow")
            self.details_text.insert(tk.END, f"{target_name}\n", "target")
            self.details_text.insert(tk.END, f"{indent}     [{method_str}]\n\n", "method")
            
            # RECURSE: Call function for the child
            self.print_recursive_evolution(target_name, depth + 1, visited.copy())

    def get_method_string(self, method_id, param):
        methods = {
            1: "Friendship (High)", 2: "Friendship (Day)", 3: "Friendship (Night)",
            4: f"Level {param}", 5: "Trade", 6: "Trade (Hold Item)",
            7: "Use Item", 8: "Level (Atk > Def)", 9: "Level (Atk = Def)",
            10: "Level (Def > Atk)", 11: "Level (Personality High)", 12: "Level (Personality Low)",
            13: "Level (Ninjask Slot)", 14: "Level (Beauty)",
            15: "Use Item (Male)", 16: "Use Item (Female)",
        }
        base = methods.get(method_id, f"Unknown ({method_id})")
        
        if method_id in [6, 7, 15, 16]:
            item = self.resolve_item_name(param)
            return f"Trade holding {item}" if method_id == 6 else f"Use {item}"
        return base

    def resolve_item_name(self, item_id):
        if self.scanner and self.item_table_offset:
            return self.scanner.read_item_name(self.item_table_offset, item_id)
        return f"Item {item_id}"

if __name__ == "__main__":
    root = tk.Tk()
    app = PokedexApp(root)
    root.mainloop()