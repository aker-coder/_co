class SymbolTable:
    def __init__(self):
        # 類別級別符號表 (Static, Field)
        self.class_table = {} 
        # 函式級別符號表 (Arg, Var)
        self.subroutine_table = {}
        # 索引計數器
        self.counts = {'STATIC': 0, 'FIELD': 0, 'ARG': 0, 'VAR': 0}

    def start_subroutine(self):
        """開始編譯新的函式時呼叫，重置函式級別的表"""
        self.subroutine_table.clear()
        self.counts['ARG'] = 0
        self.counts['VAR'] = 0

    def define(self, name, type, kind):
        """將變數加入符號表"""
        # kind: STATIC, FIELD, ARG, VAR
        if kind in ['STATIC', 'FIELD']:
            index = self.counts[kind]
            self.class_table[name] = {'type': type, 'kind': kind, 'index': index}
            self.counts[kind] += 1
        elif kind in ['ARG', 'VAR']:
            index = self.counts[kind]
            self.subroutine_table[name] = {'type': type, 'kind': kind, 'index': index}
            self.counts[kind] += 1

    def var_count(self, kind):
        """回傳該種類變數目前的數量"""
        return self.counts.get(kind, 0)

    def kind_of(self, name):
        """回傳變數種類 (STATIC, FIELD, ARG, VAR, NONE)"""
        if name in self.subroutine_table:
            return self.subroutine_table[name]['kind']
        elif name in self.class_table:
            return self.class_table[name]['kind']
        return None

    def type_of(self, name):
        """回傳變數型別"""
        if name in self.subroutine_table:
            return self.subroutine_table[name]['type']
        elif name in self.class_table:
            return self.class_table[name]['type']
        return None

    def index_of(self, name):
        """回傳變數索引"""
        if name in self.subroutine_table:
            return self.subroutine_table[name]['index']
        elif name in self.class_table:
            return self.class_table[name]['index']
        return None