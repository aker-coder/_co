## 🐛 錯誤與修正紀錄 (Bug Fixes & Troubleshooting)

### 1. `KeyError: 'pointer'` 錯誤
**狀況描述**：
執行轉譯時，程式崩潰並顯示 `KeyError: 'pointer'`。

**錯誤原因**：
在 `CodeWriter.py` 中，試圖使用 `seg_map` 字典來查找 `pointer`、`temp` 或 `static` 的基底位址。但這些記憶體區段沒有單一的基底指標 (如 LCL/ARG)，因此字典中不存在對應的 Key。

**✅ 修正後 (解決方案)**：
在 `writePushPop` 加入條件判斷，針對特殊區段分流處理。

```python
if segment == "pointer":
    label = "THIS" if index == 0 else "THAT"
    # 生成 pointer 專屬組合語言
elif segment == "temp":
    # 生成 temp (RAM[5]+i) 專屬組合語言
elif segment == "static":
    # 生成 static (FileName.i) 專屬組合語言
else:
    # 其他標準區段才使用通用函式
    self._write_pop_to_segment(segment, index)