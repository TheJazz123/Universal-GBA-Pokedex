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

def decode_gba_string(bytes_data):
    result = ""
    for b in bytes_data:
        if b == 0xFF: break
        result += GBA_MAP.get(b, "?")
    return result

class GbaRomScanner:
    def __init__(self, data):
        self.data = data
        self.detected_stride = 11  # Default stride for Gen 3 names

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

    def find_name_table(self):
        start_search = 0x10000 
        best_table_score = -99999
        best_offset = -1
        
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
                                self.detected_stride = stride
                            i += (entry_count * stride)
                            found_table = True
                            break
                if not found_table: i += 1
            else:
                i += 1

        if best_offset != -1:
            name_table_start = best_offset
            raw_first = self.data[name_table_start : name_table_start + self.detected_stride - 1]
            first_name = decode_gba_string(raw_first).strip().lower()

            if first_name == "mew": name_table_start -= (150 * self.detected_stride)
            elif first_name == "chikorita": name_table_start -= (151 * self.detected_stride)
            elif first_name == "nidorino": name_table_start -= (32 * self.detected_stride)
            elif first_name == "treecko": name_table_start -= (276 * self.detected_stride)
            
            return name_table_start
        return None

    def find_evo_table(self):
        evo_table_start = -1
        # Signature 1: Bulbasaur (Level 16 -> Ivysaur)
        p_std = b'\x04\x00\x10\x00\x02\x00\x00\x00'
        off = self.find_offset(p_std)
        if off != -1: evo_table_start = off
        
        if evo_table_start == -1:
            # Signature 2: Treecko (Level 16 -> Grovyle)
            p_treecko = b'\x04\x00\x10\x00\x16\x01\x00\x00'
            off = self.find_offset(p_treecko)
            if off != -1: evo_table_start = off - (276 * 40)
            
        if evo_table_start == -1:
             # Signature 3: Pichu (Friendship -> Pikachu)
            p_pichu = b'\x01\x00\x00\x00\x19\x00\x00\x00'
            off = self.find_offset(p_pichu)
            if off != -1: evo_table_start = off - (171 * 40)
            
        return evo_table_start

    def find_item_table(self):
        """
        FORENSIC SCANNER: Based on user provided hex.
        Target: "MASTER" (Caps) or "Master" (Standard).
        Stride: 44 Bytes (Confirmed).
        """
        
        # PATTERN 1: "MASTER" (All Caps) - Matches your ROM
        # Hex: C7(M) BB(A) CD(S) CE(T) BF(E) CC(R)
        master_caps = b'\xC7\xBB\xCD\xCE\xBF\xCC'
        
        # PATTERN 2: "Master" (Standard FireRed)
        # Hex: C7(M) D5(a) E7(s) E8(t) D9(e) E6(r)
        master_std = b'\xC7\xD5\xE7\xE8\xD9\xE6'

        # PATTERN 3: "ULTRA" (Verification for Caps)
        # Hex: CF(U) C6(L) CE(T) CC(R) BB(A)
        ultra_caps = b'\xCF\xC6\xCE\xCC\xBB'

        # PATTERN 4: "Ultra" (Verification for Std)
        # Hex: CF(U) E0(l) E8(t) E6(r) D5(a)
        ultra_std = b'\xCF\xE0\xE8\xE6\xD5'

        start = 0
        while True:
            # Look for "MASTER" (Caps) OR "Master" (Std)
            off_caps = self.data.find(master_caps, start)
            off_std = self.data.find(master_std, start)
            
            # Find the earliest occurrence
            if off_caps == -1 and off_std == -1: break
            
            if off_caps != -1 and (off_std == -1 or off_caps < off_std):
                current_off = off_caps
                is_caps = True
            else:
                current_off = off_std
                is_caps = False
            
            # CHECK: Is "ULTRA" (or "Ultra") exactly 44 bytes later?
            check_loc = current_off + 44
            
            if is_caps:
                # If we found MASTER, look for ULTRA
                if self.data[check_loc : check_loc + len(ultra_caps)] == ultra_caps:
                    return current_off - 44 # Found Item 1, return Item 0 location
            else:
                # If we found Master, look for Ultra
                if self.data[check_loc : check_loc + len(ultra_std)] == ultra_std:
                    return current_off - 44

            start = current_off + 1

        return None

    def read_item_name(self, table_start, item_id):
        if table_start is None: return f"Item {item_id}"
        offset = table_start + (item_id * 44)
        if offset + 14 > len(self.data): return f"Item {item_id}"
        raw_name = self.data[offset : offset + 14]
        return decode_gba_string(raw_name).strip()

    def extract_all_data(self, name_table_start):
        evo_table_start = self.find_evo_table()
        if evo_table_start == -1: return []

        # STEP 1: Build a Map of {ID -> Name} first.
        # This fixes the "Gap" issue. We store the name at its REAL ID.
        id_to_name = {}
        
        for i in range(1, 1200):
            # CALCULATE OFFSETS
            name_offset = name_table_start + ((i - 1) * self.detected_stride)
            if name_offset < 0 or name_offset + self.detected_stride > len(self.data): break

            # READ NAME
            raw_name = self.data[name_offset : name_offset + self.detected_stride - 1]
            name = decode_gba_string(raw_name).strip()
            
            # --- GARBAGE / BOUNDARY CHECK ---
            # If we are past Chimecho (ID 411) and hit garbage/moves, stop.
            if i > 411:
                # Common Move names that might appear if we overshoot:
                # Pound (CD D9 E9 E2 D8), Karate Chop...
                # If name looks weird or empty, stop.
                if not name or name.startswith("?") or len(name) < 3:
                    break
                # Extra check: If it looks like a Move (Move table usually follows Pokemon), stop.
                # Heuristic: If we see 5 moves in a row, we assume we hit the Move Table.
                # For safety in this version, let's HARD STOP at 412 for Gen 3 standard.
                # If you want Radical Red support later, we can increase this cap.
                if i > 412: 
                    break

            # Store in map (even if it's "?????", we might need it for index alignment)
            if name and not name.startswith("?"):
                id_to_name[i] = name
            else:
                id_to_name[i] = f"Unknown ({i})"

        # STEP 2: Build the final list using the Map for lookups
        final_data = []
        
        # Iterate only through the valid IDs we found
        sorted_ids = sorted(id_to_name.keys())
        
        for i in sorted_ids:
            name = id_to_name[i]
            
            # Skip the "Gap" entries (252-276) for the UI list
            # But we KEPT them in id_to_name so lookups work!
            if "Unknown (" in name:
                continue

            evo_offset = evo_table_start + ((i - 1) * 40)
            my_evos = []
            
            for slot in range(5):
                slot_offset = evo_offset + (slot * 8)
                if slot_offset + 8 > len(self.data): break
                entry = self.data[slot_offset : slot_offset + 8]
                method_id, param, target_id, _ = struct.unpack('<HHHH', entry)
                
                if method_id > 50: break # Corrupted/Garbage check

                if method_id != 0 and target_id != 0:
                    # KEY FIX: Look up target_id in the MAP, not a list index
                    target_name = id_to_name.get(target_id, f"#{target_id}")
                    
                    my_evos.append({
                        "target": target_name,
                        "method": method_id,
                        "param": param
                    })

            final_data.append((name, {"evolutions": my_evos}))
            
        return final_data