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
    MIXED = "mixed"

class ProductionChatworkAutoPost:
    def __init__(self, api_token: str, room_id: str, youtube_api_key: str):
        """
        本番用：YouTube API連携版チャットワーク自動投稿システム
        技術力×人間力の総合学習支援
        """
        self.api_token = api_token
        self.room_id = room_id
        self.youtube_api_key = youtube_api_key
        self.chatwork_base_url = "https://api.chatwork.com/v2"
        self.youtube_base_url = "https://www.googleapis.com/youtube/v3"
        
        # 🔧 技術系検索キーワード
        self.technical_keywords = [
            "ITパスポート 資格 取得方法 勉強法",
            "基本情報技術者 試験 勉強法 合格",
            "IT系常駐ヘルプデスク 資格 知識 スキル",
            "ヘルプデスク 仕事内容 スキル 必要な知識",
            "セキュリティ資格 情報セキュリティマネジメント",
            "MOS Excel Word PowerPoint 資格",
            "CCNA ネットワーク 資格 試験",
            "CompTIA A+ 資格 ハードウェア",
            "ITIL ファンデーション サービス管理",
            "Windows Server 管理 設定",
            "ネットワーク トラブルシューティング 方法",
            "Active Directory 設定 管理"
        ]
        
        # 🎯 人間力系検索キーワード
        self.human_skills_keywords = [
            "7つの習慣 ビジネス 自己啓発 スティーブン・コヴィー",
            "アドラー心理学 嫌われる勇気 課題の分離",
            "ビジネスマナー コミュニケーション 自己啓発",
            "人は話し方が9割 コミュニケーション術",
            "好かれる人の言葉選び ビジネス会話",
            "話しかけたくなる人 コミュニケーション スキル",
            "ビジネス敬語 話し方 マナー",
            "職場 人間関係 改善方法",
            "リーダーシップ マネジメント スキル",
            "問題解決思考 論理的思考 方法",
            "ストレス管理 メンタルヘルス 職場",
            "チームワーク 協調性 向上"
        ]
        
        # 📈 技術系投稿テンプレート
        self.technical_templates = [
            "🔧 今日のIT技術学習コンテンツ",
            "💻 スキルアップに役立つ技術動画！",
            "⚡ IT系ヘルプデスクを目指す方必見！",
            "🚀 技術力向上のための学習リソース",
            "📚 資格取得に向けた学習動画をご紹介",
            "🎯 実務で活かせるIT知識を学ぼう！"
        ]
        
        # 💡 人間力系投稿テンプレート
        self.human_skills_templates = [
            "🌟 人間力アップ！自己成長コンテンツ",
            "💬 コミュニケーション力向上の秘訣",
            "🎭 ビジネスパーソンとしての人間力を磨こう",
            "🤝 職場での人間関係を良好にするヒント",
            "💪 内面から成長！自己啓発コンテンツ",
            "🧠 心理学で学ぶ人間関係の極意"
        ]

    def get_category_by_day(self) -> ContentCategory:
        """曜日ベースのカテゴリ選択（平日のみ実行）"""
        jst = timezone(timedelta(hours=9))
        today = datetime.now(jst).weekday()
        
        if today < 5:  # 平日（月〜金）
            # 70%技術系、30%人間力系
            return random.choices(
                [ContentCategory.TECHNICAL, ContentCategory.HUMAN_SKILLS],
                weights=[0.7, 0.3]
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
        else:
            return (
                self.technical_keywords + self.human_skills_keywords,
                [],
                "統合型"
            )

    def search_youtube_videos_api(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        実際のYouTube Data API v3を使って動画を検索
        """
        try:
            # YouTube Data API v3 検索エンドポイント
            search_url = f"{self.youtube_base_url}/search"
            
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': max_results,
                'order': 'relevance',  # 関連度順
                'regionCode': 'JP',    # 日本
                'relevanceLanguage': 'ja',  # 日本語
                'key': self.youtube_api_key
            }
            
            print(f"🔍 YouTube API検索中: {query}")
            response = requests.get(search_url, params=params)
            
            if response.status_code != 200:
                print(f"❌ YouTube API エラー: {response.status_code}")
                print(f"エラー詳細: {response.text}")
                return []
            
            data = response.json()
            
            if 'items' not in data or not data['items']:
                print("❌ 検索結果が見つかりませんでした")
                return []
            
            videos = []
            video_ids = []
            
            # 動画IDを収集
            for item in data['items']:
                video_id = item['id']['videoId']
                video_ids.append(video_id)
            
            # 動画の詳細情報を取得（再生数、長さなど）
            video_details = self.get_video_details(video_ids)
            
            for i, item in enumerate(data['items']):
                video_id = item['id']['videoId']
                snippet = item['snippet']
                
                # 詳細情報を取得
                details = video_details.get(video_id, {})
                
                video_info = {
                    'title': snippet['title'],
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'video_id': video_id,
                    'channel_name': snippet['channelTitle'],
                    'channel_url': f"https://www.youtube.com/channel/{snippet['channelId']}",
                    'thumbnail': snippet['thumbnails'].get('high', {}).get('url', ''),
                    'description': snippet['description'][:200],  # 最初の200文字
                    'published_at': snippet['publishedAt'][:10],  # YYYY-MM-DD
                    'views': self.format_number(details.get('viewCount', '0')),
                    'duration': self.format_duration(details.get('duration', 'PT0S')),
                    'category': self.determine_category(snippet['title'], snippet['description'])
                }
                
                videos.append(video_info)
            
            print(f"✅ {len(videos)}本の動画を取得しました")
            return videos
            
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
            # PT1H30M45S -> 1:30:45
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
        
        title_lower = title.lower()
        desc_lower = description.lower()
        
        tech_score = sum(1 for kw in technical_keywords if kw.lower() in title_lower or kw.lower() in desc_lower)
        human_score = sum(1 for kw in human_keywords if kw.lower() in title_lower or kw.lower() in desc_lower)
        
        if tech_score > human_score:
            return "技術系"
        elif human_score > tech_score:
            return "人間力系"
        else:
            return "総合"

    def format_video_post(self, videos: List[Dict], template: str, category_name: str) -> str:
        """カテゴリに応じた投稿フォーマット"""
        jst = timezone(timedelta(hours=9))
        current_time = datetime.now(jst).strftime("%Y年%m月%d日")
        weekday_name = ["月", "火", "水", "木", "金", "土", "日"][datetime.now(jst).weekday()]
        
        # カテゴリ別のヘッダーメッセージ
        category_intro = {
            "技術系": "💼 **IT系ヘルプデスクに必要な技術力**\n技術的な知識とスキルは、お客様の問題を迅速に解決するための基盤です。",
            "人間力系": "🌟 **IT系ヘルプデスクに必要な人間力**\nお客様と直接対話するヘルプデスクでは、技術力と同じくらい人間力が重要です。",
            "統合型": "⚖️ **技術力×人間力のバランス**\n優秀なヘルプデスクエンジニアは、技術的解決力と人間的対応力を兼ね備えています。"
        }.get(category_name, "🚀 **総合スキル向上**")
        
        message = f"{template}\n\n"
        message += f"📅 {current_time}（{weekday_name}曜日）\n"
        message += f"📂 カテゴリ: {category_name}\n\n"
        message += f"{category_intro}\n\n"
        
        # 最大3本の動画を選択
        selected_videos = random.sample(videos, min(3, len(videos)))
        
        for i, video in enumerate(selected_videos, 1):
            message += f"━━━━━━━━━━━━━━━━━━━━━━\n"
            message += f"📺 **{i}. {video['title']}**\n\n"
            
            # カテゴリバッジ
            category_emoji = "🔧" if video.get('category') == '技術系' else "💡"
            message += f"{category_emoji} カテゴリ: {video.get('category', '総合')}\n\n"
            
            # サムネイル
            if video.get('thumbnail'):
                message += f"🖼️ サムネイル: {video['thumbnail']}\n\n"
            
            # 基本情報
            message += f"📊 **基本情報**\n"
            message += f"⏱️ 長さ: {video.get('duration', '不明')}\n"
            message += f"👀 再生数: {video.get('views', '不明')}\n"
            message += f"📅 投稿日: {video.get('published_at', '不明')}\n\n"
            
            # 概要
            if video.get('description'):
                desc = video['description'][:120] + "..." if len(video['description']) > 120 else video['description']
                message += f"📝 **概要**\n{desc}\n\n"
            
            # なぜこの動画が重要か
            importance_msg = self.get_importance_message(video.get('category', ''), i)
            message += f"💭 **ヘルプデスクでの活用**\n{importance_msg}\n\n"
            
            # リンク情報
            message += f"🔗 **リンク**\n"
            message += f"📹 動画URL: {video['url']}\n"
            if video.get('channel_url'):
                message += f"📺 チャンネル: {video['channel_name']} - {video['channel_url']}\n\n"
        
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"🎯 **本日のアクション**\n"
        message += self.get_daily_action_message(category_name)
        message += "\n\n💪 技術力と人間力、両方を磨いて最強のヘルプデスクエンジニアを目指しましょう！\n"
        message += f"#ITヘルプデスク #{category_name} #スキルアップ #IT学習 #人間力"
        
        return message

    def get_importance_message(self, category: str, index: int) -> str:
        """動画の重要性を説明するメッセージ"""
        tech_messages = [
            "技術資格は信頼性の証明となり、お客様からの信頼獲得につながります。",
            "システム知識があることで、より深い問題解決が可能になります。",
            "最新技術の理解は、現代的な問題への対応力を高めます。"
        ]
        
        human_messages = [
            "コミュニケーション力は、お客様の真の困りごとを引き出すために必須です。",
            "心理学の知識は、ストレスの多いお客様への適切な対応に活かされます。",
            "ビジネスマナーは、プロフェッショナルとしての印象を決定づけます。"
        ]
        
        if category == "技術系":
            return tech_messages[(index - 1) % len(tech_messages)]
        else:
            return human_messages[(index - 1) % len(human_messages)]

    def get_daily_action_message(self, category: str) -> str:
        """カテゴリ別の今日のアクションメッセージ"""
        messages = {
            "技術系": "今日は技術的な知識を一つ深堀りしてみましょう。学んだことをすぐに実践で活かすことを意識してください。",
            "人間力系": "今日は同僚やお客様との会話で、学んだコミュニケーション技術を一つ試してみましょう。",
            "統合型": "技術的な問題解決と同時に、お客様への配慮も忘れずに。両方のバランスを意識した対応を心がけましょう。"
        }
        return messages.get(category, "学んだことを実践で活かしていきましょう。")

    def post_to_chatwork(self, message: str) -> bool:
        """チャットワークにメッセージを投稿"""
        url = f"{self.chatwork_base_url}/rooms/{self.room_id}/messages"
        headers = {
            "X-ChatWorkToken": self.api_token,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"body": message}
        
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
        
        # YouTube APIで動画を検索
        videos = self.search_youtube_videos_api(selected_keyword, max_results=10)
        
        if not videos:
            print("❌ 動画が見つかりませんでした")
            return
        
        # テンプレート選択
        template = random.choice(templates)
        
        # 投稿内容作成
        message = self.format_video_post(videos, template, category_name)
        
        # チャットワークに投稿
        success = self.post_to_chatwork(message)
        
        if success:
            print(f"✅ 投稿完了!")
            print(f"   - カテゴリ: {category_name}")
            print(f"   - キーワード: {selected_keyword}")
            print(f"   - 動画数: {min(3, len(videos))}本")
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