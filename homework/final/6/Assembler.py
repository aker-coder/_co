import sys

class Parser:
    """
    負責讀取 .asm 檔案，並將每一行拆解成指令單元。
    """
    def __init__(self, filename):
        # 這裡建議一次把所有行讀進來並做初步清理（去掉空白、換行）
        with open(filename, 'r') as f:
            self.lines = f.readlines()
        
        self.current_instruction = ""
        self.current_line_idx = -1

    def has_more_lines(self):
        """檢查是否還有下一行指令"""
        return self.current_line_idx < len(self.lines) - 1

    def advance(self):
        """
        讀取下一行，並跳過空行和註解。
        目標是讓 self.current_instruction 變成一條乾淨的指令。
        """
        self.current_line_idx += 1
        raw_line = self.lines[self.current_line_idx]
        
        # TODO: 1. 去除註解 (// 之後的內容)
        clean_line = raw_line.split('//')[0]
        # TODO: 2. 去除前後空白 (.strip())
        clean_line = clean_line.strip()
        # TODO: 3. 如果是空行，遞迴呼叫 self.advance() 直到找到有效指令或檔案結束
        if clean_line == "":
            if self.has_more_lines():
                self.advance()
            else:
                self.current_instruction = ""
        else:
            self.current_instruction = clean_line
        
        # self.current_instruction = clean_line 

    def instruction_type(self):
        """
        回傳指令類型:
        - A_INSTRUCTION: @xxx
        - C_INSTRUCTION: D=M+1
        - L_INSTRUCTION: (LOOP)
        """
        # TODO: 判斷 self.current_instruction 的開頭字元
        if self.current_instruction.startswith('@'):
            return 'A_INSTRUCTION'
        elif self.current_instruction.startswith('(') and self.current_instruction.endswith(')'):
            return 'L_INSTRUCTION'
        else:
            return 'C_INSTRUCTION'
        pass

    def symbol(self):
        """
        如果是 @xxx 或 (xxx)，回傳 xxx (字串)。
        如果是數字 @123，則回傳 "123"。
        """
        # TODO: 去掉 @ 或 ()
        if self.instruction_type() == 'A_INSTRUCTION':
            return self.current_instruction[1:]
        elif self.instruction_type() == 'L_INSTRUCTION':
            return self.current_instruction[1:-1]
        pass

    def dest(self):
        """回傳 C 指令的 dest 部分 (如 'D', 'M', 'AD')"""
        # TODO: 如果有 '='，回傳 '=' 左邊的部分；否則回傳 "null"
        if '=' in self.current_instruction:
            return self.current_instruction.split('=')[0]
        return "null"

    def comp(self):
        """回傳 C 指令的 comp 部分 (如 'M+1', '0')"""
        # TODO: 處理 '=' 和 ';' 之間的邏輯，擷取中間運算部分
        comp_part = self.current_instruction
        if '=' in comp_part:
            comp_part = comp_part.split('=')[1]
        if ';' in comp_part:
            comp_part = comp_part.split(';')[0]
        return comp_part

    def jump(self):
        """回傳 C 指令的 jump 部分 (如 'JGT', 'JMP')"""
        # TODO: 如果有 ';', 回傳 ';' 右邊的部分；否則回傳 "null"
        if ';' in self.current_instruction:
            return self.current_instruction.split(';')[1]
        return "null"

class Code:
    """
    提供靜態方法，將組合語言的助記符 (Mnemonic) 轉為二進位碼。
    """
    
    @staticmethod
    def dest(mnemonic):
        """回傳 3 bits 的 dest 二進位碼"""
        # TODO: 建立字典對照表 (e.g., 'D': '010')
        # return table.get(mnemonic, '000')
        table = {
            'null': '000',
            'M': '001',
            'D': '010',
            'MD': '011',
            'A': '100',
            'AM': '101',
            'AD': '110',
            'AMD': '111'
        }
        return table.get(mnemonic, '000')

    @staticmethod
    def comp(mnemonic):
        """回傳 7 bits 的 comp 二進位碼 (包含 a-bit)"""
        # 注意：你需要處理 a=0 和 a=1 的情況
        # 例如: 'D+1' -> a=0, '011111'
        #       'M+1' -> a=1, '111111'
        table = {
            # a = 0 (使用 A 暫存器)
            '0':   '0101010',
            '1':   '0111111',
            '-1':  '0111010',
            'D':   '0001100',
            'A':   '0110000',
            '!D':  '0001101',
            '!A':  '0110001',
            '-D':  '0001111',
            '-A':  '0110011',
            'D+1': '0011111',
            'A+1': '0110111',
            'D-1': '0001110',
            'A-1': '0110010',
            'D+A': '0000010',
            'D-A': '0010011',
            'A-D': '0000111',
            'D&A': '0000000',
            'D|A': '0010101',
            
            # a = 1 (使用 Memory，也就是把上面 A 的部分換成 M)
            'M':   '1110000',
            '!M':  '1110001',
            '-M':  '1110011',
            'M+1': '1110111',
            'M-1': '1110010',
            'D+M': '1000010',
            'D-M': '1010011',
            'M-D': '1000111',
            'D&M': '1000000',
            'D|M': '1010101'
        }
        return table.get(mnemonic, '0000000') # 若找不到回傳 0000000 避免當機

    @staticmethod
    def jump(mnemonic):
        """回傳 3 bits 的 jump 二進位碼"""
        # TODO: 建立字典對照表 (e.g., 'JMP': '111')
        table = {
            'null': '000',
            'JGT': '001',
            'JEQ': '010',
            'JGE': '011',
            'JLT': '100',
            'JNE': '101',
            'JLE': '110',
            'JMP': '111'
        }
        return table.get(mnemonic, '000')

