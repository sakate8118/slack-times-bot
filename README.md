# Slack Times Bot
https://api.slack.com/apps/A0AMQ12D72T
## ■ 概要

本Botは、インターン生の稼働状況を可視化するために、Slack上の投稿状況を自動で監視し、一定時間更新がない場合にDMで通知するツールです。
GitHub Actionsを利用することで、サーバー不要で定期実行されます。

---

## ■ 機能

* インターン生（プロフィールタイトルが「インターン生」）を自動判定
* 「#0_勤怠」チャンネルの投稿数から出勤状態を判定
* 「#times-intern」の投稿状況を監視
* 最終投稿から一定時間（例：90分）経過した場合にDM通知
* 一度通知したユーザーには当日中再通知しない（スパム防止）

---

## ■ 通知条件

以下のすべてを満たす場合に通知されます：

1. プロフィールタイトルが「インターン生」である
2. 「#0_勤怠」に当日1回のみ投稿している（出勤中）
3. 「#times-intern」に一定時間以上投稿していない
4. 当日まだ通知されていない

---

## ■ 通知内容

対象ユーザーに対してSlackのDMで以下のようなメッセージが送信されます。

例：
⏰ 90分以上 #times-intern の更新がありません。
作業状況の共有をお願いします！

---

## ■ 使用技術

* Python
* Slack Web API（slack_sdk）
* GitHub Actions（定期実行）

---

## ■ ファイル構成

```
slack-times-bot/
├── bot.py                  # メイン処理
├── requirements.txt       # 依存ライブラリ
├── notified_users.json    # 通知済みユーザー管理
└── .github/
    └── workflows/
        └── run.yml        # GitHub Actions設定
```

---

## ■ セットアップ手順

### ① Slack Appの作成

* Slack APIページから新規アプリを作成

* Bot Token Scopes に以下を追加：

  * users:read
  * users.profile:read
  * channels:history
  * channels:read
  * chat:write

* ワークスペースにインストールし、Bot Token（xoxb-）を取得

---

### ② GitHub Secrets設定

リポジトリの Settings → Secrets and variables → Actions から以下を登録：

* Name：SLACK_BOT_TOKEN
* Value：取得したBot Token

---

### ③ チャンネルID設定

SlackのURLからチャンネルIDを取得し、`bot.py` に設定：

```python
CHANNEL_ATTENDANCE = "CXXXXXXXX"
CHANNEL_TIMES = "CXXXXXXXX"
```

---

### ④ Botをチャンネルに追加

Slackで以下を実行：

```
/invite @Bot名
```

対象：

* #0_勤怠
* #times-intern

---

### ⑤ GitHub Actions設定

`.github/workflows/run.yml` にワークフローを作成し、定期実行を設定：

```yaml
schedule:
  - cron: "*/5 * * * *"
```

※ 5分ごとに実行

---

## ■ 実行方法

### 手動実行

1. GitHubの「Actions」タブを開く
2. ワークフローを選択
3. 「Run workflow」をクリック

---

### 自動実行

設定したcronに従い、自動で定期実行されます。

---

## ■ 注意事項

* Botがチャンネルに参加していないと動作しません
* チャンネル名ではなく「チャンネルID」を使用してください
* notified_users.json が存在しない場合はエラーになります
* GitHub Actionsでは状態保持のため、JSONファイルをコミットしています

---

## ■ カスタマイズ

以下の項目は `bot.py` を修正することで変更可能です：

* 通知時間（例：30分 → 90分）
* 通知メッセージ内容
* 通知条件のロジック
* DM通知 → チャンネル通知

---

## ■ 今後の改善案

* 投稿があった場合に通知フラグを解除
* 勤怠の出勤時刻を基準にした判定
* エラー発生時のSlack通知

---

## ■ ライセンス

本リポジトリはMITライセンスで公開されています。
