import re

class JackTokenizer:
    # Jack 語言的關鍵字列表
    KEYWORDS = {
        'class', 'constructor', 'function', 'method', 'field', 'static', 'var',
        'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this',
        'let', 'do', 'if', 'else', 'while', 'return'
    }
    
    # 符號集合
    SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}
    
    # XML 轉義對照表 (第11章其實用不到，但留著無妨)
    XML_ENTITY = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}

    def __init__(self, input_file):
        with open(input_file, 'r') as f:
            content = f.read()
        
        self.tokens = self._tokenize(content)
        self.current_token_idx = 0
        self.current_token = None # (Type, Value)

    def _tokenize(self, content):
        # 1. 移除註解
        # 修正：改成 /\*.*?\*/ 以同時匹配 /** doc */ 和 /* block comment */
        content = re.sub(r'/\*.*?\*/', ' ', content, flags=re.DOTALL) 
        content = re.sub(r'//.*', ' ', content)
        
        # 2. Regex 定義
        kws = '|'.join(re.escape(k) for k in self.KEYWORDS)
        keyword_regex = r'(?P<KEYWORD>(' + kws + r')(?!\w))'
        
        symbol_regex = r'(?P<SYMBOL>[' + re.escape(''.join(self.SYMBOLS)) + r'])'
        int_regex = r'(?P<INT_CONST>\d+)'
        string_regex = r'(?P<STRING_CONST>"[^"\n]*")'
        id_regex = r'(?P<IDENTIFIER>[a-zA-Z_]\w*)'

        regex = '|'.join([keyword_regex, symbol_regex, int_regex, string_regex, id_regex])
        
        tokens = []
        for match in re.finditer(regex, content):
            if match.lastgroup:
                token_type = match.lastgroup
                token_val = match.group(token_type)
                
                if token_type == 'STRING_CONST':
                    tokens.append(('STRING_CONST', token_val[1:-1]))
                elif token_type == 'INT_CONST':
                    tokens.append(('INT_CONST', token_val))
                elif token_type == 'KEYWORD':
                    tokens.append(('KEYWORD', token_val))
                else:
                    tokens.append((token_type, token_val))
                    
        return tokens

    def hasMoreTokens(self):
        return self.current_token_idx < len(self.tokens)

    def advance(self):
        if self.hasMoreTokens():
            self.current_token = self.tokens[self.current_token_idx]
            self.current_token_idx += 1

    # --- API 方法 (注意命名與回傳值) ---

    def tokenType(self):
        return self.current_token[0]

    # 重要修正：改為 camelCase 並回傳大寫，以符合 CompilationEngine 的判斷
    def keyWord(self):
        if self.current_token[0] == 'KEYWORD':
            return self.current_token[1].upper() # 轉成大寫！
        return self.current_token[1]

    def symbol(self):
        return self.current_token[1]

    def identifier(self):
        return self.current_token[1]

    def intVal(self):
        return self.current_token[1]

    def stringVal(self):
        return self.current_token[1]
    
    def peek(self):
        if self.current_token_idx < len(self.tokens):
            return self.tokens[self.current_token_idx]
        return None