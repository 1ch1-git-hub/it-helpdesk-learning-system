# IT系ヘルプデスク学習支援システム（本番版）

技術力×人間力の総合学習支援システム。毎朝9時（平日のみ）にChatworkへ自動投稿。

## 🚀 機能

- **YouTube API連携**: リアルタイムで最新の学習動画を検索
- **平日限定自動投稿**: 月曜〜金曜の朝9時に自動実行
- **カテゴリ別投稿**: 技術系70%、人間力系30%の比率
- **GitHub Actions**: 完全自動化された実行環境

## 📋 セットアップ

### 1. API設定

#### YouTube Data API v3
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. プロジェクトを作成または選択
3. YouTube Data API v3を有効化
4. APIキーを作成

#### Chatwork API
1. [Chatwork API設定](https://www.chatwork.com/service/packages/chatwork/subpackages/api/token.php)でトークン取得
2. 投稿先ルームIDを確認

### 2. GitHub Secrets設定

リポジトリの Settings > Secrets and variables > Actions で以下を設定：
- `CHATWORK_API_TOKEN`: ChatworkのAPIトークン
- `CHATWORK_ROOM_ID`: 投稿先のルームID  
- `YOUTUBE_API_KEY`: YouTube Data API v3のAPIキー

## 📅 実行スケジュール

- **自動実行**: 平日（月〜金） 日本時間 朝9:00
- **手動実行**: GitHub ActionsのWorkflow Dispatchから随時可能

## 🎯 投稿内容

### 技術系コンテンツ (70%)
- ITパスポート、基本情報技術者試験
- CCNA、CompTIA A+、ITIL
- ヘルプデスク業務、システム管理

### 人間力系コンテンツ (30%)
- 7つの習慣、アドラー心理学
- ビジネスマナー、コミュニケーション術
- リーダーシップ、チームワーク
