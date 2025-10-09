#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import json
import random
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Tuple
from enum import Enum
from urllib.parse import quote

class ContentCategory(Enum):
    TECHNICAL = "technical"
    HUMAN_SKILLS = "human_skills"
    AI_ML = "ai_ml"
    MIXED = "mixed"

class ProductionChatworkAutoPost:
    def __init__(self, api_token: str, room_id: str, youtube_api_key: str):
        """
        本番用：YouTube API連携版チャットワーク自動投稿システム
        技術力×人間力×AI活用力の総合学習支援
        """
        self.api_token = api_token
        self.room_id = room_id
        self.youtube_api_key = youtube_api_key
        self.chatwork_base_url = "https://api.chatwork.com/v2"
        self.youtube_base_url = "https://www.googleapis.com/youtube/v3"
        
        # 🔧 技術系検索キーワード（社内スキルアップ向け）
        self.technical_keywords = [
            "ITパスポート 資格 社内勉強会 スキルアップ",
            "基本情報技術者 試験 企業内研修 勉強法",
            "IT系ヘルプデスク 社内サポート 業務効率化",
            "ヘルプデスク 社内対応 顧客満足度 向上",
            "情報セキュリティ 社内研修 対策 管理",
            "Excel VBA 業務自動化 効率化 実務",
            "ネットワーク 社内インフラ 管理 運用",
            "システム管理 社内IT 運用 保守",
            "ITIL サービス管理 社内プロセス 改善",
            "Windows Server 社内環境 構築 運用",
            "ネットワーク トラブル対応 社内サポート",
            "Active Directory 社内システム 管理運用"
        ]
        
        # 🎯 人間力系検索キーワード（社内コミュニケーション向け）
        self.human_skills_keywords = [
            "7つの習慣 職場 チームワーク 生産性向上",
            "アドラー心理学 職場関係 部下指導 マネジメント",
            "ビジネスマナー 社内コミュニケーション 接客対応",
            "効果的な会話術 顧客対応 社内連携",
            "好印象を与える話し方 営業力 接客スキル",
            "コミュニケーション能力 チーム連携 協働",
            "ビジネス敬語 顧客対応 電話応対",
            "職場 人間関係 チームビルディング",
            "リーダーシップ 部下育成 チーム管理",
            "問題解決思考 業務改善 効率化手法",
            "ストレス管理 メンタルヘルス 働き方改革",
            "チームワーク 協調性 生産性向上"
        ]
        
        # 🤖 AI・機械学習系検索キーワード
        self.ai_ml_keywords = [
            # 🔥 主要AI競合・代替サービス
            "Claude Anthropic 使い方 ChatGPT 比較 違い",
            "Google Gemini 旧Bard 機能 活用法 Gmail連携",
            "Microsoft Copilot Office365 Word Excel 統合活用",
            "DeepSeek AI 推論能力 コード生成 使い方",
            "Perplexity AI ウェブ検索 情報収集 調査ツール",
            "Meta AI Facebook Instagram WhatsApp 統合",
            "Grok xAI Twitter X リアルタイム情報",
            "ChatGPT vs Claude vs Gemini 比較 選び方",
            "生成AI 比較 2025 最新 おすすめ ランキング",
            
            # 🎯 AI基礎・入門
            "AI人工知能 基礎 初心者 わかりやすい 仕組み",
            "機械学習 Machine Learning 入門 基本概念",
            "深層学習 ディープラーニング ニューラルネットワーク",
            "自然言語処理 NLP 大規模言語モデル LLM",
            "生成AI Generative AI 概要 種類 活用事例",
            
            # 💻 実践・プログラミング
            "Python データサイエンス 機械学習 入門",
            "Google Colab Python 機械学習 実践 チュートリアル",
            "TensorFlow Keras PyTorch 入門 比較",
            "scikit-learn データ分析 機械学習ライブラリ",
            "Jupyter Notebook データサイエンス 環境構築",
            
            # 🚀 プロンプトエンジニアリング・活用
            "プロンプトエンジニアリング 技術 コツ 効果的な書き方",
            "ChatGPT 活用法 ビジネス 業務効率化 事例",
            "AI プロンプト 作成 テンプレート 実践例",
            "生成AI ビジネス活用 導入事例 成功パターン",
            
            # 📊 データサイエンス・分析
            "データサイエンス 統計 分析手法 基礎",
            "機械学習 アルゴリズム 種類 回帰 分類 クラスタリング",
            "データ前処理 特徴量エンジニアリング Python",
            "AutoML 自動機械学習 ツール 比較 使い方",
            
            # 🎨 画像・音声・マルチモーダル
            "Computer Vision 画像認識 OpenCV 基礎",
            "Stable Diffusion Midjourney AI画像生成 比較",
            "音声認識 音声合成 AI 技術 活用事例",
            "マルチモーダルAI 画像 テキスト 統合処理",
            
                # 💼 AI社内活用・業務改善
            "AI業務効率化 社内導入 生産性向上 ヘルプデスク",
            "データ活用 社内システム 分析手法 業務改善",
            "AIツール チーム連携 導入事例 社内活用",
            "AIリテラシー 社内研修 スキルアップ 人材育成",
            
            # 🌐 AI倫理・社会影響
            "AI倫理 人工知能 社会への影響 課題",
            "AIガバナンス 責任あるAI 開発 運用",
            "AI セキュリティ プライバシー 保護対策",
            "AI 雇用への影響 未来の働き方 変化",
            
            # 🔮 最新技術・トレンド
            "Transformer BERT GPT モデル 仕組み 解説",
            "RAG Retrieval Augmented Generation 活用法",
            "ファインチューニング 学習済みモデル カスタマイズ",
            "エッジAI IoT 組み込みシステム 活用",
            
            # 🏢 業界別AI活用
            "AI ヘルプデスク 自動化 チャットボット 導入",
            "AIカスタマーサポート 対話システム 構築",
            "IT運用 AIOps 異常検知 自動化",
            "AI 業務自動化 RPA 連携 効率化"
        ]
        
        # 📈 技術系投稿テンプレート（社内情報共有用）
        self.technical_templates = [
            "🔧 社内ITスキル向上情報共有",
            "💻 ヘルプデスク業務改善ノウハウ",
            "⚡ 社内ITサポート品質向上のために",
            "🚀 チームの技術力底上げ情報",
            "📚 社内研修サポートコンテンツ",
            "🎯 業務効率化のための学習リソース"
        ]
        
        # 💡 人間力系投稿テンプレート（社内コミュニケーション向上）
        self.human_skills_templates = [
            "🌟 社内コミュニケーション力向上情報",
            "💬 顧客対応品質向上のために",
            "🎭 プロフェッショナルな対応スキル研修",
            "🤝 チームワーク向上のためのヒント",
            "💪 社内人材育成＆スキルアップ情報",
            "🧠 心理学で学ぶ顧客心理理解術"
        ]
        
        # 🤖 AI・機械学習系投稿テンプレート（社内AI活用推進）
        self.ai_ml_templates = [
            "🤖 社内AI活用推進情報共有",
            "⚡ 生成AIでヘルプデスク業務改善",
            "🚀 AIツール活用で生産性向上",
            "🧠 機械学習基礎知識共有会",
            "🎯 AIプロンプト技術社内研修",
            "💡 社内AI導入成功事例シェア",
            "🔮 未来の業務スタイル情報共有",
            "⚙️ AI×ITで業務改革を実現"
        ]

    def get_category_by_day(self) -> ContentCategory:
        """曜日ベースのカテゴリ選択（平日のみ実行）"""
        jst = timezone(timedelta(hours=9))
        today = datetime.now(jst).weekday()
        
        if today < 5:  # 平日（月〜金）
            # 50%技術系、25%人間力系、25%AI・機械学習系
            return random.choices(
                [ContentCategory.TECHNICAL, ContentCategory.HUMAN_SKILLS, ContentCategory.AI_ML],
                weights=[0.5, 0.25, 0.25]
            )[0]
        else:
            return ContentCategory.TECHNICAL

    def get_keywords_and_template(self) -> Tuple[List[str], List[str], str]:
        """カテゴリに応じたキーワードとテンプレートを取得"""
        category = self.get_category_by_day()
        
        if category == ContentCategory.TECHNICAL:
            return (
                self.technical_keywords,
                self.technical_templates,
                "技術系"
            )
        elif category == ContentCategory.HUMAN_SKILLS:
            return (
                self.human_skills_keywords,
                self.human_skills_templates,
                "人間力系"
            )
        elif category == ContentCategory.AI_ML:
            return (
                self.ai_ml_keywords,
                self.ai_ml_templates,
                "AI・機械学習系"
            )
        else:
            return (
                self.technical_keywords + self.human_skills_keywords + self.ai_ml_keywords,
                [],
                "統合型"
            )

    def get_channel_details(self, channel_ids: List[str]) -> Dict:
        """
        チャンネルIDのリストから詳細情報（登録者数等）を取得
        """
        try:
            channels_url = f"{self.youtube_base_url}/channels"
            
            params = {
                'part': 'statistics,snippet',
                'id': ','.join(channel_ids),
                'key': self.youtube_api_key
            }
            
            response = requests.get(channels_url, params=params)
            
            if response.status_code != 200:
                print(f"❌ チャンネル詳細取得エラー: {response.status_code}")
                return {}
            
            data = response.json()
            details = {}
            
            for item in data.get('items', []):
                channel_id = item['id']
                statistics = item.get('statistics', {})
                
                details[channel_id] = {
                    'subscriberCount': statistics.get('subscriberCount', '0'),
                    'videoCount': statistics.get('videoCount', '0'),
                    'viewCount': statistics.get('viewCount', '0')
                }
            
            return details
            
        except Exception as e:
            print(f"❌ チャンネル詳細取得エラー: {e}")
            return {}

    def calculate_video_quality_score(self, video: Dict) -> float:
        """
        動画の質を数値化してスコア算出（社内向け高品質フィルタ）
        """
        score = 0.0
        
        # 登録者数スコア (最大30点) - より完全なコンテンツを求める
        subscriber_count = int(video.get('subscriber_count', '0'))
        if subscriber_count >= 500000:  # 50万人以上
            score += 30
        elif subscriber_count >= 100000:  # 10万人以上
            score += 25
        elif subscriber_count >= 50000:  # 5万人以上
            score += 20
        elif subscriber_count >= 10000:  # 1万人以上 (最低基準)
            score += 15
        else:  # 1万人未満は除外
            return 0.0  # 即座除外
        
        # 再生数スコア (最大25点)
        view_count = int(video.get('view_count_raw', '0'))
        if view_count >= 100000:  # 10万再生以上
            score += 25
        elif view_count >= 50000:  # 5万再生以上
            score += 20
        elif view_count >= 10000:  # 1万再生以上
            score += 15
        elif view_count >= 1000:   # 1000再生以上
            score += 10
        
        # 動画の長さスコア (最大30点) - 十分な解説を求める
        duration_seconds = self.parse_duration_to_seconds(video.get('duration', 'PT0S'))
        if duration_seconds < 600:  # 10分未満は除外
            return 0.0  # 即座除外
        elif 600 <= duration_seconds <= 1800:  # 10分〜30分 (理想的)
            score += 30
        elif 1800 <= duration_seconds <= 3600:  # 30分〜1時間
            score += 25
        elif 3600 <= duration_seconds <= 5400:  # 1時間〜1.5時間
            score += 20
        else:  # 1.5時間超えは減点
            score += 10
        
        # タイトル品質スコア (最大15点)
        title = video.get('title', '').lower()
        quality_keywords = [
            '解説', 'わかりやすい', '入門', '基礎', '実践', '方法', 
            '初心者', '完全版', 'まとめ', 'ノウハウ', 'コツ', '攻略'
        ]
        title_score = sum(5 for keyword in quality_keywords if keyword in title)
        score += min(title_score, 15)  # 最大15点
        
        # 投稿日の新しさスコア (最大10点)
        try:
            published_date = datetime.strptime(video.get('published_at', '2000-01-01'), '%Y-%m-%d')
            days_ago = (datetime.now() - published_date).days
            if days_ago <= 30:      # 1ヶ月以内
                score += 10
            elif days_ago <= 90:    # 3ヶ月以内
                score += 8
            elif days_ago <= 180:   # 6ヶ月以内
                score += 6
            elif days_ago <= 365:   # 1年以内
                score += 4
        except:
            pass
        
        return score

    def parse_duration_to_seconds(self, duration_str: str) -> int:
        """ISO 8601形式の時間を秒数に変換"""
        try:
            import re
            pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
            match = re.match(pattern, duration_str)
            
            if not match:
                return 0
            
            hours, minutes, seconds = match.groups()
            total_seconds = 0
            total_seconds += int(hours) * 3600 if hours else 0
            total_seconds += int(minutes) * 60 if minutes else 0
            total_seconds += int(seconds) if seconds else 0
            
            return total_seconds
        except:
            return 0

    def search_youtube_videos_api(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        改良版YouTube動画検索（質の高い動画を優先選択）
        """
        try:
            # YouTube Data API v3 検索エンドポイント
            search_url = f"{self.youtube_base_url}/search"
            
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': max_results,
                'order': 'relevance',
                'regionCode': 'JP',
                'relevanceLanguage': 'ja',
                'key': self.youtube_api_key
            }
            
            print(f"🔍 YouTube API検索中: {query}")
            response = requests.get(search_url, params=params)
            
            if response.status_code != 200:
                print(f"❌ YouTube API エラー: {response.status_code}")
                return []
            
            data = response.json()
            
            if 'items' not in data or not data['items']:
                print("❌ 検索結果が見つかりませんでした")
                return []
            
            videos = []
            video_ids = []
            channel_ids = []
            
            # 動画IDとチャンネルIDを収集
            for item in data['items']:
                video_id = item['id']['videoId']
                channel_id = item['snippet']['channelId']
                video_ids.append(video_id)
                channel_ids.append(channel_id)
            
            # 動画の詳細情報とチャンネル詳細を並行取得
            video_details = self.get_video_details(video_ids)
            channel_details = self.get_channel_details(list(set(channel_ids)))
            
            for item in data['items']:
                video_id = item['id']['videoId']
                channel_id = item['snippet']['channelId']
                snippet = item['snippet']
                
                # 詳細情報を取得
                v_details = video_details.get(video_id, {})
                c_details = channel_details.get(channel_id, {})
                
                video_info = {
                    'title': snippet['title'],
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'video_id': video_id,
                    'channel_name': snippet['channelTitle'],
                    'channel_id': channel_id,
                    'channel_url': f"https://www.youtube.com/channel/{channel_id}",
                    'thumbnail': snippet['thumbnails'].get('high', {}).get('url', ''),
                    'description': snippet['description'][:200],
                    'published_at': snippet['publishedAt'][:10],
                    'views': self.format_number(v_details.get('viewCount', '0')),
                    'view_count_raw': v_details.get('viewCount', '0'),
                    'duration': self.format_duration(v_details.get('duration', 'PT0S')),
                    'subscriber_count': c_details.get('subscriberCount', '0'),
                    'subscriber_count_formatted': self.format_number(c_details.get('subscriberCount', '0')),
                    'category': self.determine_category(snippet['title'], snippet['description'])
                }
                
                videos.append(video_info)
            
            # 動画の質スコアを計算してソート
            for video in videos:
                video['quality_score'] = self.calculate_video_quality_score(video)
            
            # スコア順でソート（高い順）
            videos.sort(key=lambda x: x['quality_score'], reverse=True)
            
            print(f"✅ {len(videos)}本の動画を取得・品質評価完了")
            
            # 上位の質の高い動画のみを返す
            return videos[:min(10, len(videos))]
            
        except Exception as e:
            print(f"❌ YouTube API検索エラー: {e}")
            return []

    def get_video_details(self, video_ids: List[str]) -> Dict:
        """
        動画IDのリストから詳細情報を取得
        """
        try:
            videos_url = f"{self.youtube_base_url}/videos"
            
            params = {
                'part': 'statistics,contentDetails',
                'id': ','.join(video_ids),
                'key': self.youtube_api_key
            }
            
            response = requests.get(videos_url, params=params)
            
            if response.status_code != 200:
                print(f"❌ 動画詳細取得エラー: {response.status_code}")
                return {}
            
            data = response.json()
            details = {}
            
            for item in data.get('items', []):
                video_id = item['id']
                statistics = item.get('statistics', {})
                content_details = item.get('contentDetails', {})
                
                details[video_id] = {
                    'viewCount': statistics.get('viewCount', '0'),
                    'duration': content_details.get('duration', 'PT0S')
                }
            
            return details
            
        except Exception as e:
            print(f"❌ 動画詳細取得エラー: {e}")
            return {}

    def format_number(self, number_str: str) -> str:
        """数値を見やすい形式にフォーマット"""
        try:
            num = int(number_str)
            if num >= 1000000:
                return f"{num/1000000:.1f}M"
            elif num >= 1000:
                return f"{num/1000:.1f}K"
            else:
                return str(num)
        except:
            return number_str

    def format_duration(self, duration_str: str) -> str:
        """ISO 8601形式の時間を見やすい形式に変換"""
        try:
            import re
            
            pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
            match = re.match(pattern, duration_str)
            
            if not match:
                return "不明"
            
            hours, minutes, seconds = match.groups()
            
            hours = int(hours) if hours else 0
            minutes = int(minutes) if minutes else 0
            seconds = int(seconds) if seconds else 0
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes}:{seconds:02d}"
                
        except Exception as e:
            return "不明"

    def determine_category(self, title: str, description: str) -> str:
        """タイトルと概要からカテゴリを判定"""
        technical_keywords = ['IT', '資格', '技術', 'パスポート', 'ネットワーク', 'システム', 'エンジニア', 'プログラ']
        human_keywords = ['習慣', 'コミュニケーション', 'マナー', 'アドラー', '心理学', '話し方', '人間関係', 'ビジネス']
        ai_keywords = ['AI', '人工知能', '機械学習', 'ChatGPT', 'Claude', 'Gemini', 'データサイエンス', 'プロンプト', '生成AI', 'ディープラーニング']
        
        title_lower = title.lower()
        desc_lower = description.lower()
        
        tech_score = sum(1 for kw in technical_keywords if kw.lower() in title_lower or kw.lower() in desc_lower)
        human_score = sum(1 for kw in human_keywords if kw.lower() in title_lower or kw.lower() in desc_lower)
        ai_score = sum(1 for kw in ai_keywords if kw.lower() in title_lower or kw.lower() in desc_lower)
        
        if ai_score > tech_score and ai_score > human_score:
            return "AI・機械学習系"
        elif tech_score > human_score:
            return "技術系"
        elif human_score > tech_score:
            return "人間力系"
        else:
            return "総合"

    def format_video_post(self, videos: List[Dict], template: str, category_name: str) -> str:
        """
        改良版：見やすいChatwork投稿フォーマット
        """
        jst = timezone(timedelta(hours=9))
        current_time = datetime.now(jst).strftime("%Y年%m月%d日")
        weekday_name = ["月", "火", "水", "木", "金", "土", "日"][datetime.now(jst).weekday()]
        
        # ヘッダー部分の改良
        message = f"""
╔══════════════════════════════════════════════╗
║  {template}  ║
╚══════════════════════════════════════════════╝

📅 **{current_time}（{weekday_name}曜日）**
📂 **カテゴリ：** {category_name}

"""
        
        # カテゴリ説明の改良
        category_intro = self.get_enhanced_category_intro(category_name)
        message += f"{category_intro}\n\n"
        
        # 動画リスト部分の改良
        message += "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        message += "┃           📺 おすすめ動画リスト           ┃\n"
        message += "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        
        # 最大3本の高品質動画を選択
        selected_videos = videos[:3]  # 既にスコア順でソートされているため
        
        for i, video in enumerate(selected_videos, 1):
            # 動画セクションの区切り線
            message += f"{'─' * 50}\n"
            message += f"🎥 **動画 {i}：{video['title']}**\n"
            message += f"{'─' * 50}\n\n"
            
            # 品質インジケーター
            quality_score = video.get('quality_score', 0)
            quality_stars = "★" * min(5, int(quality_score / 20)) + "☆" * (5 - min(5, int(quality_score / 20)))
            message += f"⭐ **品質スコア：** {quality_stars} ({quality_score:.1f}/100点)\n\n"
            
            # チャンネル情報（登録者数を強調）
            subscriber_count = video.get('subscriber_count_formatted', '不明')
            message += f"📺 **チャンネル：** {video['channel_name']}\n"
            message += f"👥 **登録者数：** {subscriber_count}人\n\n"
            
            # 動画統計情報をテーブル形式で
            message += "📊 **動画情報**\n"
            message += "```\n"
            message += f"⏱️ 長さ     │ {video.get('duration', '不明')}\n"
            message += f"👀 再生数   │ {video.get('views', '不明')}\n"
            message += f"📅 投稿日   │ {video.get('published_at', '不明')}\n"
            message += f"🏷️ カテゴリ │ {video.get('category', '総合')}\n"
            message += "```\n\n"
            
            # 概要（改行で読みやすく）
            if video.get('description'):
                desc = video['description'][:150].replace('\n', ' ')
                message += f"📝 **概要**\n"
                message += f">{desc}{'...' if len(video['description']) > 150 else ''}\n\n"
            
            # ヘルプデスクでの活用ポイント
            importance_msg = self.get_enhanced_importance_message(video.get('category', ''), i)
            message += f"💡 **ヘルプデスクでの活用ポイント**\n"
            message += f"📌 {importance_msg}\n\n"
            
            # リンクセクション
            message += f"🔗 **アクセス**\n"
            message += f"   📹 [動画を見る]({video['url']})\n"
            message += f"   📺 [チャンネルを見る]({video['channel_url']})\n\n"
        
        # フッター部分
        message += "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        message += "┃           🎯 今日のアクション          ┃\n"
        message += "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        
        action_message = self.get_enhanced_daily_action_message(category_name)
        message += f"✅ {action_message}\n\n"
        
        # 最終メッセージ（社内用）
        message += "💪 **今日から社内で実践できること**\n"
        message += "• 1つの動画を最後まで視聴してメモを取る\n"
        message += "• 学んだ内容を社内業務で実際に試してみる\n"
        message += "• チームメンバーと情報共有し、知識を水平展開する\n\n"
        
        message += "🚀 **技術力 × コミュニケーション力 × AI活用力** で社内ITサポートの品質向上を実現しましょう！\n\n"
        
        # ハッシュタグ（社内用）
        hashtags = f"#社内ITサポート #{category_name.replace('・', '')} #スキルアップ #情報共有 #人材育成"
        message += f"{hashtags}"
        
        return message

    def get_enhanced_category_intro(self, category_name: str) -> str:
        """カテゴリ説明の強化版（社内情報共有用）"""
        intros = {
            "技術系": """🔧 **社内ITサポート品質向上のために**

技術的な知識とスキルは、社内ユーザーの問題を迅速に解決し、
業務継続性を保つための重要な基盤です。
本日のコンテンツは、特に社内スキルアップに適した
**高品質な学習リソース** です。""",
            
            "人間力系": """🌟 **社内コミュニケーション品質向上**

社内ユーザーやチームメンバーとの効果的なコミュニケーションは、
ITサポートの品質を大きく左右します。
心理学的アプローチやビジネスマナーを身につけ、
社内顧客満足度の向上を目指しましょう。""",
            
            "AI・機械学習系": """🤖 **社内AI活用で業務革新**

生成AIや機械学習技術を社内業務に取り入れることで、
体的業務の効率化と品質向上を実現できます。
ChatGPT、Claude、Geminiなどの最新AIツールを業務に活用し、
チーム全体の生産性向上を目指しましょう。"""
        }
        
        return intros.get(category_name, "🚀 **社内総合スキル向上**\n継続的な学習でチーム全体のスキルアップを目指しましょう。")

    def get_enhanced_importance_message(self, category: str, index: int) -> str:
        """動画の重要性を説明するメッセージの強化版（社内情報共有用）"""
        tech_messages = [
            "技術資格やスキルは社内ユーザーからの信頼を得るための重要な要素です。体系的な知識習得で社内ITサポートの品質を向上させましょう。",
            "システム知識があることで、社内システムの根本的な問題解決が可能になります。業務停止時間を短縮し、生産性向上に貢献できます。",
            "最新技術の理解は、将来の社内システム升級や新技術導入に備えるために重要です。先進的な知識でチームをリードしましょう。"
        ]
        
        human_messages = [
            "コミュニケーション力は、社内ユーザーの真のニーズを理解し、効果的なサポートを提供するために不可欠です。適切なヒアリングで業務効率を大幅に改善できます。",
            "心理学の知識は、ストレスを抱えた社内ユーザーへの適切な対応に活用できます。相手の状況を理解し、安心して相談できる環境を提供しましょう。",
            "ビジネスマナーは、社内各部署との連携や外部ベンダーとの交渉において、会社の信頼性を高める重要な要素です。"
        ]
        
        ai_messages = [
            "AI技術の理解と活用により、繰り返し業務の自動化や効率化が可能になり、より付加価値の高い業務に集中できます。社内生産性の大幅向上を実現しましょう。",
            "プロンプトエンジニアリングスキルで、AIツールを業務に効果的に組み込むことができます。複雑な社内システムの問題も段階的に解決できるようになります。",
            "生成AIを活用したマニュアル作成やFAQ整備により、社内ユーザーへのサポート品質を向上させられます。統一された情報提供で業務効率を改善しましょう。"
        ]
        
        if category == "技術系":
            return tech_messages[(index - 1) % len(tech_messages)]
        elif category == "AI・機械学習系":
            return ai_messages[(index - 1) % len(ai_messages)]
        else:
            return human_messages[(index - 1) % len(human_messages)]

    def get_enhanced_daily_action_message(self, category: str) -> str:
        """カテゴリ別の今日のアクションメッセージの強化版（社内用）"""
        messages = {
            "技術系": "今日は技術的な知識を一つ深堀りし、社内システムやテスト環境で実際に試してみましょう。学んだことを業務に活かせるスキルとして身につけてください。",
            "人間力系": "今日は社内ユーザーやチームメンバーとのコミュニケーションで、学んだ技術を一つ実践してみましょう。相手の反応や業務改善効果を確認してください。",
            "AI・機械学習系": "今日はAIツールを一つ社内業務に試してみましょう。具体的な業務シーンでの活用方法を想像し、実際のタスクで効果を確認してください。",
            "統合型": "技術的な問題解決、コミュニケーション配慮、AI活用を組み合わせた総合的なアプローチで社内サポート品質を向上させましょう。"
        }
        return messages.get(category, "学んだことを社内業務で実践し、チーム全体のスキル向上を心がけましょう。")

    def post_to_chatwork(self, message: str) -> bool:
        """チャットワークにメッセージを投稿"""
        url = f"{self.chatwork_base_url}/rooms/{self.room_id}/messages"
        headers = {
            "X-ChatWorkToken": self.api_token,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        # 先頭に [toall] を追加
        data = {"body": "[toall]\n" + message}
        
        try:
            print("📤 チャットワークに投稿中...")
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                print("✅ チャットワークに投稿完了")
                return True
            else:
                print(f"❌ 投稿失敗: {response.status_code}")
                print(f"エラー詳細: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 投稿エラー: {e}")
            return False

    def run_production_auto_post(self):
        """本番用自動投稿実行"""
        jst = timezone(timedelta(hours=9))
        current_time = datetime.now(jst)
        
        print(f"[{current_time}] 本番用自動投稿システム開始")
        
        # 平日チェック
        if current_time.weekday() >= 5:
            print("⏰ 今日は週末のため投稿をスキップします")
            return
        
        # カテゴリとキーワード選択
        keywords, templates, category_name = self.get_keywords_and_template()
        selected_keyword = random.choice(keywords)
        
        print(f"📂 選択カテゴリ: {category_name}")
        print(f"🔍 選択キーワード: {selected_keyword}")
        
        # YouTube APIで動画を検索（品質スコア付き）
        videos = self.search_youtube_videos_api(selected_keyword, max_results=20)
        
        if not videos:
            print("❌ 動画が見つかりませんでした")
            return
        
        # 品質スコアによる完全なフィルタリング（スコア70点以上の高品質動画のみ）
        high_quality_videos = [v for v in videos if v.get('quality_score', 0) >= 70]
        
        if not high_quality_videos:
            print("⚠️ 高品質動画が見つかりませんでした。基準を下げて再検索します。")
            # 基準を下げたフィルタリング
            high_quality_videos = [v for v in videos if v.get('quality_score', 0) >= 50]
            if not high_quality_videos:
                print("⚠️ 基準を下げても適切な動画が見つかりません。キーワードを変更して再検索してください。")
                return  # 投稿をスキップ
        
        print(f"✅ 高品質動画 {len(high_quality_videos)}本を選出")
        
        # テンプレート選択
        template = random.choice(templates)
        
        # 投稿内容作成
        message = self.format_video_post(high_quality_videos, template, category_name)
        
        # チャットワークに投稿
        success = self.post_to_chatwork(message)
        
        if success:
            print(f"✅ 投稿完了!")
            print(f"   - カテゴリ: {category_name}")
            print(f"   - キーワード: {selected_keyword}")
            print(f"   - 動画数: {min(3, len(high_quality_videos))}本")
            print(f"   - 平均品質スコア: {sum(v.get('quality_score', 0) for v in high_quality_videos[:3]) / min(3, len(high_quality_videos)):.1f}点")
        else:
            print("❌ 投稿失敗")

def main():
    """メイン実行関数"""
    # 環境変数から設定を取得
    chatwork_api_token = os.getenv('CHATWORK_API_TOKEN')
    chatwork_room_id = os.getenv('CHATWORK_ROOM_ID')
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    
    # 必要な環境変数チェック
    if not chatwork_api_token:
        print("❌ CHATWORK_API_TOKEN が設定されていません")
        return
    
    if not chatwork_room_id:
        print("❌ CHATWORK_ROOM_ID が設定されていません")
        return
    
    if not youtube_api_key:
        print("❌ YOUTUBE_API_KEY が設定されていません")
        return
    
    # 本番用システムのインスタンス作成
    production_poster = ProductionChatworkAutoPost(
        chatwork_api_token, 
        chatwork_room_id, 
        youtube_api_key
    )
    
    # 本番用自動投稿実行
    production_poster.run_production_auto_post()

if __name__ == "__main__":
    main()
