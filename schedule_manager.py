#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配信スケジュール管理Web UI
配信予定・配信内容・キーワード検索を管理し、動画配信を制御します。
"""

import os
import json
import uuid
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, send_from_directory

app = Flask(__name__)
SCHEDULES_FILE = Path(__file__).parent / "schedules.json"

WEEKDAY_NAMES = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]

DEFAULT_SCHEDULES = {
    "schedules": [
        {"id": "mon-0900", "weekday": 0, "time": "09:00", "name": "月曜: リーダーシップ", "keywords": ["コミュニケーション", "マネジメント", "リーダーシップ"], "description": "リーダーシップとチームマネジメントに関する学習コンテンツを配信します。"},
        {"id": "tue-0900", "weekday": 1, "time": "09:00", "name": "火曜: サイバー攻撃・セキュリティ", "keywords": ["サイバー攻撃", "セキュリティ", "ランサムウェア"], "description": "サイバーセキュリティと攻撃対策に関する学習コンテンツを配信します。"},
        {"id": "wed-0900", "weekday": 2, "time": "09:00", "name": "水曜: 組織・チーム", "keywords": ["チーム", "心理的安全性", "組織 チーム"], "description": "組織とチーム運営に関する学習コンテンツを配信します。"},
        {"id": "thu-0900", "weekday": 3, "time": "09:00", "name": "木曜: AI・技術トレンド", "keywords": ["AI", "機械学習", "人工知能"], "description": "AIと最新技術トレンドに関する学習コンテンツを配信します。"},
        {"id": "fri-0900", "weekday": 4, "time": "09:00", "name": "金曜: 生産性・働き方", "keywords": ["リモートワーク", "生産性働き方", "働き方"], "description": "生産性向上と新しい働き方に関する学習コンテンツを配信します。"},
    ]
}


def load_schedules():
    """schedules.json を読み込む"""
    if SCHEDULES_FILE.exists():
        with open(SCHEDULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"schedules": []}


def save_schedules(data):
    """schedules.json に保存"""
    with open(SCHEDULES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>配信スケジュール管理</title>
    <style>
        :root {
            --bg: #f8f9fa;
            --card: #fff;
            --text: #212529;
            --border: #dee2e6;
            --primary: #0d6efd;
            --danger: #dc3545;
            --success: #198754;
            --muted: #6c757d;
            --shadow: 0 1px 3px rgba(0,0,0,.08);
        }
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 24px; background: var(--bg); color: var(--text); line-height: 1.6; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { font-size: 1.5rem; margin-bottom: 24px; color: var(--text); }
        .card { background: var(--card); border-radius: 8px; padding: 24px; margin-bottom: 24px; box-shadow: var(--shadow); border: 1px solid var(--border); }
        .form-row { display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end; margin-bottom: 16px; }
        .form-group { display: flex; flex-direction: column; gap: 4px; }
        .form-group label { font-size: 0.875rem; color: var(--muted); font-weight: 500; }
        select, input[type="text"], input[type="number"] { padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 1rem; }
        select { min-width: 100px; }
        input[type="number"] { width: 56px; text-align: center; }
        .btn { padding: 8px 16px; border: none; border-radius: 6px; font-size: 0.9rem; cursor: pointer; font-weight: 500; transition: opacity .2s; }
        .btn:hover { opacity: .9; }
        .btn-primary { background: var(--primary); color: #fff; }
        .btn-danger { background: var(--danger); color: #fff; }
        .btn-secondary { background: var(--border); color: var(--text); }
        .btn-sm { padding: 6px 12px; font-size: 0.8rem; }
        .default-section { margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border); }
        .default-section p { font-size: 0.875rem; color: var(--muted); margin: 8px 0 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid var(--border); }
        th { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }
        td { vertical-align: middle; }
        .actions { display: flex; gap: 8px; flex-wrap: wrap; }
        .keyword-cell { max-width: 280px; word-break: break-word; }
        .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,.5); align-items: center; justify-content: center; z-index: 100; }
        .modal.show { display: flex; }
        .modal-content { background: var(--card); padding: 24px; border-radius: 8px; max-width: 400px; width: 90%; }
        .modal-content h3 { margin-top: 0; }
        .modal-content p { color: var(--muted); font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>スケジュール (何曜日の何時に配信するか)</h1>
        
        <div class="card">
            <form id="add-form">
                <div class="form-row">
                    <div class="form-group">
                        <label>曜日</label>
                        <select name="weekday" required>
                            <option value="0">月曜日</option>
                            <option value="1">火曜日</option>
                            <option value="2">水曜日</option>
                            <option value="3">木曜日</option>
                            <option value="4">金曜日</option>
                            <option value="5">土曜日</option>
                            <option value="6">日曜日</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>時刻</label>
                        <div style="display: flex; align-items: center; gap: 4px;">
                            <input type="number" name="hour" min="0" max="23" value="9" required>
                            <span>:</span>
                            <input type="number" name="minute" min="0" max="59" value="0" required>
                        </div>
                    </div>
                    <div class="form-group" style="flex: 1; min-width: 180px;">
                        <label>名前</label>
                        <input type="text" name="name" placeholder="例: 朝のニュース" required>
                    </div>
                    <div class="form-group" style="flex: 1; min-width: 200px;">
                        <label>キーワード（カンマ区切り）</label>
                        <input type="text" name="keywords" placeholder="例: AI, 機械学習, 人工知能" required>
                    </div>
                    <div class="form-group">
                        <label>&nbsp;</label>
                        <button type="submit" class="btn btn-primary">追加</button>
                    </div>
                </div>
            </form>
            <div class="default-section">
                <button type="button" class="btn btn-secondary" id="reset-default">デフォルトの紐付けに戻す</button>
                <p>デフォルトは各曜日3キーワード (月: リーダーシップ・マネジメント・コミュニケーションなど)</p>
            </div>
        </div>
        
        <div class="card">
            <table>
                <thead>
                    <tr>
                        <th>曜日</th>
                        <th>時刻</th>
                        <th>名前</th>
                        <th>キーワード</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody id="schedule-list"></tbody>
            </table>
        </div>
    </div>
    
    <div class="modal" id="desc-modal">
        <div class="modal-content">
            <h3 id="modal-title">説明</h3>
            <p id="modal-body"></p>
            <button class="btn btn-secondary" onclick="closeModal()">閉じる</button>
        </div>
    </div>
    
    <script>
        const WEEKDAYS = ['月曜日','火曜日','水曜日','木曜日','金曜日','土曜日','日曜日'];
        
        async function loadSchedules() {
            const res = await fetch('/api/schedules');
            const data = await res.json();
            renderTable(data.schedules);
        }
        
        function renderTable(schedules) {
            const tbody = document.getElementById('schedule-list');
            tbody.innerHTML = schedules.map(s => {
                const time = s.time || '09:00';
                const kw = Array.isArray(s.keywords) ? s.keywords.join('、') : s.keywords || '';
                const desc = (s.description || '説明はありません').replace(/"/g, '&quot;');
                const name = (s.name || '').replace(/"/g, '&quot;');
                return `<tr data-name="${name}" data-desc="${desc}" data-id="${s.id}">
                    <td>${WEEKDAYS[s.weekday]}</td>
                    <td>${time}</td>
                    <td>${escapeHtml(s.name)}</td>
                    <td class="keyword-cell">${escapeHtml(kw)}</td>
                    <td>
                        <div class="actions">
                            <button class="btn btn-secondary btn-sm btn-desc">説明</button>
                            <button class="btn btn-secondary btn-sm btn-edit">編集</button>
                            <button class="btn btn-danger btn-sm btn-delete">削除</button>
                        </div>
                    </td>
                </tr>`;
            }).join('');
            tbody.querySelectorAll('.btn-desc').forEach(btn => {
                btn.onclick = () => { const tr = btn.closest('tr'); showDesc(tr.dataset.name, tr.dataset.desc); };
            });
            tbody.querySelectorAll('.btn-delete').forEach(btn => {
                btn.onclick = () => deleteSchedule(btn.closest('tr').dataset.id);
            });
            tbody.querySelectorAll('.btn-edit').forEach(btn => {
                btn.onclick = () => editSchedule(btn.closest('tr').dataset.id);
            });
        }
        
        function escapeHtml(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
        
        document.getElementById('add-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const fd = new FormData(e.target);
            const hour = String(fd.get('hour')).padStart(2,'0');
            const minute = String(fd.get('minute')).padStart(2,'0');
            const keywords = String(fd.get('keywords')).split(/[,、]/).map(k => k.trim()).filter(Boolean);
            const data = {
                weekday: parseInt(fd.get('weekday')),
                time: `${hour}:${minute}`,
                name: fd.get('name'),
                keywords: keywords,
                description: ''
            };
            await fetch('/api/schedules', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
            await loadSchedules();
            e.target.reset();
        });
        
        document.getElementById('reset-default').addEventListener('click', async () => {
            if (!confirm('デフォルトのスケジュールに戻しますか？')) return;
            await fetch('/api/schedules/reset', { method: 'POST' });
            await loadSchedules();
        });
        
        async function deleteSchedule(id) {
            if (!confirm('このスケジュールを削除しますか？')) return;
            await fetch(`/api/schedules/${id}`, { method: 'DELETE' });
            await loadSchedules();
        }
        
        function showDesc(title, body) {
            document.getElementById('modal-title').textContent = title;
            document.getElementById('modal-body').textContent = body;
            document.getElementById('desc-modal').classList.add('show');
        }
        
        function closeModal() {
            document.getElementById('desc-modal').classList.remove('show');
        }
        
        function editSchedule(id) { alert('編集機能はキーワード・名前を変更して再追加し、古いスケジュールを削除してください。'); }
        
        loadSchedules();
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/schedules", methods=["GET"])
def get_schedules():
    return jsonify(load_schedules())


@app.route("/api/schedules", methods=["POST"])
def add_schedule():
    data = load_schedules()
    body = request.get_json() or {}
    schedule_id = body.get("id") or f"{body.get('weekday', 0)}-{body.get('time', '09:00').replace(':', '')}"
    entry = {
        "id": schedule_id,
        "weekday": int(body.get("weekday", 0)),
        "time": body.get("time", "09:00"),
        "name": body.get("name", "未設定"),
        "keywords": body.get("keywords", []),
        "description": body.get("description", ""),
    }
    existing = [s for s in data["schedules"] if s["id"] != entry["id"]]
    existing.append(entry)
    data["schedules"] = existing
    save_schedules(data)
    return jsonify(data)


@app.route("/api/schedules/<schedule_id>", methods=["DELETE"])
def delete_schedule(schedule_id):
    data = load_schedules()
    data["schedules"] = [s for s in data["schedules"] if s["id"] != schedule_id]
    save_schedules(data)
    return jsonify(data)


@app.route("/api/schedules/reset", methods=["POST"])
def reset_schedules():
    save_schedules(DEFAULT_SCHEDULES)
    return jsonify(DEFAULT_SCHEDULES)


if __name__ == "__main__":
    print("配信スケジュール管理UI: http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
