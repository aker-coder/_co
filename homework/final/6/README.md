第 6 章：組譯器 (Assembler)



• 任務：寫一個程式，將組合語言（.asm，如 add.asm, pong.asm）翻譯成二進位機器碼（.hack）。

• 實作重點：

    ◦ 處理 A 指令（以 @ 開頭，如 @100）：翻譯成二進位數值。

    ◦ 處理 C 指令（運算與跳躍，如 D=M+1;JMP）：查表對照指令集將其轉為二進位碼。

    ◦ 處理 符號與標籤（Symbol & Label）：如 (LOOP) 或 @sum，需要建立符號表（Symbol Table）來對應記憶體位址。