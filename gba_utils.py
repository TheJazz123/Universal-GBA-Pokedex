import struct

# --- 1. CONFIGURATION ---
GBA_MAP = {
    0x00: " ", 
    0xA1: "0", 0xA2: "1", 0xA3: "2", 0xA4: "3", 0xA5: "4", 
    0xA6: "5", 0xA7: "6", 0xA8: "7", 0xA9: "8", 0xAA: "9", 
    0xAB: "!", 0xAC: "?", 0xAD: ".", 0xAE: "-", 0xAF: "·",
    0xB0: "...", 0xB1: "«", 0xB2: "»", 0xB3: "'", 0xB4: "'", 
    0xB5: "♂", 0xB6: "♀", 
    0xB7: ":", 0xB8: ",", 0xB9: "k", 0xBA: "/", 
    0xBB: "A", 0xBC: "B", 0xBD: "C", 0xBE: "D", 0xBF: "E", 0xC0: "F", 0xC1: "G",
    0xC2: "H", 0xC3: "I", 0xC4: "J", 0xC5: "K", 0xC6: "L", 0xC7: "M", 0xC8: "N",
    0xC9: "O", 0xCA: "P", 0xCB: "Q", 0xCC: "R", 0xCD: "S", 0xCE: "T", 0xCF: "U",
    0xD0: "V", 0xD1: "W", 0xD2: "X", 0xD3: "Y", 0xD4: "Z",
    0xD5: "a", 0xD6: "b", 0xD7: "c", 0xD8: "d", 0xD9: "e", 0xDA: "f", 0xDB: "g",
    0xDC: "h", 0xDD: "i", 0xDE: "j", 0xDF: "k", 0xE0: "l", 0xE1: "m", 0xE2: "n",
    0xE3: "o", 0xE4: "p", 0xE5: "q", 0xE6: "r", 0xE7: "s", 0xE8: "t", 0xE9: "u",
    0xEA: "v", 0xEB: "w", 0xEC: "x", 0xED: "y", 0xEE: "z", 0xFF: ""
}

ITEM_MAP = {
    0x5D: "Sun Stone", 0x5E: "Moon Stone", 0x5F: "Fire Stone", 0x60: "Thunder Stone",
    0x61: "Water Stone", 0x62: "Leaf Stone", 0x6F: "Up-Grade", 0xC6: "Deep Sea Tooth",
    0xC7: "Deep Sea Scale", 0xC8: "Dragon Scale", 0xC9: "Metal Coat", 0xFE: "Red Scarf"
}

EVO_METHODS = {
    1: "Friendship", 2: "Friendship (Day)", 3: "Friendship (Night)", 4: "Level",
    5: "Trade", 6: "Trade (Hold Item)", 7: "Stone", 8: "Atk > Def", 9: "Atk = Def",
    10: "Def > Atk", 11: "Personality", 12: "Personality", 13: "Ninjask Slot", 14: "Shedinja Slot", 15: "Beauty"
}

def decode_gba_string(bytes_data):
    result = ""
    for b in bytes_data:
        if b == 0xFF: break
        result += GBA_MAP.get(b, "?")
    return result

