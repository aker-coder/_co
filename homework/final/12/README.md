# Nand2Tetris Project 12: The Operating System

## 📖 專案概述 (Overview)
這是 Nand2Tetris 課程的最後一塊拼圖：**作業系統 (Operating System)**。
在這個章節中，我們探討了如何在此電腦架構（Hack Platform）之上，透過軟體層面來補足硬體功能的缺失。由於 Hack 硬體架構極簡（不支援硬體乘除法、無內建繪圖指令），因此必須透過高階語言（Jack OS）來實作一組標準函式庫，以提供應用程式開發所需的基礎服務。

## ⚠️ 特別說明 (Course Regulation)
**根據課程規定與指導：**
本章節的工程規模龐大，重點在於**理解作業系統的設計原理與演算法實作**。因此，本專案的執行方式為**研讀並分析**現有的作業系統實作（基於老師提供的 `CPU2OS` 版本或 Nand2Tetris 官方參考實作），而非從零開始撰寫所有程式碼。

本專案旨在深入理解以下核心概念：
* 如何用軟體演算法實作數學運算（乘法、除法）。
* 記憶體管理（Heap Management）的底層邏輯。
* 圖形與文字輸出的點陣處理。

## 📂 OS 模組架構 (System Modules)

本作業系統由 8 個核心類別（Class）組成，每個類別對應一個 `.jack` 檔案。以下是各模組的功能分析與研讀重點：

### 1. Math.jack (數學運算)
* **功能**：提供如 `multiply` (乘法), `divide` (除法), `sqrt` (開根號) 等基礎數學函式。
* **關鍵實作**：
    * 由於硬體沒有乘法器，乘法是透過 **Bit-shift (位移)** 和 **加法** 來實現（類似長乘法原理）。
    * 除法採用遞迴的長除法演算法。
    * 為了效能，預先計算了 $2^i$ 的陣列 (`twoToThe`)。

### 2. Memory.jack (記憶體管理)
* **功能**：負責 Heap（堆積）的記憶體配置 (`alloc`) 與釋放 (`deAlloc`)，以及直接記憶體存取 (`peek`, `poke`)。
* **關鍵實作**：
    * 使用 **Free List (空閒列表)** 演算法來追蹤可用的記憶體區段。
    * `alloc` 採用 First-fit 或 Best-fit 策略尋找足夠大的區塊。

### 3. Screen.jack (螢幕繪圖)
* **功能**：提供基本的繪圖指令，如畫點 (`drawPixel`)、畫線 (`drawLine`)、畫圓 (`drawCircle`) 及畫矩形。
* **關鍵實作**：
    * 直接操作 **Screen Memory Map (RAM 16384 - 24575)**。
    * 透過 Bitwise 操作（位元運算）來控制特定像素的開關，同時優化橫向直線的繪製（一次寫入 16 bits 以提升效能）。

### 4. Output.jack (文字輸出)
* **功能**：處理文字在螢幕上的顯示，包含游標移動與字元點陣圖的繪製。
* **關鍵實作**：
    * 定義了字型庫（Font Map），將 ASCII 對應到 11x8 的像素矩陣。
    * 實作了 `printInt` 與 `printString`，並處理換行與 Backspace 的邏輯。

### 5. Keyboard.jack (鍵盤輸入)
* **功能**：處理使用者輸入。
* **關鍵實作**：
    * 監聽 **Keyboard Memory Map (RAM 24576)**。
    * 提供 `readLine` 與 `readInt`，實作了基本的輸入緩衝區（Buffer）與回顯（Echo）功能。

### 6. String.jack (字串處理)
* **功能**：實作字串物件及其操作（長度、附加字元、整數轉換）。
* **關鍵實作**：
    * 字串在內部被視為一個字元陣列。
    * 實作了整數與字串之間的相互轉換演算法。

### 7. Array.jack (陣列支援)
* **功能**：提供陣列的建立與釋放。
* **關鍵實作**：
    * 直接呼叫 `Memory.alloc` 與 `Memory.deAlloc`，是 OS 中最輕量的封裝。

### 8. Sys.jack (系統核心)
* **功能**：作業系統的進入點（Entry point）與執行時控制。
* **關鍵實作**：
    * `init`：初始化所有 OS 模組，並呼叫 `Main.main` 啟動使用者程式。
    * `wait`：透過空迴圈實作時間延遲。
    * `halt`：透過無窮迴圈停止系統運行。

## 🔗 參考資源 (References)
* **Source Code**: [GitHub - CPU2OS](https://github.com/ccc114a/cpu2os/tree/master/_nand2tetris/12)
* **Textbook**: *The Elements of Computing Systems* (Nand2Tetris) by Noam Nisan and Shimon Schocken.

---