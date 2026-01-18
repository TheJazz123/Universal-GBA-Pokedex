import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import gba_utils

class PokedexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal ROM Hack Pokedex")
        self.root.geometry("700x600")

        self.pokedex = {}

        # --- GUI ELEMENTS ---
        self.top_frame = tk.Frame(root, pady=10)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.btn_load = tk.Button(self.top_frame, text="Load GBA ROM", command=self.load_rom, bg="#e1e1e1", width=15)
        self.btn_load.pack(side=tk.LEFT, padx=10)
        
        self.btn_list = tk.Button(self.top_frame, text="Show All Pokemon", command=self.show_full_list, bg="#e1e1e1", width=15)
        self.btn_list.pack(side=tk.LEFT, padx=10)

        self.lbl_status = tk.Label(self.top_frame, text="No ROM Loaded", fg="red")
        self.lbl_status.pack(side=tk.LEFT, padx=10)

        self.search_frame = tk.Frame(root, pady=10)
        self.search_frame.pack(side=tk.TOP, fill=tk.X, padx=10)

        tk.Label(self.search_frame, text="Search Pokemon:").pack(side=tk.LEFT)
        
        self.entry_search = tk.Entry(self.search_frame)
        self.entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entry_search.bind("<Return>", self.search_pokemon)

        self.btn_search = tk.Button(self.search_frame, text="Search", command=self.search_pokemon)
        self.btn_search.pack(side=tk.LEFT)

        self.tree_frame = tk.Frame(root)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("from", "method", "condition", "target")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        
        self.tree.heading("from", text="Pokemon")
        self.tree.heading("method", text="Method")
        self.tree.heading("condition", text="Condition / Item")
        self.tree.heading("target", text="Evolves Into")
        
        self.tree.column("from", width=120)
        self.tree.column("method", width=120)
        self.tree.column("condition", width=150)
        self.tree.column("target", width=120)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_rom(self):
        file_path = filedialog.askopenfilename(filetypes=[("GBA ROMs", "*.gba")])
        if not file_path: return

        self.lbl_status.config(text="Scanning... (Please wait)", fg="orange")
        self.root.update()

        try:
            reader = gba_utils.GBAReader(file_path)
            self.pokedex = reader.extract_rom_data() 
            
            if "error" in self.pokedex:
                self.lbl_status.config(text=f"Error: {self.pokedex['error']}", fg="red")
            else:
                count = len(self.pokedex)
                self.lbl_status.config(text=f"Loaded {count} Pokemon!", fg="green")
        except Exception as e:
            self.lbl_status.config(text="Error loading ROM", fg="red")
            print(e)

    def show_full_list(self):
        if not self.pokedex:
            messagebox.showinfo("Info", "Please load a ROM first.")
            return
            
        top = Toplevel(self.root)
        top.title("Full Pokemon List")
        top.geometry("300x600")
        
        listbox = tk.Listbox(top, font=("Courier", 10))
        scrollbar = tk.Scrollbar(top, orient="vertical", command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        listbox.pack(side="left", fill="both", expand=True)
        
        # Sort by ID (keys are now Integers)
        sorted_pokedex = sorted(self.pokedex.items(), key=lambda item: item[0])
        for pid, data in sorted_pokedex:
            # pid is Int, data is Dict {'name': '...', 'evos': ...}
            listbox.insert("end", f"#{pid:03}: {data['name']}")

    def normalize_name(self, name):
        return name.lower().replace(".", "").replace(" ", "").strip()

    def find_all_evolutions(self, pokemon_name, depth=0, visited=None):
        if visited is None: visited = set()
        if pokemon_name in visited: return []
        visited.add(pokemon_name)

        lookup_name = self.normalize_name(pokemon_name)
        found_data = None
        real_name = pokemon_name
        
        # Iterate over values() since keys are now IDs
        for data in self.pokedex.values():
            if self.normalize_name(data['name']) == lookup_name:
                found_data = data
                real_name = data['name']
                break
        
        if not found_data: return []

        results = []
        for evo in found_data['evos']:
            target = evo['target']
            indent = "  " * depth
            from_display = f"{indent}{real_name}"
            results.append((from_display, evo['method'], evo['param'], target))
            sub_results = self.find_all_evolutions(target, depth + 1, visited)
            results.extend(sub_results)
        return results

    def search_pokemon(self, event=None):
        query = self.entry_search.get().strip()
        if not query: return

        # Normalize Input
        search_term = query.lower()
        search_term = search_term.replace(" female", "♀").replace(" male", "♂")
        search_term = search_term.replace(" f", "♀").replace(" m", "♂")
        search_term_clean = self.normalize_name(search_term)
        
        found_name = None
        
        # Search by Value
        for data in self.pokedex.values():
            if self.normalize_name(data['name']) == search_term_clean:
                found_name = data['name']
                break
        
        if not found_name:
            for data in self.pokedex.values():
                if search_term_clean in self.normalize_name(data['name']):
                    found_name = data['name']
                    break
        
        self.tree.delete(*self.tree.get_children())

        if found_name:
            full_tree = self.find_all_evolutions(found_name)
            if not full_tree:
                self.tree.insert("", "end", values=(found_name, "Fully Evolved", "-", "-"))
            else:
                for row in full_tree:
                    self.tree.insert("", "end", values=row)
        else:
            self.tree.insert("", "end", values=("Not Found", "Check spelling", "-", "-"))

if __name__ == "__main__":
    root = tk.Tk()
    app = PokedexApp(root)
    root.mainloop()