# Project 9: Sky Defender (Jack Language Game)

這是一個基於 **Nand2Tetris 課程第 9 章 (High-Level Language)** 實作的簡單射擊遊戲。使用 **Jack 語言** 撰寫，運行於 Nand2Tetris 的 VMEmulator 上。

## 1. Jack 語言基本語法 (Jack Basic Syntax)

Jack 是一種類似 Java 的物件導向語言，但在設計上為了配合課程後續的編譯器實作，有許多嚴格的語法限制：

* **類別結構 (Class Structure)**
    * **單一類別**：每個檔案只能定義一個 `class`，且檔名必須與類別名稱完全一致。
    * **無繼承**：Jack 不支援 `extends` 或 `implements`。

* **變數宣告 (Variable Declaration)**
    * **宣告位置**：所有的變數宣告（`field`, `static`, `var`）必須寫在函式內的任何邏輯語句（如 `let`, `do`）**之前**。
    * **變數類型**：支援 `int`, `char`, `boolean`, 以及類別名稱（物件）。

* **函式類型**
    * `function`：靜態函式，類似 Java 的 `static` 方法。
    * `method`：物件方法，操作物件的 `field`，隱含 `this` 指標。
    * `constructor`：建構子，必須呼叫 `Memory.alloc` 並回傳 `this`。

* **特殊關鍵字**
    * `do`：用於呼叫**沒有回傳值 (void)** 的函式。例如：`do function();`
    * `let`：用於變數賦值。例如：`let x = 1;`
    * `Array`：沒有 `[]` 語法，必須使用 `Array.new(size)` 宣告與 `arr[i]` 存取。

## 2. 檔案結構與功能 (File Structure)

本專案由 5 個 `.jack` 檔案組成，不需要 `import` 語句，編譯器會自動連結同一資料夾下的檔案。

| 檔案名稱 | 類型 | 職責說明 |
| :--- | :--- | :--- |
| **Main.jack** | Entry Point | 程式入口。負責初始化 `Game` 物件，呼叫 `run()`，並在結束後進行 `dispose()`。 |
| **Game.jack** | Controller | **核心邏輯**。管理玩家、敵人與子彈陣列。處理輸入 (`Keyboard`) 與遊戲迴圈。 |
| **Player.jack** | Model / View | 定義玩家飛機的屬性（座標）與繪製方法 (`draw`, `erase`)。 |
| **Enemy.jack** | Model / View | 定義敵人的移動模式（左右移動 + 下降）與重置邏輯。 |
| **Bullet.jack** | Model / View | 定義子彈的飛行邏輯。包含 `active` 狀態以判斷是否飛出螢幕。 |

## 3. 程式邏輯 (Game Logic)

### 3.1 遊戲主迴圈 (The Game Loop)
遊戲運行在 `Game.jack` 的 `run()` 方法中，採用 Frame-based 迴圈設計：
1.  **Input (輸入)**：使用 `Keyboard.keyPressed()` 偵測按鍵。
    * *Debounce 處理*：為了防止瞬間發射多顆子彈，加入了 `spacePressed` 旗標來鎖定按鍵狀態。
2.  **Update (更新)**：計算 Player、Enemy 與所有 Bullet 的新座標。
3.  **Collision (碰撞)**：檢查子彈與敵人是否發生碰撞。
4.  **Draw (繪製)**：先擦除舊位置 (`color = false`)，再繪製新位置 (`color = true`)。
5.  **Wait (等待)**：呼叫 `Sys.wait(30)` 來控制 FPS，避免遊戲速度過快。

### 3.2 碰撞偵測 (Collision Detection)
採用 **AABB (Axis-Aligned Bounding Box)** 演算法。
程式檢查兩個矩形（子彈與敵人）是否**沒有**重疊。若上下左右四個方向皆無分離，則判定為碰撞。

### 3.3 記憶體管理 (Memory Management)
Jack 語言**沒有 Garbage Collection (GC)**，必須手動管理記憶體：
* **子彈銷毀**：當子彈飛出螢幕或擊中目標時，呼叫 `bullet.dispose()` 並將陣列該格設為 `null`。
* **遊戲結束**：程式結束前，`Main` 會呼叫 `game.dispose()`，進而觸發所有物件的 `dispose()` 方法，釋放記憶體 (`Memory.deAlloc`)。

## 4. 如何編譯與執行 (How to Compile & Run)

### 步驟 1：檔案準備
確保 `Main.jack`, `Game.jack`, `Player.jack`, `Enemy.jack`, `Bullet.jack` 位於同一個資料夾中（例如命名為 `SkyDefender`）。

### 步驟 2：編譯 (Compilation)
使用 Nand2Tetris 提供的工具集：
1. 開啟終端機 (Terminal)。
2. 執行指令：`JackCompiler SkyDefender` (資料夾路徑)。
3. 確認資料夾內是否產生了對應的 `.vm` 檔案。

### 步驟 3：模擬與執行 (Emulation)
1. 開啟 **VMEmulator**。
2. 點選 **File -> Load Folder** (載入整個 `SkyDefender` 資料夾)。
3. **關鍵設定**：將 **Animate** 選項設為 **"No animation"** (必須設定，否則效能不足)。
4. 點選 **Run** (雙箭頭圖示) 開始遊戲。

### 操作方式
* **LEFT / RIGHT**：左右移動飛機。
* **SPACE**：發射子彈。
* **Q**：離開遊戲。

## 參考資料
[Gemini對話](https://gemini.google.com/share/d5e0bb33810f)

---

> **⚠️ 常見問題 (Troubleshooting)**
>
> **Q: 為什麼按了空白鍵卻沒有發射子彈？**
> **A:** 請檢查您的電腦輸入法是否處於 **中文模式**。
> Jack 模擬器直接讀取鍵盤的 ASCII 碼，中文輸入法會攔截空白鍵訊號（用於選字），導致程式讀取不到 `key code 32`。**請切換回英文輸入法即可解決。**