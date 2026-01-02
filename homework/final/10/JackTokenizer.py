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
    
    # XML 轉義對照表
    XML_ENTITY = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}

    def __init__(self, input_file):
        with open(input_file, 'r') as f:
            content = f.read()
        
        self.tokens = self._tokenize(content)
        self.current_token_idx = 0
        self.current_token = None # (Type, Value)

    def _tokenize(self, content):
        # 1. 移除註解
        content = re.sub(r'/\*\*.*?\*/', ' ', content, flags=re.DOTALL) 
        content = re.sub(r'//.*', ' ', content)
        
        # 2. 定義 Token 的 Regex (修正：移除外層多餘括號，並分開定義以增加可讀性)
        # 關鍵字：使用 \b 邊界或 (?!\w) 確保不會匹配到變數的前綴 (如 classVar)
        # 這裡我們用 re.escape 確保安全，雖然關鍵字都是英文
        kws = '|'.join(re.escape(k) for k in self.KEYWORDS)
        keyword_regex = r'(?P<KEYWORD>(' + kws + r')(?!\w))'
        
        symbol_regex = r'(?P<SYMBOL>[' + re.escape(''.join(self.SYMBOLS)) + r'])'
        int_regex = r'(?P<INT_CONST>\d+)'
        string_regex = r'(?P<STRING_CONST>"[^"\n]*")'
        id_regex = r'(?P<IDENTIFIER>[a-zA-Z_]\w*)'

        # 將所有規則用 | (OR) 連接起來
        regex = '|'.join([keyword_regex, symbol_regex, int_regex, string_regex, id_regex])
        
        tokens = []
        for match in re.finditer(regex, content):
            # 安全檢查：確保 lastgroup 存在
            if match.lastgroup:
                token_type = match.lastgroup
                token_val = match.group(token_type)
                
                if token_type == 'STRING_CONST':
                    # 去除字串前後的引號: "Hello" -> Hello
                    tokens.append(('STRING_CONST', token_val[1:-1]))
                elif token_type == 'INT_CONST':
                    tokens.append(('INT_CONST', token_val))
                elif token_type == 'KEYWORD':
                    # 因為我們的 regex 結構是 ((k1|k2..)(?!\w))，group 抓到的可能會包含 lookahead 的部分(雖然 lookahead 不佔字元)
                    # 為了保險，我們只取單字部分，但通常 token_val 就已經正確了
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

    # 以下是用於獲取當前 token 資訊的 API
    def tokenType(self):
        return self.current_token[0]

    def keyword(self):
        return self.current_token[1]

    def symbol(self):
        return self.current_token[1]

    def identifier(self):
        return self.current_token[1]

    def intVal(self):
        return self.current_token[1]

    def stringVal(self):
        return self.current_token[1]
    
    # 輔助：偷看下一個 Token (用於 LL(2) 分析，如區分變數與陣列)
    def peek(self):
        if self.current_token_idx < len(self.tokens):
            return self.tokens[self.current_token_idx]
        return None