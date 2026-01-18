# Universal GBA Pokedex

<img width="869" height="780" alt="image" src="https://github.com/user-attachments/assets/379517a8-f88f-447b-8f25-b9dff2c3eb03" />

A heuristic-based ROM analysis tool designed to extract and visualize Pokémon evolution data from Game Boy Advance ROMs.

Unlike traditional editors that rely on hardcoded memory offsets for specific game versions, this tool utilizes a byte-signature scanning algorithm. This allows it to dynamically locate data tables (Names, Evolutions, and Items) across different regions, versions, and extensive ROM hacks without manual configuration.

## Key Features

* **Dynamic Offset Detection:** Uses pattern matching to locate internal data structures, making it compatible with FireRed, LeafGreen, Emerald, and modified engines (e.g., CFRU).
* **Recursive Evolution Mapping:** Generates complete evolution trees (e.g., Charmander → Charmeleon → Charizard) rather than single-step data.
* **Data Integrity Filtering:** Implements consistency checks to filter out "Bad Egg" data, empty slots, and memory garbage often found in expanded ROMs.
* **Fuzzy Search & Normalization:** Handles character encoding differences and special formatting (e.g., "Mr. Mime" vs "Mr Mime") automatically.

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
