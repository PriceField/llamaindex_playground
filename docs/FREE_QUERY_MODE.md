# FREE Query Mode - 完全免費的查詢模式

## 問題：為什麼建立本地向量資料庫還會產生費用？

你說得對！當你問「用繁體中文介紹這個專案」時，系統呼叫了**多次 LLM API**，產生了不必要的費用。

### 費用分析

| 操作 | 位置 | 費用 |
|------|------|------|
| **建立向量嵌入** | 本地 (HuggingFace) | ✅ 免費 |
| **儲存向量** | 本地磁碟 | ✅ 免費 |
| **向量搜尋** | 本地向量資料庫 | ✅ 免費 |
| **生成答案** | 遠端 API (Claude) | 💰 **每次查詢 $0.01-0.05** |

### 為什麼會多次呼叫？

查看 `src/code_query_engine.py:63`:

```python
response_synthesizer = get_response_synthesizer(
    response_mode="compact",  # ← 這會導致多次 LLM 呼叫！
)
```

**"compact" 模式的運作方式：**
1. 檢索 5 個程式碼區塊
2. **呼叫 1：** 處理第一個區塊 → 部分答案
3. **呼叫 2：** 處理第二個區塊 → 細化答案
4. **呼叫 3-5：** 繼續處理...
5. **最終呼叫：** 整合所有答案

**單次查詢成本：** 5 次呼叫 × $0.01 = **約 $0.05 或更多！**

## 解決方案：完全免費的查詢模式

我已經新增了 **FREE Query Mode**，完全不呼叫 LLM：

### 新增的檔案

1. **`src/free_query_mode.py`** - 免費查詢引擎
2. **`demo_free_vs_paid.py`** - 比較免費與付費模式的示範腳本

### 使用方式

#### 方法 1: 互動模式

```bash
python src/main.py
```

選擇「Query an index」時，你會看到：

```
[MODE SELECTION]
  1. FREE mode - Retrieval only, no LLM (💰 $0.00 per query)
  2. AI mode - LLM synthesis (💰 ~$0.01-0.05 per query)

Your choice (1/2, default: 1):
```

選擇 **1** 即可使用免費模式！

#### 方法 2: 程式碼中使用

```python
from main import DocumentIndexer

# 建立索引器（不需要 LLM）
indexer = DocumentIndexer("my_index", require_llm=False)
indexer.load_existing_index()

# 免費查詢（完全不呼叫 LLM）
indexer.free_query("如何進行身份驗證？", top_k=5)
```

#### 方法 3: 執行比較示範

```bash
python demo_free_vs_paid.py
```

這會示範兩種模式的差異。

## FREE 模式會得到什麼？

### 免費模式輸出範例

```
🔍 SEARCH RESULTS (FREE MODE - No LLM used)
======================================================================

[1] auth.py
    Path: src/auth.py
    Lines: 15-45
    Language: python
    Type: code
    Relevance: 0.872

    Content:
    ------------------------------------------------------------------
    def login(username, password):
        """Authenticate user credentials."""
        user = db.find_user(username)
        if user and check_password(password, user.hash):
            return create_session(user)
        return None
    ------------------------------------------------------------------

[2] user.py
    Path: src/user.py
    Lines: 88-120
    Language: python
    Type: code
    Relevance: 0.815

    Content:
    ------------------------------------------------------------------
    class User:
        def validate_credentials(self):
            # validation logic
            ...
    ------------------------------------------------------------------

💡 TIP: Read the code above to find your answer (FREE!)
💰 COST: $0.00 (No LLM calls made)
======================================================================
```

**你需要做的：** 自己閱讀這些程式碼區塊並理解答案。

## AI 模式會得到什麼？（需付費）

### AI 模式輸出範例

```
ANSWER:
======================================================================
身份驗證系統分為兩個步驟：

1. 登入驗證（auth.py:15-45）：login() 函數接收使用者名稱和密碼，
   查詢資料庫，並使用 check_password() 驗證密碼雜湊值。

2. 使用者驗證（user.py:88-120）：User 類別有額外的憑證驗證邏輯。

驗證成功後，會透過 create_session() 建立會話。如果憑證無效，則返回 None。
======================================================================

💰 COST: $0.03 (Made 3 LLM API calls)
```

**LLM 做了什麼：** 閱讀所有區塊，理解它們，並為你撰寫連貫的解釋。

## 何時使用哪種模式？

| 使用情境 | 建議 |
|----------|------|
| **快速程式碼搜尋** - 「登入函數在哪裡？」 | ❌ 不需要 LLM - 使用免費模式 |
| **尋找範例** - 「顯示 API 端點範例」 | ❌ 不需要 LLM - 只顯示區塊 |
| **理解複雜邏輯** - 「快取系統如何運作？」 | ✅ LLM 有幫助 - 整合解釋 |
| **解釋關聯性** - 「這 3 個模組如何互動？」 | ✅ LLM 很有幫助 - 連結概念 |
| **成本敏感** - 大量查詢，預算有限 | ❌ 不使用 LLM - 省錢 |
| **需要其他語言解釋** - 「用繁體中文介紹」 | ✅ 需要 LLM - 但成本高！ |

## 建議

**日常使用：** 使用免費模式
- 尋找函數、類別、範例
- 理解程式碼結構
- 快速查找

**僅在以下情況使用 AI 模式：**
- 需要複雜解釋
- 連接多個檔案中的概念
- 用自然語言翻譯/解釋
- **願意支付費用**

## 技術細節

### FREE 模式的運作方式

1. 將你的問題轉換為向量（使用本地 HuggingFace 模型）
2. 在向量資料庫中搜尋（完全本地）
3. 返回前 K 個最相關的程式碼區塊
4. 顯示結果（含元資料）
5. **完全不呼叫 LLM** ✅

### AI 模式的運作方式

1. 將你的問題轉換為向量（使用本地 HuggingFace 模型）
2. 在向量資料庫中搜尋（完全本地）
3. 返回前 K 個最相關的程式碼區塊
4. **呼叫 LLM API 多次**（compact 模式）💰
5. LLM 讀取所有區塊並生成答案
6. 顯示整合的答案

## 總結

**你原本的想法是對的：**
```
本地向量資料庫 = 應該免費 ✅
```

**現在的實作：**
```
本地向量資料庫 = 免費搜尋 + 可選的 LLM 整合（付費）
```

使用新的 **FREE 模式**，你可以：
- ✅ 享受語義搜尋的強大功能
- ✅ 完全不需成本
- ✅ 取得所有相關程式碼區塊
- ❌ 但需要自己閱讀和理解程式碼

**這才是真正的 $0.00 成本！** 🎉