class GBAReader:
    def __init__(self, file_path):
        self.path = file_path
        with open(file_path, 'rb') as f:
            self.data = f.read()

    def find_offset(self, pattern, start_index=0):
        return self.data.find(pattern, start_index)

    def score_entry(self, offset, stride):
        if offset + stride > len(self.data): return -9999
        score = 0
        first_byte = self.data[offset]
        if 0xBB <= first_byte <= 0xD4: score += 10
        elif 0xD5 <= first_byte <= 0xEE: return -9999
        else: return -9999
        check_data = self.data[offset+1 : offset+stride]
        has_terminator = False
        for b in check_data:
            if b == 0xFF: 
                has_terminator = True
                break
            if b == 0x00: score -= 5 
            if not ((0xA1 <= b <= 0xAC) or (0xBB <= b <= 0xEE)): score -= 20
        if not has_terminator: return -9999
        return score

    def extract_rom_data(self, manual_name_offset=None, manual_evo_offset=None):
        pokedex = {}
        name_table_start = -1
        evo_table_start = -1
        detected_stride = 11

        if manual_name_offset:
            try: name_table_start = int(manual_name_offset, 16)
            except: return {"error": "Invalid Name Offset"}
        if manual_evo_offset:
            try: evo_table_start = int(manual_evo_offset, 16)
            except: return {"error": "Invalid Evo Offset"}

        # --- THE MASTER SCANNER ---
        if name_table_start == -1:
            start_search = 0x10000 
            best_table_score = -99999
            best_offset = -1
            best_stride = 11
            
            i = start_search
            while i < len(self.data) - 5000:
                if 0xBB <= self.data[i] <= 0xD4:
                    found_table = False
                    for stride in range(10, 15):
                        if (self.score_entry(i, stride) > 0 and 
                            self.score_entry(i+stride, stride) > 0 and 
                            self.score_entry(i+(2*stride), stride) > 0):
                            
                            total_score = 0
                            entry_count = 0
                            for k in range(50):
                                s = self.score_entry(i + (k*stride), stride)
                                if s == -9999: break 
                                total_score += s
                                entry_count += 1
                            
                            if entry_count >= 20:
                                total_score += (entry_count * 10)
                                if total_score > best_table_score:
                                    best_table_score = total_score
                                    best_offset = i
                                    best_stride = stride
                                i += (entry_count * stride)
                                found_table = True
                                break
                    if not found_table: i += 1
                else:
                    i += 1

            if best_offset != -1:
                name_table_start = best_offset
                detected_stride = best_stride
                
                # Realignment
                raw_first = self.data[name_table_start : name_table_start + detected_stride - 1]
                first_name = decode_gba_string(raw_first).strip().lower()

                if first_name == "mew": name_table_start -= (150 * detected_stride)
                elif first_name == "chikorita": name_table_start -= (151 * detected_stride)
                elif first_name == "nidorino": name_table_start -= (32 * detected_stride)
                elif first_name == "treecko": name_table_start -= (276 * detected_stride)
            else:
                return {"error": "No valid Pokemon table found."}

        if evo_table_start == -1:
            p_std = b'\x04\x00\x10\x00\x02\x00\x00\x00'
            off = self.find_offset(p_std)
            if off != -1: evo_table_start = off
            if evo_table_start == -1:
                p_treecko = b'\x04\x00\x10\x00\x16\x01\x00\x00'
                off = self.find_offset(p_treecko)
                if off != -1: evo_table_start = off - 11040 
            if evo_table_start == -1:
                p_pichu = b'\x01\x00\x00\x00\x19\x00\x00\x00'
                off = self.find_offset(p_pichu)
                if off != -1: evo_table_start = off - 6840

        if evo_table_start == -1: return {"error": "Could not detect Evo Table."}
        
        # --- SCAN LOOP ---
        for i in range(1, 1200): 
            name_offset = name_table_start + ((i - 1) * detected_stride)
            if name_offset < 0: name = f"Gen1_Miss_{i}"
            elif name_offset + detected_stride > len(self.data): break
            else:
                raw_name = self.data[name_offset : name_offset + detected_stride - 1]
                name = decode_gba_string(raw_name).strip()
            
            if not name or name == "?" or name.startswith("????"):
                name = f"Unknown_ID_{i}"
            
            evo_offset = evo_table_start + ((i - 1) * 40)
            my_evos = []
            
            # TRACK INVALID EVOS TO DETECT END OF TABLE
            has_insane_evo_data = False
            
            for slot in range(5):
                slot_offset = evo_offset + (slot * 8)
                if slot_offset + 8 > len(self.data): break
                entry = self.data[slot_offset : slot_offset + 8]
                method_id, param, target_id, _ = struct.unpack('<HHHH', entry)
                
                # DATA CONSISTENCY CHECK
                # If method_id > 50, we are definitely reading garbage/code, not an Evo Table.
                if method_id > 50:
                    has_insane_evo_data = True

                if method_id != 0 and target_id != 0:
                    method_name = EVO_METHODS.get(method_id, f"Method {method_id}")
                    if method_id == 7 or method_id == 6:
                        method_name = "Use" if method_id == 7 else method_name
                        param = ITEM_MAP.get(param, f"Item {param}")
                    my_evos.append({"method": method_name, "param": str(param), "target_id": target_id})

            # Store the raw "sanity" status in the dictionary for the cleanup loop
            pokedex[i] = {"name": name.title(), "evos": my_evos, "is_corrupted": has_insane_evo_data}

        # --- FINAL CLEANUP ---
        final_dex = {}
        consecutive_junk = 0 
        
        for pid, data in pokedex.items():
            name = data['name']
            
            if 252 <= pid <= 276: continue

            if pid > 411:
                is_junk = False
                
                # Check 1: Name looks like garbage (symbols, too short)
                if "Unknown_ID" in name or "!" in name or "?" in name or "." in name or "," in name or len(name) < 3:
                    is_junk = True
                
                # Check 2: The Evolution Data was mathematically impossible (e.g. Method #34021)
                # This catches Move Names (which look valid) but have garbage Evo data
                if data["is_corrupted"]:
                    is_junk = True
                
                if is_junk:
                    consecutive_junk += 1
                else:
                    consecutive_junk = 0
                
                if consecutive_junk >= 5: # If we hit 5 rows of garbage/moves, STOP.
                    break
                
                if is_junk: continue

            if "Unknown_ID" in name: continue
            if name.startswith("?") or name == "?????": continue
            if len(name) > 12: continue

            clean_evos = []
            for evo in data['evos']:
                target_data = pokedex.get(evo['target_id'])
                if not target_data or "Unknown_ID" in target_data['name']: continue
                if 252 <= evo['target_id'] <= 276: continue
                target_name = target_data['name']
                clean_evos.append({"target": target_name, "method": evo['method'], "param": evo['param']})
            
            final_dex[pid] = {'name': name, 'evos': clean_evos}
            
        return final_dex