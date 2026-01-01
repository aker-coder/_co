import sys

# 定義指令類型常數
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
    def __init__(self, input_file):
        with open(input_file, 'r') as f:
            self.lines = f.readlines()
        self.current_command = ""
        self.current_line_index = -1

    def hasMoreLines(self):
        return self.current_line_index < len(self.lines) - 1

    def advance(self):
        self.current_line_index += 1
        line = self.lines[self.current_line_index]
        # 移除註解與前後空白
        line = line.split('//')[0].strip()
        if not line: # 如果是空行，繼續讀下一行
            if self.hasMoreLines():
                self.advance()
            else:
                self.current_command = ""
        else:
            self.current_command = line

    def commandType(self):
        cmd = self.current_command.split(' ')[0]
        if cmd in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
            return C_ARITHMETIC
        elif cmd == 'push': return C_PUSH
        elif cmd == 'pop': return C_POP
        elif cmd == 'label': return C_LABEL
        elif cmd == 'goto': return C_GOTO
        elif cmd == 'if-goto': return C_IF
        elif cmd == 'function': return C_FUNCTION
        elif cmd == 'return': return C_RETURN
        elif cmd == 'call': return C_CALL
        else: return None

    def arg1(self):
        if self.commandType() == C_ARITHMETIC:
            return self.current_command.split(' ')[0]
        return self.current_command.split(' ')[1]

    def arg2(self):
        split_cmd = self.current_command.split(' ')
        if len(split_cmd) > 2:
            return int(split_cmd[2])
        return 0