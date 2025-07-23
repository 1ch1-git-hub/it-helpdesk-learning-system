#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def test_env_variables():
    """環境変数の確認"""
    print("🔍 環境変数チェック:")
    
    chatwork_token = os.getenv('CHATWORK_API_TOKEN')
    chatwork_room = os.getenv('CHATWORK_ROOM_ID')
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    
    print(f"Chatwork Token: {'✅ 設定済み' if chatwork_token else '❌ 未設定'}")
    print(f"Chatwork Room: {'✅ 設定済み' if chatwork_room else '❌ 未設定'}")
    print(f"YouTube API Key: {'✅ 設定済み' if youtube_key else '❌ 未設定'}")
    
    if all([chatwork_token, chatwork_room, youtube_key]):
        print("✅ すべての環境変数が設定されています")
        return True
    else:
        print("❌ 必要な環境変数が不足しています")
        return False

if __name__ == "__main__":
    test_env_variables()
