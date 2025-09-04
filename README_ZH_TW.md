# Green Moment - 智慧碳足跡追蹤平台

![Green Moment Logo](assets/leaf_plug_single.png)

## 專案簡介

Green Moment 是一款創新的行動應用程式，協助台灣家庭透過即時監控台電電網的碳排放強度來減少碳足跡。透過將高耗能活動轉移到低碳時段，使用者可以在維持生活品質的同時為環保盡一份心力。

## 核心功能

### 🌱 即時碳排追蹤
- 即時監控台灣電網碳排放強度
- 查看未來 24 小時預測，規劃您的活動
- 歷史數據分析與趨勢圖表

### 📱 智慧家電排程
- 記錄家用電器使用情況
- 獲得最佳使用時段建議
- 追蹤智慧排程帶來的碳減量

### 🏆 遊戲化與獎勵機制
- 基於每月碳減量的聯盟系統
- 從青銅晉升至鑽石聯盟
- 追蹤您的環境影響力

### 🔔 智慧通知系統
- 低碳時段的客製化提醒
- 基於使用習慣的個人化建議
- 在您偏好的時間接收每日提醒

### 👤 彈性認證方式
- 匿名模式快速開始
- 安全的 Google 登入以保存資料
- 從匿名無縫升級為註冊帳戶

## 系統架構

Green Moment 生態系統包含三個主要元件：

### 1. 後端 API (FastAPI)
- **位置**：`/green_moment_backend_api`
- **技術堆疊**：Python、FastAPI、PostgreSQL、Redis、Firebase
- **功能特色**：
  - 支援非同步的 RESTful API
  - 基於 JWT 的身份驗證
  - 即時資料快取
  - 推播通知系統
  - 自動化排程器進行資料更新

### 2. 行動應用程式 (Flutter)
- **位置**：`/green_moment_app`
- **技術堆疊**：Flutter、Dart、Firebase Messaging
- **平台**：Android（iOS 就緒）
- **功能特色**：
  - Material Design 使用者介面
  - 即時資料視覺化
  - 離線功能
  - 推播通知

### 3. 資料管線
- **位置**：`/green_moment_integrated`
- **技術堆疊**：Python、Pandas
- **功能特色**：
  - 每 10 分鐘收集發電資料
  - 整合天氣資料以提供更準確預測
  - 區域碳排放強度計算

## 快速開始

### 系統需求
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Flutter 3.8+
- 已啟用 FCM 的 Firebase 專案

### 後端設定

1. **複製專案**
```bash
git clone [repository-url]
cd green_moment_backend_api
```

2. **建立虛擬環境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安裝相依套件**
```bash
pip install -r requirements.txt
```

4. **設定環境變數**
```bash
cp .env.example .env
# 編輯 .env 檔案，填入您的設定
```

5. **設定資料庫**
```bash
# 建立資料庫
createdb green_moment

# 執行遷移
alembic upgrade head
```

6. **啟動服務**
```bash
# 終端機 1：API 伺服器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 終端機 2：碳資料產生器（在 X9 分執行）
python scripts/carbon_intensity_generator.py --scheduled

# 終端機 3：通知排程器（在 X0 分執行）
python scripts/run_notification_scheduler.py
```

### Flutter 應用程式設定

1. **切換至應用程式目錄**
```bash
cd green_moment_app
```

2. **安裝相依套件**
```bash
flutter pub get
```

3. **設定 Google 登入**
- 將您的 `google-services.json` 加入 `android/app/`
- 在 `android/app/src/main/res/values/strings.xml` 更新您的 Web Client ID

4. **執行應用程式**
```bash
flutter run
```

## 專案結構

```
green_moment/
├── green_moment_backend_api/      # 後端 API
│   ├── app/                       # 應用程式程式碼
│   │   ├── api/                   # API 端點
│   │   ├── core/                  # 核心功能
│   │   ├── models/                # 資料庫模型
│   │   ├── schemas/               # Pydantic 架構
│   │   └── services/              # 商業邏輯
│   ├── migrations/                # 資料庫遷移
│   ├── scripts/                   # 工具腳本
│   └── tests/                     # 測試套件
│
├── green_moment_app/              # Flutter 行動應用程式
│   ├── lib/                       # Dart 原始碼
│   │   ├── models/                # 資料模型
│   │   ├── screens/               # UI 畫面
│   │   ├── services/              # API 服務
│   │   └── widgets/               # 可重用元件
│   ├── android/                   # Android 設定
│   └── assets/                    # 圖片和資源
│
└── green_moment_integrated/       # 資料管線
    ├── stru_data/                 # 輸出 CSV 檔案
    ├── logs/                      # 日誌檔案
    └── config/                    # 設定檔
```

## API 文件

後端啟動後，請造訪：
- Swagger UI：http://localhost:8000/api/v1/docs
- ReDoc：http://localhost:8000/api/v1/redoc

### 主要端點

- **身份驗證**
  - `POST /api/v1/auth/google` - Google 登入
  - `POST /api/v1/auth/anonymous` - 匿名登入
  
- **碳資料**
  - `GET /api/v1/carbon/current` - 目前強度
  - `GET /api/v1/carbon/forecast` - 24 小時預測
  
- **使用者進度**
  - `GET /api/v1/progress/summary` - 使用者統計
  - `POST /api/v1/chores/log` - 記錄家電使用

## 開發指南

### 執行測試
```bash
# 後端測試
cd green_moment_backend_api
pytest

# Flutter 測試
cd green_moment_app
flutter test
```

### 程式碼風格
```bash
# Python 格式化
black app/
flake8 app/

# Dart 格式化
flutter analyze
flutter format lib/
```

## 部署指南

### 生產環境檢查清單

1. **安全性**
   - [ ] 更改預設資料庫密碼
   - [ ] 產生安全的 JWT 密鑰
   - [ ] 設定 HTTPS/SSL
   - [ ] 設定 API 速率限制

2. **設定**
   - [ ] 更新 Flutter 應用程式中的生產環境 URL
   - [ ] 為生產環境設定 Firebase
   - [ ] 設定網域和 SSL 憑證
   - [ ] 設定雲端儲存空間

3. **基礎設施**
   - [ ] 設定雲端資料庫（Cloud SQL/RDS）
   - [ ] 設定 Redis 快取
   - [ ] 設定監控和日誌記錄
   - [ ] 設定自動擴展

### 部署選項

**選項 1：Google Cloud Platform**
```yaml
服務：
- Cloud Run：API 和排程器
- Cloud SQL：PostgreSQL
- Memorystore：Redis
- Cloud Storage：資料檔案
- Cloud Scheduler：Cron 作業
```

**選項 2：經濟實惠方案**
```yaml
服務：
- Render.com：免費 API 層級
- Supabase：免費 PostgreSQL
- Redis Labs：免費層級
- GitHub Actions：CI/CD
```

## 貢獻指南

我們歡迎貢獻！詳情請參閱我們的[貢獻指南](CONTRIBUTING.md)。

### 開發工作流程
1. Fork 專案
2. 建立功能分支
3. 進行您的修改
4. 新增測試
5. 提交 Pull Request

## 支援

- **文件**：[Wiki](wiki-url)
- **問題回報**：[GitHub Issues](issues-url)
- **電子郵件**：support@greenmoment.tw

## 授權

本專案採用 MIT 授權 - 詳情請參閱 [LICENSE](LICENSE) 檔案。

## 致謝

- 台灣電力公司提供即時資料
- 中央氣象署提供天氣資料
- 所有測試人員和貢獻者

---

**Green Moment** - 讓每一度電都為永續未來盡一份力 🌱