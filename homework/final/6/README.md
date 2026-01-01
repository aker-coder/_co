# Nand2Tetris Project 6: Hack Assembler (Hack 組譯器)

這是一個用 Python 實作的 Hack 電腦組譯器 (Assembler)。

本專案是 **Nand2Tetris (從 Nand 到 Tetris)** 課程第 6 章的作業成果。此程式能夠將 Hack 組合語言原始碼 (`.asm`) 翻譯成 Hack 電腦硬體可執行的二進位機器碼 (`.hack`)。

## 🚀 功能特點

* **完整的指令支援**：能夠精確處理所有的 A 指令 (`@value`) 與 C 指令 (`dest=comp;jump`)。
* **符號解析 (Symbol Resolution)**：
    * 支援 **預定義符號** (如 `SCREEN`, `KBD`, `R0`~`R15`)。
    * 支援 **標籤 (Labels)** (如 `(LOOP)`, `(END)`) 用於跳轉控制。
    * 支援 **變數 (Variables)** (如 `@i`, `@sum`) 自動分配記憶體位址 (從 RAM[16] 開始)。
* **兩遍掃描 (Two-Pass Process)**：採用標準的兩遍掃描演算法，有效解決程式碼中「向前參考 (Forward Reference)」的標籤問題。
* **強健的解析能力**：能自動忽略原始碼中的空白行與註解 (`//`)，並去除多餘空白。

## 📂 檔案結構

本專案採用單一檔案實作 (`assembler.py`)，內部採用物件導向設計，包含三個核心類別：

* **`Parser`**：
    * 負責讀取 `.asm` 檔案。
    * 清理每一行指令 (去除註解、空白)。
    * 拆解指令欄位 (如區分 `dest`, `comp`, `jump`)。
* **`Code`**：
    * 提供二進位查表功能。
    * 將助記符 (Mnemonics) 轉換為對應的 Hack 二進位碼 (例如 `D=M+1` -> `1111110111010000`)。
* **`SymbolTable`**：
    * 管理符號與記憶體位址的對應關係。
    * 預先載入標準符號表，並動態新增使用者定義的標籤與變數。

## 🛠️ 安裝與執行

### 需求環境
* Python 3.6 或以上版本

### 使用方式
打開終端機 (Terminal) 或命令提示字元 (CMD)，切換到檔案所在目錄，執行以下指令：

```bash
python assembler.py <你的檔案.asm>
