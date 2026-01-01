import os

class CodeWriter:
    def __init__(self, output_file):
        self.output_file = open(output_file, 'w')
        self.file_name = ""  # 當前處理的 .vm 檔名 (用於 static 變數)
        self.function_name = "Sys.init" # 當前處理的函式名 (用於 label scope)
        self.label_count = 0 # 用於生成唯一標籤 (如 EQ_TRUE_1)
        self.call_count = 0  # 用於生成唯一的回傳地址標籤

    def setFileName(self, file_name):
        """通知 CodeWriter 目前正在處理哪個檔案"""
        self.file_name = file_name

    def writeInit(self):
        """Chapter 8: 寫入 Bootstrap code"""
        # TODO: 
        # 1. @256, D=A, @SP, M=D (初始化 SP)
        # 2. 呼叫 writeCall('Sys.init', 0)
        self._write_asm([
            "@256",
            "D=A",
            "@SP",
            "M=D"
        ])
        self.writeCall("Sys.init", 0)
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

    def writeArithmetic(self, command):
        """Chapter 7: 算術邏輯 (沿用你之前的代碼)"""
        # self._write_asm(...)
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
        pass
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

    def writePushPop(self, command, segment, index):
        """
        處理 push 或 pop 指令。
        支援所有記憶體區段：constant, local, argument, this, that, pointer, temp, static
        """
        # 1. 統一指令名稱 (解決 1 != "push" 的問題)
        cmd_str = ""
        if command == 1 or command == "push":
            cmd_str = "push"
        elif command == 2 or command == "pop":
            cmd_str = "pop"
            
        self.output_file.write(f"// {cmd_str} {segment} {index}\n")

        if cmd_str == "push":
            if segment == "constant":
                # push constant i
                asm_code = f"@{index}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1"
                self._write_asm(asm_code)
            
            elif segment in ["local", "argument", "this", "that"]:
                self._write_push_from_segment(segment, index)

            elif segment == "temp":
                # push temp i (RAM[5+i])
                asm_code = f"@{5 + index}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1"
                self._write_asm(asm_code)

            elif segment == "pointer":
                # push pointer 0/1 (0 -> THIS, 1 -> THAT)
                label = "THIS" if index == 0 else "THAT"
                asm_code = f"@{label}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1"
                self._write_asm(asm_code)

            elif segment == "static":
                # push static i (FileName.i)
                static_label = f"{self.file_name}.{index}"
                asm_code = f"@{static_label}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1"
                self._write_asm(asm_code)
        
        elif cmd_str == "pop":
            if segment in ["local", "argument", "this", "that"]:
                self._write_pop_to_segment(segment, index)

            elif segment == "temp":
                # pop temp i (存入 RAM[5+i])
                # 邏輯：addr = 5+i, SP--, *addr = *SP
                asm_code = f"""
                @SP
                AM=M-1
                D=M
                @{5 + index}
                M=D
                """
                self._write_asm(asm_code)

            elif segment == "pointer":
                # pop pointer 0/1
                label = "THIS" if index == 0 else "THAT"
                asm_code = f"""
                @SP
                AM=M-1
                D=M
                @{label}
                M=D
                """
                self._write_asm(asm_code)

            elif segment == "static":
                # pop static i
                static_label = f"{self.file_name}.{index}"
                asm_code = f"""
                @SP
                AM=M-1
                D=M
                @{static_label}
                M=D
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

    # ================= Chapter 8 新增區域 =================

    def writeLabel(self, label):
        """
        處理 label command
        格式: (functionName$label)
        """
        full_label = f"{self.function_name}${label}"
        self._write_asm([f"({full_label})"])

    def writeGoto(self, label):
        """
        處理 goto command
        格式: @functionName$label, 0;JMP
        """
        full_label = f"{self.function_name}${label}"
        self._write_asm([
            f"@{full_label}",
            "0;JMP"
        ])

    def writeIf(self, label):
        """
        處理 if-goto command
        邏輯: Pop stack -> D. If D != 0 jump to label.
        """
        full_label = f"{self.function_name}${label}"
        self._write_asm([
            "@SP", "AM=M-1", "D=M", # Pop top to D
            f"@{full_label}",
            "D;JNE" # Jump if D != 0
        ])

    def writeFunction(self, function_name, num_locals):
        """
        處理 function command
        1. 宣告 (functionName) 標籤
        2. push 0 到堆疊 num_locals 次
        """
        self.function_name = function_name
        # TODO: 實作 function 邏輯
        self._write_asm([f"({function_name})"])
        for _ in range(num_locals):
            self._write_asm([
                "@0",
                "D=A",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ])
        pass

    def writeReturn(self):
        """
        處理 return command
        依據規格書恢復 FRAME, RET, SP, THAT, THIS, ARG, LCL
        """
        # TODO: 實作 return 邏輯
        # FRAME = LCL
        self._write_asm([
            "@LCL",
            "D=M",
            "@R13",  # R13 作為 FRAME 暫存器
            "M=D"
        ])
        # RET = *(FRAME - 5)
        self._write_asm([
            "@5",
            "A=D-A",
            "D=M",
            "@R14",  # R14 作為 RET 暫存器
            "M=D"
        ])
        # *ARG = pop()
        self._write_asm([
            "@SP",
            "AM=M-1",
            "D=M",
            "@ARG",
            "A=M",
            "M=D"
        ])
        # SP = ARG + 1
        self._write_asm([
            "@ARG",
            "D=M+1",
            "@SP",
            "M=D"
        ])
        # THAT = *(FRAME - 1)
        self._write_asm([
            "@R13",
            "AM=M-1",
            "D=M",
            "@THAT",
            "M=D"
        ])
        # THIS = *(FRAME - 2)
        self._write_asm([
            "@R13",
            "AM=M-1",
            "D=M",
            "@THIS",
            "M=D"
        ])
        # ARG = *(FRAME - 3)
        self._write_asm([
            "@R13",
            "AM=M-1",
            "D=M",
            "@ARG",
            "M=D"
        ])
        # LCL = *(FRAME - 4)
        self._write_asm([
            "@R13",
            "AM=M-1",
            "D=M",
            "@LCL",
            "M=D"
        ])
        # goto RET
        self._write_asm([
            "@R14",
            "A=M",
            "0;JMP"
        ])

    def writeCall(self, function_name, num_args):
        """
        處理 call command
        保存狀態 (Push ret, LCL, ARG, THIS, THAT) -> 調整 ARG/LCL -> goto -> 宣告 (ret)
        """
        return_label = f"{self.function_name}$ret.{self.call_count}"
        self.call_count += 1
        
        # TODO: 實作 call 邏輯
        self._write_asm([
            # Push return address
            f"@{return_label}",
            "D=A",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            # Push LCL
            "@LCL",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            # Push ARG
            "@ARG",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            # Push THIS
            "@THIS",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            # Push THAT
            "@THAT",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            # Reposition ARG (ARG = SP - n - 5)
            "@SP",
            "D=M",
            f"@{num_args + 5}",
            "D=D-A",
            "@ARG",
            "M=D",
            # Reposition LCL (LCL = SP)
            "@SP",
            "D=M",
            "@LCL",
            "M=D",
            # Goto function
            f"@{function_name}",
            "0;JMP",
            # Declare return label
            f"({return_label})"
        ])
        pass

    # ================= 輔助函式 =================

    def _write_asm(self, commands):
        # 如果傳進來的是單純的字串 (多行 f-string)，先幫它切開並去除空白
        if isinstance(commands, str):
            lines = commands.strip().split('\n')
            for line in lines:
                clean_line = line.strip()
                if clean_line: # 避免寫入空行
                    self.output_file.write(clean_line + '\n')
        # 如果傳進來的是列表 (List)
        else:
            for cmd in commands:
                self.output_file.write(cmd + '\n')

    def close(self):
        self.output_file.close()