class SymbolTable:
    def __init__(self):
        self.table = {}
        # TODO: 初始化預設符號 (R0~R15, SCREEN, KBD, SP, LCL, ARG, THIS, THAT)
        # 例如: self.table['R0'] = 0
        #      self.table['SCREEN'] = 16384
        for i in range(16):
            self.table[f'R{i}'] = i
        self.table['SP'] = 0
        self.table['LCL'] = 1
        self.table['ARG'] = 2
        self.table['THIS'] = 3
        self.table['THAT'] = 4
        self.table['SCREEN'] = 16384
        self.table['KBD'] = 24576

    def add_entry(self, symbol, address):
        """新增一組 (symbol, address)"""
        self.table[symbol] = address

    def contains(self, symbol):
        """檢查符號是否存在"""
        return symbol in self.table

    def get_address(self, symbol):
        """取得符號對應的位址"""
        return self.table[symbol]

def main():
    if len(sys.argv) != 2:
        print("Usage: python assembler.py Prog.asm")
        return

    input_file = sys.argv[1]
    output_file = input_file.replace('.asm', '.hack')

    symbol_table = SymbolTable()

    # ==========================================
    # 第一遍掃描 (First Pass): 建立符號表
    # ==========================================
    parser = Parser(input_file)
    rom_address = 0

    while parser.has_more_lines():
        parser.advance()
        instr_type = parser.instruction_type()

        if instr_type == 'L_INSTRUCTION': # (LOOP)
            # TODO: 取得標籤名稱，加入 symbol_table，位址為目前的 rom_address
            # 注意：標籤本身不佔用 ROM 空間，所以 rom_address 不用加 1
            label = parser.symbol()
            symbol_table.add_entry(label, rom_address)
            pass
        else:
            # A 指令或 C 指令都佔用 1 行 ROM
            rom_address += 1

    # ==========================================
    # 第二遍掃描 (Second Pass): 翻譯程式碼
    # ==========================================
    parser = Parser(input_file) # 重新建立 Parser 以從頭讀取
    output_lines = []
    
    # 用來分配變數記憶體位址 (從 RAM[16] 開始)
    variable_address = 16 

    while parser.has_more_lines():
        parser.advance()
        instr_type = parser.instruction_type()

        if instr_type == 'A_INSTRUCTION': # @xxx
            symbol = parser.symbol()
            # TODO: 
            # 1. 如果 symbol 是數字 -> 直接轉二進位
            # 2. 如果 symbol 是符號 -> 查表
            #    - 如果表裡沒有，視為新變數，存入表 (位址 = variable_address++)
            # 3. 轉成 16-bit 二進位字串 (開頭補0)
            if symbol.isdigit():
                address = int(symbol)
            else:
                if not symbol_table.contains(symbol):
                    symbol_table.add_entry(symbol, variable_address)
                    variable_address += 1
                address = symbol_table.get_address(symbol)
            binary_string = format(address, '016b')
            output_lines.append(binary_string)

        elif instr_type == 'C_INSTRUCTION': # D=M+1
            # TODO:
            # 1. 呼叫 parser 取得 dest, comp, jump
            # 2. 呼叫 Code 模組轉成二進位
            # 3. 拼湊成 '111' + comp + dest + jump
            dest_mnemonic = parser.dest()
            comp_mnemonic = parser.comp()
            jump_mnemonic = parser.jump()
            binary_string = '111' + Code.comp(comp_mnemonic) + Code.dest(dest_mnemonic) + Code.jump(jump_mnemonic)
            output_lines.append(binary_string)

        elif instr_type == 'L_INSTRUCTION':
            # 第二遍掃描可以直接忽略標籤
            continue
            
        # 將翻譯好的二進位字串加入 output_lines
        # output_lines.append(binary_string)

    # 寫入檔案
    with open(output_file, 'w') as f:
        for line in output_lines:
            f.write(line + '\n')
    
    print(f"Assembly completed! Output: {output_file}")

if __name__ == "__main__":
    main()