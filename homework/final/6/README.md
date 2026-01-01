Nand2Tetris Project 6: Hack Assembler (Hack 組譯器)
這是一個用 Python 實作的 Hack 電腦組譯器 (Assembler)。

本專案是 Nand2Tetris (從 Nand 到 Tetris) 課程第 6 章的作業目標。此程式能夠將 Hack 組合語言 (.asm) 翻譯成 Hack 電腦硬體可執行的二進位機器碼 (.hack)。

🚀 功能特點
完整的指令支援：能夠處理所有的 A 指令 (@value) 與 C 指令 (dest=comp;jump)。

符號解析 (Symbol Resolution)：

支援 預定義符號 (如 SCREEN, KBD, R0~R15)。

支援 標籤 (Labels) (如 (LOOP), (END)) 用於跳轉控制。

支援 變數 (Variables) (如 @i, @sum) 自動分配記憶體位址 (從 RAM[16] 開始)。

兩遍掃描 (Two-Pass Process)：採用標準的兩遍掃描演算法，解決程式碼中「向前參考 (Forward Reference)」的標籤問題。

錯誤處理：能忽略原始碼中的空白行與註解 (//)。

📂 檔案結構
本專案採用單一檔案實作，內部包含三個主要類別：

assembler.py：主程式，包含以下模組：

Parser 類別：負責讀取檔案、清理字串、拆解指令欄位。

Code 類別：提供二進位查表功能 (Mnemonic to Binary)。

SymbolTable 類別：管理符號與記憶體位址的對應關係。

🛠️ 安裝與執行
需求環境
Python 3.6 或以上版本

使用方式
在終端機 (Terminal) 中執行以下指令：

Bash

python assembler.py <你的檔案.asm>
範例
假設你有一個 Pong.asm 檔案，執行：

Bash

python assembler.py Pong.asm
程式執行完畢後，會在同一個資料夾下產生 Pong.hack 檔案。你可以將此檔案載入 CPUEmulator 進行測試。

🧠 實作邏輯 (Implementation Details)
本組譯器採用 兩遍掃描 (Two-Pass Approach)：

第一遍掃描 (First Pass)：

只讀取標籤定義 (Label)。

將標籤名稱與其對應的 ROM 位址 (下一行指令的行號) 存入 SymbolTable。

此階段不進行翻譯，不產生輸出。

第二遍掃描 (Second Pass)：

重新讀取檔案，處理 A 指令與 C 指令。

A 指令：若遇到變數符號 (如 @sum)，先檢查符號表；若不存在則分配新的 RAM 位址 (從 16 開始遞增)。

C 指令：利用 Parser 切割欄位，並呼叫 Code 模組查詢對應的二進位碼。

將最終的 16-bit 二進位字串寫入 .hack 檔案。

✅ 測試與驗證
本組譯器已通過以下標準測試檔案驗證：

Add.asm (無符號的基本運算)

Max.asm (包含標籤與跳轉)

Rect.asm (包含預定義符號與繪圖迴圈)

Pong.asm (大型程式，包含所有組譯器特性)

產出的 .hack 檔案與 Nand2Tetris 提供的標準組譯器輸出結果一致。