import sys

# 定義指令類型的常數 (Constants)
# 這樣做比直接用字串判斷更安全，也能配合課本的 API 設計
C_ARITHMETIC = 0
C_PUSH = 1
C_POP = 2
C_LABEL = 3
C_GOTO = 4
C_IF = 5
C_FUNCTION = 6
C_RETURN = 7
C_CALL = 8

class Parser:
    """
    負責讀取 .vm 檔案，解析每一行指令，並提供存取其組成的介面。
    """

    def __init__(self, input_file):
        """
        開啟檔案並讀取所有內容。
        為了簡化處理，我們會在初始化時就先把所有註解和空白行濾掉，
        只留下乾淨的指令列表。
        """
        self.commands = []
        self.current_command = ""
        self.current_index = -1

        try:
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                # 1. 去除註解 (// 之後的內容)
                line = line.split('//')[0]
                # 2. 去除前後空白
                line = line.strip()
                # 3. 如果不是空行，就加入指令列表
                if line:
                    self.commands.append(line)
                    
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found.")
            sys.exit(1)

    def has_more_commands(self):
        """還有更多指令嗎？"""
        # 檢查目前的索引是否還沒指到最後一行
        return (self.current_index + 1) < len(self.commands)

    def advance(self):
        """
        讀取下一個指令，並設為當前指令。
        呼叫前應先確認 has_more_commands() 為 True。
        """
        self.current_index += 1
        self.current_command = self.commands[self.current_index]

    def command_type(self):
        """
        回傳當前指令的類型。
        """
        # 將指令以空白切割，取第一個字 (例如 "push", "add", "goto")
        tokens = self.current_command.split()
        cmd = tokens[0]

        arithmetic_cmds = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']

        if cmd in arithmetic_cmds:
            return C_ARITHMETIC
        elif cmd == 'push':
            return C_PUSH
        elif cmd == 'pop':
            return C_POP
        elif cmd == 'label':
            return C_LABEL
        elif cmd == 'goto':
            return C_GOTO
        elif cmd == 'if-goto':
            return C_IF
        elif cmd == 'function':
            return C_FUNCTION
        elif cmd == 'return':
            return C_RETURN
        elif cmd == 'call':
            return C_CALL
        else:
            # 為了除錯，如果遇到不認識的指令可以報錯
            raise ValueError(f"Unknown command type: {cmd}")

    def arg1(self):
        """
        回傳當前指令的第一個參數。
        如果是 C_ARITHMETIC，則回傳指令本身 (例如 "add")。
        """
        tokens = self.current_command.split()
        ctype = self.command_type()

        if ctype == C_ARITHMETIC:
            return tokens[0]  # 例如 "add"
        elif ctype == C_RETURN:
            return None       # return 指令沒有參數
        else:
            return tokens[1]  # 例如 "push constant 5" -> 回傳 "constant"

    def arg2(self):
        """
        回傳當前指令的第二個參數 (整數)。
        只有 C_PUSH, C_POP, C_FUNCTION, C_CALL 會用到這個。
        """
        tokens = self.current_command.split()
        return int(tokens[2]) # 例如 "push constant 5" -> 回傳 5