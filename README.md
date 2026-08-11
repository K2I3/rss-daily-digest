# RSS Daily Digest

前日8:00〜当日8:00(JST)に配信されたRSS記事の「タイトル」と「リンク」を収集し、
メールで日次配信するアプリです。あわせて配信日・タイトル・リンクをSQLiteに蓄積します。
毎朝8:00(JST)にGitHub Actionsで自動実行されます。

(注: AI要約機能は含まれていません。記事本文の取得やClaude/Geminiによる要約が必要な場合は、
別途 `article_extractor.py` / `summarizer.py` を追加する拡張版で対応可能です)

## 構成

```
rss-daily-digest/
├── .github/workflows/daily_digest.yml  # 定期実行の設定(GitHub Actions)
├── src/
│   ├── main.py         # 全体の処理フロー(JSTの8:00境界を計算)
│   ├── config.py       # 設定・環境変数の読み込み
│   ├── rss_fetcher.py  # RSS取得と期間フィルタ
│   ├── database.py     # SQLiteへの保存(配信日・タイトル・リンク)
│   └── mailer.py       # メール送信(タイトル+リンクの一覧)
├── feeds.yaml           # 収集対象RSSの一覧(ここを編集して使う)
├── requirements.txt
├── .env.example          # 環境変数サンプル
└── data/                  # SQLiteデータベースの保存先
```

---

## 1. ローカル開発環境のセットアップ(VS Code / Windows)

### 1-1. リポジトリの準備

1. GitHubで新規リポジトリを作成(例: `rss-daily-digest`)
2. このフォルダの中身をそのままリポジトリ直下にコピー
3. VS Codeでフォルダを開く

### 1-2. Python仮想環境の作成

PowerShellで以下を実行:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 1-3. 環境変数ファイルの作成

```powershell
copy .env.example .env
```

`.env` を開いて以下を設定します。

| 変数名 | 内容 |
|---|---|
| `SMTP_USER` / `SMTP_PASSWORD` | Gmailの場合、SMTP_USERはGmailアドレス、SMTP_PASSWORDは**Googleアカウントのアプリパスワード**(2段階認証を有効にした上で発行) |
| `MAIL_TO` | 配信先メールアドレス(複数はカンマ区切り) |

### 1-4. 収集対象RSSの設定

`feeds.yaml` に取得したいRSSのURLを追加してください。

### 1-5. 動作確認(ローカル実行)

```powershell
cd src
python main.py
```

「前日8:00〜当日8:00(JST)」の期間に該当する記事がない場合、メールは送信されず
ログにその旨が表示されるだけです。動作確認だけしたい場合は `main.py` の
`get_time_window()` を一時的に広い範囲に書き換えてテストしてください。

---

## 2. GitHub Actionsでの自動実行設定(本番運用)

### 2-1. コードをGitHubにpush

```powershell
git add .
git commit -m "initial commit"
git push origin main
```

`.env` は `.gitignore` により除外されるため、認証情報は誤ってpushされません。

### 2-2. GitHub SecretsにSMTP情報を登録

GitHubリポジトリの `Settings` → `Secrets and variables` → `Actions` → `New repository secret` から、
以下を1つずつ登録します。

- `SMTP_USER`
- `SMTP_PASSWORD`
- `MAIL_TO`

### 2-3. 動作確認

- `Actions` タブを開き、`Daily RSS Digest` ワークフローを選択
- `Run workflow` ボタンから手動実行して正常終了するか確認
- 以降は毎日 UTC 23:00(= JST 8:00・翌日)に自動実行されます

### 2-4. データベースの永続化について

実行後にSQLiteファイル(`data/rss_digest.db`)を自動でリポジトリにコミットし直す仕組みにしているため、
「一度取得した記事を重複して配信・記録しない」という状態が日をまたいでも保持されます
(`link` カラムにUNIQUE制約を付けているため、同じ記事は2度保存されません)。

---

## 3. データベースの内容

`articles` テーブルには以下が保存されます。

| カラム | 内容 |
|---|---|
| `distribution_date` | RSS配信日(JST、このバッチが実行された日) |
| `feed_name` | どのフィード由来かの参考情報(`feeds.yaml` の `name`) |
| `title` | 記事タイトル |
| `link` | 元サイトへのリンク(重複防止のためUNIQUE) |

`feed_name` は仕様には明記されていませんでしたが、複数フィードを登録する場合に
どこから来た記事か分かった方が便利なため追加しています。不要であれば
`database.py` / `main.py` / `mailer.py` から該当箇所を削除してください。

## 4. カスタマイズのヒント

- **配信時刻を変える**: `.github/workflows/daily_digest.yml` の `cron` と、
  `src/main.py` の `window_end_jst = now_jst.replace(hour=8, ...)` の `hour` を両方変更してください。
- **収集フィードを増やす**: `feeds.yaml` に追記するだけで対応可能です。
