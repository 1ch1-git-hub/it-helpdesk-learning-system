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
        
        # 🔧 技術系検索キーワード（シンプル版）
        self.technical_keywords = [
            "ITパスポート",
            "基本情報技術者",
            "ヘルプデスク",
            "CCNA",
            "CompTIA A+",
            "ITIL",
            "Windows Server",
            "ネットワーク"
        ]
        
        # 🎯 人間力系検索キーワード（シンプル版）
        self.human_skills_keywords = [
            "7つの習慣",
            "アドラー心理学",
            "ビジネスマナー",
            "コミュニケーション",
            "話し方",
            "リーダーシップ",
            "問題解決",
            "チームワーク"
        ]
        
        # 🤖 AI・機械学習系検索キーワード（シンプル版）
        self.ai_ml_keywords = [
            # 🔥 主要AIサービス
            "ChatGPT",
            "Claude",
            "Gemini",
            "Copilot",
            "DeepSeek",
            
            # 🎯 AI基礎
            "AI 基礎",
            "機械学習",
            "生成AI",
            "Python AI",
            
            # 🚀 実用スキル
            "プロンプト",
            "AI 活用",
            "データ分析",
            "AI ヘルプデスク"
        ]
        
        # 📈 技術系投稿テンプレート（シンプル版）
        self.technical_templates = [
            "IT学習動画",
            "技術スキル向上",
            "資格取得サポート"
        ]
        
        # 💡 人間力系投稿テンプレート（シンプル版）
        self.human_skills_templates = [
            "コミュニケーション向上",
            "人間力アップ",
            "職場での成長"
        ]
        
        # 🤖 AI・機械学習系投稿テンプレート（シンプル版）
        self.ai_ml_templates = [
            "AI活用術",
            "機械学習入門",
            "生成AI実践"
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
        動画の質を数値化してスコア算出
        """
        score = 0.0
        
        # 登録者数スコア (最大30点)
        subscriber_count = int(video.get('subscriber_count', '0'))
        if subscriber_count >= 100000:  # 10万人以上
            score += 30
        elif subscriber_count >= 50000:  # 5万人以上
            score += 25
        elif subscriber_count >= 10000:  # 1万人以上
            score += 20
        elif subscriber_count >= 1000:   # 1000人以上
            score += 10
        
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
        
        # 動画の長さスコア (最大20点) - 短すぎず長すぎない動画を優先
        duration_seconds = self.parse_duration_to_seconds(video.get('duration', 'PT0S'))
        if 300 <= duration_seconds <= 1800:  # 5分〜30分
            score += 20
        elif 180 <= duration_seconds <= 300:  # 3分〜5分
            score += 15
        elif 1800 <= duration_seconds <= 3600:  # 30分〜1時間
            score += 15
        
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
        シンプル版：見やすいChatwork投稿フォーマット
        """
        jst = timezone(timedelta(hours=9))
        current_time = datetime.now(jst).strftime("%m月%d日")
        weekday_name = ["月", "火", "水", "木", "金", "土", "日"][datetime.now(jst).weekday()]
        
        # シンプルなヘッダー
        message = f"""
🎯 **【{current_time}({weekday_name}) {category_name}】おすすめ学習動画**

{self.get_simple_category_intro(category_name)}

"""
        
        # 動画リスト（最大2本まで）
        selected_videos = videos[:2]
        
        for i, video in enumerate(selected_videos, 1):
            message += f"📹 **動画{i}：{video['title']}**\n"
            message += f"📺 {video['channel_name']} ({video.get('subscriber_count_formatted', '不明')}人)\n"
            message += f"⏰ {video.get('duration', '不明')} | 👀 {video.get('views', '不明')}\n"
            message += f"🔗 {video['url']}\n\n"
        
        # シンプルなアクション
        message += f"💡 **今日のポイント**\n{self.get_simple_action_message(category_name)}\n\n"
        
        # ハッシュタグ
        message += f"#ITヘルプデスク #{category_name.replace('・', '')} #学習"
        
        return message

    def get_simple_category_intro(self, category_name: str) -> str:
        """シンプルなカテゴリ説明"""
        intros = {
            "技術系": "🔧 ヘルプデスクに必要なIT技術スキルを学びましょう！",
            "人間力系": "🌟 お客様対応に活かせるコミュニケーション力を向上させましょう！",
            "AI・機械学習系": "🤖 AIツールを活用して業務効率化を図りましょう！"
        }
        return intros.get(category_name, "📚 継続的な学習でスキルアップしていきましょう！")

    def get_simple_action_message(self, category_name: str) -> str:
        """シンプルなアクションメッセージ"""
        messages = {
            "技術系": "動画で学んだ技術を実際に試してみて、理解を深めましょう。",
            "人間力系": "学んだコミュニケーション技術を今日の業務で実践してみましょう。",
            "AI・機械学習系": "紹介されたAIツールを一つ試して、業務での活用方法を考えてみましょう。"
        }
        return messages.get(category_name, "動画の内容を実務で活かしてスキルアップしましょう。")

    def get_enhanced_category_intro(self, category_name: str) -> str:
        """カテゴリ説明の強化版"""
        intros = {
            "技術系": """🔧 **IT系ヘルプデスクに必要な技術力**

技術的な知識とスキルは、お客様の問題を迅速に解決するための基盤です。
今日選出した動画は、登録者数・再生数・内容の質を総合的に評価した
**高品質コンテンツ** です。""",
            
            "人間力系": """🌟 **IT系ヘルプデスクに必要な人間力**

お客様と直接対話するヘルプデスクでは、技術力と同じくらい人間力が重要です。
コミュニケーション能力や心理学的アプローチを学ぶことで、
より効果的なサポートが提供できるようになります。""",
            
            "AI・機械学習系": """🤖 **AI時代のヘルプデスクエンジニア**

生成AIや機械学習技術を活用することで、より効率的で高度な問題解決が可能になります。
ChatGPTやClaude、Geminiなどの最新AIツールを使いこなし、
業務の自動化と質の向上を実現しましょう。"""
        }
        
        return intros.get(category_name, "🚀 **総合スキル向上**\n継続的な学習で着実にスキルアップしていきましょう。")

    def get_enhanced_importance_message(self, category: str, index: int) -> str:
        """動画の重要性を説明するメッセージの強化版"""
        tech_messages = [
            "技術資格は信頼性の証明となり、お客様からの信頼獲得につながります。体系的な知識習得で問題解決力を向上させましょう。",
            "システム知識があることで、より深い問題解決が可能になります。根本原因の特定と効率的な解決策の提案ができるようになります。",
            "最新技術の理解は、現代的な問題への対応力を高めます。技術トレンドを把握することで、お客様により良いアドバイスができます。"
        ]
        
        human_messages = [
            "コミュニケーション力は、お客様の真の困りごとを引き出すために必須です。適切な質問と傾聴スキルでより良いサポートを提供できます。",
            "心理学の知識は、ストレスの多いお客様への適切な対応に活かされます。相手の心理状態を理解し、安心感を与える対応ができるようになります。",
            "ビジネスマナーは、プロフェッショナルとしての印象を決定づけます。第一印象と継続的な信頼関係構築の基盤となります。"
        ]
        
        ai_messages = [
            "AI技術の理解により、自動化可能な作業を特定し、より高度な問題に集中できます。効率化と質の向上を同時に実現できます。",
            "プロンプトエンジニアリングスキルで、AIツールを効果的に活用した問題解決が可能です。複雑な問題も段階的に解決できるようになります。",
            "生成AIを活用することで、お客様への説明資料作成や回答の質を向上させられます。分かりやすい説明で顧客満足度を向上させましょう。"
        ]
        
        if category == "技術系":
            return tech_messages[(index - 1) % len(tech_messages)]
        elif category == "AI・機械学習系":
            return ai_messages[(index - 1) % len(ai_messages)]
        else:
            return human_messages[(index - 1) % len(human_messages)]

    def get_enhanced_daily_action_message(self, category: str) -> str:
        """カテゴリ別の今日のアクションメッセージの強化版"""
        messages = {
            "技術系": "今日は技術的な知識を一つ深堀りしてみましょう。学んだことをラボ環境で実際に試し、実践スキルとして身につけてください。",
            "人間力系": "今日は同僚やお客様との会話で、学んだコミュニケーション技術を一つ試してみましょう。相手の反応を観察し、効果を確認してください。",
            "AI・機械学習系": "今日はAIツールを一つ試してみましょう。業務での活用シーンを具体的に想像し、実際のタスクに適用してみてください。",
            "統合型": "技術的な問題解決、人間的な配慮、AI活用を組み合わせた最適なアプローチを意識して取り組みましょう。"
        }
        return messages.get(category, "学んだことを実践で活かし、継続的なスキル向上を心がけましょう。")

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
        
        # 品質スコアによるフィルタリング（スコア50点以上の動画のみ選択）
        high_quality_videos = [v for v in videos if v.get('quality_score', 0) >= 50]
        
        if not high_quality_videos:
            print("⚠️ 高品質動画が見つかりませんでした。全動画から選択します。")
            high_quality_videos = videos
        
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
