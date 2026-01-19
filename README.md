# Universal GBA Pokedex

<p align="center">
  <img src="https://github.com/user-attachments/assets/9c1a8bda-12fb-455f-b8e4-ae017142a930" width="800" alt="Main Interface Dark Mode">
  <br>
  <em>Modern Dark Mode Interface with Syntax Highlighting</em>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/fd59a5d1-ceb9-4de2-b638-b07d197a2429" width="400" alt="Recursive Evolution Tree">
  <img src="https://github.com/user-attachments/assets/994e410d-b12a-45d3-8af3-47a6e62060f4" width="400" alt="Item Detection">
  <br>
  <em>Left: Recursive Evolution Trees (Eevee) | Right: Automatic Item Name Detection</em>
</p>




A heuristic-based ROM analysis tool designed to extract and visualize Pokémon evolution data from Game Boy Advance ROMs.

Unlike traditional editors that rely on hardcoded memory offsets for specific game versions, this tool utilizes a byte-signature scanning algorithm. This allows it to dynamically locate data tables (Names, Evolutions, and Items) across different regions, versions, and extensive ROM hacks without manual configuration.


## Key Features

* **Universal Compatibility:** Automatically detects data offsets for FireRed, Emerald, and many ROM Hacks.
* **Recursive Evolution Engine:** Visualizes the entire evolutionary lineage (e.g., Bulbasaur → Ivysaur → Venusaur) in a single view.
* **Heuristic Item Scanner:** Uses structure-based pattern matching to detect Item Tables even in heavily modified game engines.
* **Modern Dark UI:** Features a professional, VS Code-inspired interface with resizable panels and syntax highlighting.
* **Gap Logic:** Intelligent handling of empty data slots to prevent offset shifting in expanded Pokedexes.

## Verified Compatibility

The tool has been tested and verified on the following:
* **Official Titles:** Pokémon FireRed (US/EU), Pokémon LeafGreen (US/EU), Pokémon Emerald (US).
* **ROM Hacks:** Compatible with standard FireRed-based hacks. (Support for Expanded Dex hacks like Radical Red is currently experimental).

## Installation & Usage

### Option A: Standalone Application (Windows)
For users who do not wish to run Python scripts:
1.  Navigate to the **Releases** section on the right-hand side of this repository.
2.  Download the latest `UniversalPokedex.exe`.
3.  Launch the application and select **"Load GBA ROM"**.

### Option B: Running from Source
Requirements: Python 3.x (Tkinter is included with standard Python installations).

1.  Clone the repository:
    ```bash
    git clone [https://github.com/TheJazz123/Universal-GBA-Pokedex.git](https://github.com/TheJazz123/Universal-GBA-Pokedex.git)
    cd Universal-GBA-Pokedex
    ```

2.  Run the application:
    ```bash
    python pokedex_app.py
    ```

## Technical Overview

The core logic resides in `gba_utils.py`. The scanner performs the following operations:
1.  **Signature Search:** Scans the ROM binary for byte patterns characteristic of Gen 3 data tables.
2.  **Score-Based Validation:** Candidates for data tables are scored based on valid ASCII character frequency and pointer logic.
3.  **Self-Alignment:** Once a table is found, the script calculates the offset of specific anchor entries (e.g., "Mew" or "Treecko") to realign the index to 0.
4.  **Garbage Collection:** A post-processing pass analyzes the Evolution Method IDs. If a sequence of mathematically invalid IDs is detected (indicating the end of the table), the scanner terminates to prevent reading adjacent game data as Pokémon.

## Built With

* **Python 3.13** - Core logic and data processing.
* **Tkinter** - Standard Python GUI framework.
* **PyInstaller** - Used to compile the standalone Windows executable.

## Disclaimer

This project is a research tool intended for educational purposes only.

* **No ROMs Included:** This repository does not contain any game files, ROM images, or copyrighted assets.
* **Affiliation:** This project is not affiliated with, endorsed by, or connected to Nintendo, Game Freak, or The Pokémon Company in any way.
* **Usage:** Users are responsible for ensuring they possess the legal right to modify and analyze their own game backups in accordance with their local laws.

## Acknowledgments

* **Hex Maniac Advance:** An essential tool used to verify memory offsets and validate the scanner's results.
* **The ROM Hacking Community:** For years of documentation on the Game Boy Advance data structures that made this tool possible.
