# Nand2Tetris Project 10: Jack Compiler (Syntax Analysis)

這是我在 **Nand2Tetris (From Nand to Tetris)** 課程中，針對第 10 章：**編譯器 I：語法分析 (Compiler I: Syntax Analysis)** 所實作的專案。

本專案是用 **Python** 撰寫的，目標是將高階的 Jack 語言 (`.jack`) 進行詞法分析與語法分析，並輸出符合課程定義的 XML 格式語法樹 (Parse Tree)。這是構建完整編譯器（第 11 章）的前端基礎。

## 📂 專案結構 (File Structure)

本編譯器由三個主要模組組成：

* **`JackAnalyzer.py`** (入口程式)
    * 主程式驅動器。
    * 負責接收命令列參數（檔案或目錄）。
    * 建立 `JackTokenizer` 和 `CompilationEngine` 實例並串聯運作。

* **`JackTokenizer.py`** (詞法分析器 / Lexer)
    * 負責讀取 `.jack` 原始碼。
    * 移除所有註解 (`//`, `/** */`) 和多餘空白。
    * 將程式碼切分為最小單位的 **Tokens** (`Keyword`, `Symbol`, `Identifier`, `IntConstant`, `StringConstant`)。
    * **實作細節**：使用 Python 強大的 `re` (Regular Expression) 模組進行模式匹配。

* **`CompilationEngine.py`** (語法分析器 / Parser)
    * 核心邏輯所在。
    * 接收 Tokenizer 產出的 Tokens。
    * 使用 **遞迴下降分析法 (Recursive Descent Parsing)** 驗證語法結構。
    * 輸出階層化的 XML 標籤（如 `<class>`, `<whileStatement>`, `<term>`）。

## 🚀 快速開始 (Usage)

### 環境需求
* Python 3.6 或以上版本。

### 執行方式
你可以針對單一檔案或整個目錄進行編譯：

```bash
# 編譯單一檔案
python JackAnalyzer.py MyProgram.jack

# 編譯整個目錄 (會自動尋找目錄下所有的 .jack 檔)
python JackAnalyzer.py ./ArrayTest/
```

**輸出結果**
程式執行後，會在相同目錄下產生同名的 .xml 檔案：
* 輸入：`Main.jack`
* 輸出：`Main.xml` (完整的語法樹 XML)

## 🛠️ 實作細節 (Implementation Details)
1. **詞法分析 (Tokenizer)**
為了高效處理字串，我避免了手寫狀態機 (State Machine)，而是利用 **正規表達式 (Regex)** 的群組功能：

* **註解處理**：使用 `re.sub` 優先處理 `/** ... */` 區塊註解，再處理 `//` 行內註解，確保程式碼乾淨。

* **Token 識別**：使用 `(?P<GROUP_NAME>pattern)` 語法定義五種 Token 類型，並透過 `re.finditer` 一次性掃描所有 Tokens。

* **特殊字元XML 實體轉換**：XML 輸出時，自動將 `<`、`>`、`&`、`"` 轉換為對應的實體代碼 (Entity Code，如 `&lt;`)。

2. **語法分析 (Parser)**
採用標準的 **遞迴下降 (Recursive Descent)** 架構。每個非終端符號 (Non-terminal) 對應一個 Python 方法（例如 `compileClass`, `compileLet`）。

**關鍵技術挑戰與解決方案**：

* **LL(2) Lookahead (預讀兩步)**：
    在處理 `compileTerm` 時，單看一個 Identifier 無法判斷是變數、陣列還是函式呼叫。

* **解決方案**：實作 `tokenizer.peek()` 方法偷看下一個 Token。
    * 若下一個是 `[` $\rightarrow$ 陣列存取 (`arr[i]`)。
    * 若下一個是 `(` 或 `.`$\rightarrow$ 函式呼叫 (`func()` 或 `Class.method()`)。
    * 否則 $\rightarrow$ 單純變數。

* **運算式優先級 (Expression Priority)**：
    Jack 語言的運算子結合律較簡單，遵循 `term (op term)*` 的結構。
    * **實作**：在 `compileExpression` 中使用 `while` 迴圈持續吞噬運算子與隨後的 Term，確保平行的運算結構正確反映在 XML 樹狀圖中。

* **結構化輸出**：
為了確保 XML 縮排正確，Engine 內部維護了一個 `indent_level` 變數，隨著遞迴深度自動增減縮排空格。

## 🧪 測試與驗證 (Testing)
本專案已通過 Nand2Tetris 提供的標準測試集：
1. **ArrayTest**: 測試基本的陣列操作與變數宣告。

2. **Square**: 測試類別、方法呼叫與繪圖指令。

3. **ExpressionLessSquare**: 測試控制流結構（省略複雜運算式）。

**驗證方法**：
使用課程提供的 `TextComparer` 工具比對產出的 `.xml` 與標準答案：
```Bash
# Windows 範例
../../tools/TextComparer.bat ArrayTest/Main.xml ArrayTest/Main.xml
# 比對結果應為：Comparison ended successfully
```

## 📝 開發心得 (Notes)
* Regex 的威力：Python 的 `re` 模組極大地簡化了 Tokenizer 的程式碼量，從原本可能的上百行縮減為精簡的定義。

* 遞迴思維：編寫 CompilationEngine 時，核心在於完全信任「遞迴函式會正確處理剩下的部分」。只要定義好當前的語法規則，剩下的細節交給遞迴呼叫即可，這讓處理複雜的嵌套結構（如 `if` 內還有 `while`）變得直觀。

## 🔜 下一步 (Next Steps)
目前專案僅完成 **前端 (Front-end) 分析**，產出 XML。
下一階段 (Project 11) 將擴充此專案，將 XML 輸出邏輯替換為 **VM Code Generation**，完成完整的 Jack 語言編譯器。將這邊全部用markdown語法寫給我