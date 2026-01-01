class CodeWriter:
    def __init__(self, output_file):
        """
        開啟輸出檔案，並準備進行寫入。
        """
        self.output_file = open(output_file, 'w')
        self.file_name = ""  # 用於 static 變數 (例如 FileName.0)
        self.label_count = 0 # 用於產生唯一的比較指令 Label

    def set_file_name(self, file_name):
        """
        通知 CodeWriter 現在正在處理哪個 VM 檔。
        這對於 static 變數的命名至關重要。
        """
        self.file_name = file_name

    def write_arithmetic(self, command):
        """
        將算術/邏輯 VM 指令轉譯成 Hack Assembly。
        command: 字串 (例如 "add", "sub", "eq"...)
        """
        # 寫入註解方便除錯
        self.output_file.write(f"// {command}\n")

        if command == "add":
            self._write_binary_op("+")
        elif command == "sub":
            self._write_binary_op("-")
        elif command == "and":
            self._write_binary_op("&")
        elif command == "or":
            self._write_binary_op("|")
        elif command == "neg":
            self._write_unary_op("-")
        elif command == "not":
            self._write_unary_op("!")
        elif command in ["eq", "gt", "lt"]:
            self._write_compare_op(command)
        else:
            raise ValueError(f"Unknown command: {command}")

    def write_push_pop(self, command, segment, index):
        """
        處理 push 或 pop 指令。
        command: "push" 或 "pop"
        segment: "constant", "local", "argument", "this", "that", ...
        index: 整數
        """
        self.output_file.write(f"// {command} {segment} {index}\n")

        if command == "push":
            if segment == "constant":
                # push constant i
                # D = i, *SP = D, SP++
                asm_code = f"""
                @{index}
                D=A
                @SP
                A=M
                M=D
                @SP
                M=M+1
                """
                self._write_asm(asm_code)
            
            elif segment in ["local", "argument", "this", "that"]:
                # 這裡要實作 push segment i
                # Address = Base + index
                self._write_push_from_segment(segment, index)
            
            # ... 處理 temp, pointer, static ...

        elif command == "pop":
            if segment in ["local", "argument", "this", "that"]:
                # 這裡要實作 pop segment i
                self._write_pop_to_segment(segment, index)
            
            # ... 處理 temp, pointer, static ...

    def close(self):
        """關閉輸出檔案"""
        self.output_file.close()

    # --- 輔助函式 (Helper Methods) ---

    def _write_asm(self, code):
        """輔助函式：去除縮排並寫入檔案"""
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        for line in lines:
            self.output_file.write(line + '\n')

    def _write_binary_op(self, op):
        """處理 add, sub, and, or"""
        # 邏輯：SP--, D = y, SP--, M = x op y, SP++
        # 優化後：
        asm_code = f"""
        @SP
        AM=M-1
        D=M
        A=A-1
        M=M{op}D
        """
        self._write_asm(asm_code)

    def _write_unary_op(self, op):
        """處理 neg, not"""
        # 邏輯：直接修改堆疊頂端的值
        asm_code = f"""
        @SP
        A=M-1
        M={op}M
        """
        self._write_asm(asm_code)

    def _write_compare_op(self, command):
        """處理 eq, gt, lt (最難的部分)"""
        # 邏輯：x - y，根據結果跳轉
        label_true = f"TRUE_{self.label_count}"
        label_end = f"END_{self.label_count}"
        self.label_count += 1
        
        if command == "eq": jump_cmd = "JEQ"
        elif command == "gt": jump_cmd = "JGT"
        elif command == "lt": jump_cmd = "JLT"

        asm_code = f"""
        @SP
        AM=M-1
        D=M
        A=A-1
        D=M-D
        @{label_true}
        D;{jump_cmd}
        @SP
        A=M-1
        M=0
        @{label_end}
        0;JMP
        ({label_true})
        @SP
        A=M-1
        M=-1
        ({label_end})
        """
        self._write_asm(asm_code)

    def _write_pop_to_segment(self, segment, index):
        """處理 pop local/argument/this/that"""
        # 對應表
        seg_map = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
        base_label = seg_map[segment]

        # 邏輯：
        # 1. 計算目標位址 (Base + index) 存入 R13
        # 2. SP--, 取得值存入 D
        # 3. 將 D 存入 *R13
        asm_code = f"""
        @{index}
        D=A
        @{base_label}
        D=M+D
        @R13
        M=D
        @SP
        AM=M-1
        D=M
        @R13
        A=M
        M=D
        """
        self._write_asm(asm_code)
        
    def _write_push_from_segment(self, segment, index):
        """處理 push local/argument/this/that"""
        # 這裡留給你練習填空
        # 邏輯：
        # 1. 計算來源位址 (Base + index)
        seg_map = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
        # 2. 讀取該位址的值到 D
        base_label = seg_map[segment]
        asm_code = f"""
        @{index}
        D=A
        @{base_label}
        A=M+D
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        """
        # 3. 將 D push 到堆疊
        self._write_asm(asm_code)