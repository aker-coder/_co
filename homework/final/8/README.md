# Nand2Tetris Project 8: VM Translator (Control & Functions)

這是一個基於 Python 實作的 VM Translator (虛擬機轉譯器)，對應 Nand2Tetris 課程的第 8 章。
本專案擴充了第 7 章的堆疊運算功能，新增了 **流程控制 (Program Flow)** 與 **函式呼叫 (Function Calling)** 的完整支援。

## 🚀 功能特色 (Features)

本轉譯器能夠將 `.vm` 虛擬機代碼轉譯為 Hack Assembly (`.asm`)，支援以下指令：

### 1. 堆疊算術與記憶體存取 (Chapter 7 基礎)
* **算術邏輯**：`add`, `sub`, `neg`, `eq`, `gt`, `lt`, `and`, `or`, `not`
* **記憶體操作**：`push`, `pop`
* **記憶體區段**：`constant`, `local`, `argument`, `this`, `that`, `temp`, `pointer`, `static`

### 2. 流程控制 (Program Flow)
* `label labelName`：定義跳轉標籤。
* `goto labelName`：無條件跳轉。
* `if-goto labelName`：條件跳轉 (若堆疊頂端值不為 0 則跳轉)。

### 3. 函式呼叫 (Function Calling)
* `function funcName nVars`：定義函式並初始化區域變數。
* `call funcName nArgs`：呼叫函式 (自動保存 Caller 狀態與 Stack Frame)。
* `return`：從函式返回 (恢復 Caller 狀態與回傳值)。

### 4. 系統啟動 (Bootstrap Code)
* 支援多檔案目錄輸入。
* 自動寫入 `Sys.init` 啟動程式碼 (可選)。

---

## 🛠️ 專案結構 (Structure)

* **`VMTranslator.py`**：主程式。負責判斷輸入是檔案還是目錄，並驅動 Parser 與 CodeWriter。
* **`Parser.py`**：解析器。負責讀取 `.vm` 檔案，移除空白與註解，並將指令拆解為指令類型 (`commandType`) 與參數 (`arg1`, `arg2`)。
* **`CodeWriter.py`**：核心轉譯邏輯。負責將解析後的 VM 指令輸出為 Hack Assembly 代碼。

---

## 💻 使用方式 (Usage)

請在終端機 (Terminal) 執行以下指令：

### 1. 轉譯單一檔案 (適用於 SimpleFunction)
```bash
python VMTranslator.py Path/To/YourFile.vm
```

### 2. 轉譯整個目錄 (適用於 NestedCall, FibonacciElement)
```bash
python VMTranslator.py Path/To/Directory
```

## 🧪 測試策略 (Testing Strategy)

建議依照以下順序進行測試，確保功能逐步完善：

| 階段 | 測試專案 (`FunctionCalls/`) | 測試重點 | Bootstrap 設定 (`writeInit`) |
| :--- | :--- | :--- | :--- |
| **1** | `SimpleFunction` | `function`, `return` 基礎功能 | **關閉** (需註解掉) |
| **2** | `NestedCall` | `Sys.init`, `call`, Stack Frame 保存與恢復 | **開啟** |
| **3** | `FibonacciElement` | 遞迴演算法 (Recursion), 多檔案連結 | **開啟** |
| **4** | `StaticsTest` | 靜態變數命名空間 (`Class.i`) 獨立性 | **開啟** |

## 參考資料
[Gemini對話](https://gemini.google.com/share/ae4115456b6f)