import os
import sys
import time
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

from tools.flight_tools import ALL_TOOLS
from harness.base_harness import FlightBookingHarness
from agents.react_agent import ReActFlightAgent
from agents.plan_execute_agent import PlanThenExecuteAgent
from agents.hybrid_agent import HybridFlightAgent

app = Flask(__name__)
app.secret_key = "flightai-btvn3-secret-key-pro"

# Khởi tạo Harness điều phối
harness = FlightBookingHarness(max_iterations=8)
harness.access.auto_approve = True

CURRENT_MODEL = os.getenv("GROQ_MODEL") or os.getenv("GOOGLE_MODEL") or "Groq (Qwen 3.8-27b)"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FlightAI — Hệ Thống Trợ Lý Đặt Vé Máy Bay Thông Minh</title>
  
  <!-- Fonts Google Inter & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  
  <!-- FontAwesome Icons -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  
  <!-- Marked.js để render Markdown và Bảng biểu -->
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

  <style>
    :root {
      --bg-base: #060913;
      --bg-surface: #0d1527;
      --bg-surface-elevated: #131f38;
      --bg-card: rgba(22, 36, 65, 0.55);
      --border-subtle: rgba(56, 189, 248, 0.12);
      --border-focus: rgba(56, 189, 248, 0.4);
      --primary: #38bdf8;
      --primary-glow: rgba(56, 189, 248, 0.25);
      --accent: #818cf8;
      --emerald: #34d399;
      --emerald-glow: rgba(52, 211, 153, 0.2);
      --amber: #fbbf24;
      --rose: #fb7185;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --bubble-user: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
      --bubble-bot: rgba(19, 31, 56, 0.85);
      --sidebar-width: 320px;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg-base);
      color: var(--text-main);
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background-image: 
        radial-gradient(circle at 15% 15%, rgba(56, 189, 248, 0.05) 0%, transparent 40%),
        radial-gradient(circle at 85% 85%, rgba(129, 140, 248, 0.05) 0%, transparent 40%);
    }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.2); border-radius: 9999px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(148, 163, 184, 0.35); }

    .app-header {
      height: 64px;
      background: rgba(13, 21, 39, 0.85);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-subtle);
      padding: 0 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      z-index: 20;
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .brand-icon {
      width: 40px;
      height: 40px;
      border-radius: 12px;
      background: linear-gradient(135deg, #0284c7 0%, #6366f1 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      color: white;
      box-shadow: 0 0 20px var(--primary-glow);
    }

    .brand-title h1 {
      font-size: 16px;
      font-weight: 700;
      letter-spacing: -0.3px;
      background: linear-gradient(135deg, #f8fafc 0%, #cbd5e1 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .brand-title p {
      font-size: 12px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .custom-select-wrap {
      position: relative;
      display: flex;
      align-items: center;
    }

    .custom-select {
      appearance: none;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      padding: 8px 32px 8px 14px;
      border-radius: 10px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      outline: none;
      transition: all 0.2s ease;
    }

    .custom-select:hover {
      border-color: var(--border-focus);
      box-shadow: 0 0 12px var(--primary-glow);
    }

    .select-arrow {
      position: absolute;
      right: 12px;
      pointer-events: none;
      font-size: 11px;
      color: var(--text-muted);
    }

    .status-pill {
      display: flex;
      align-items: center;
      gap: 7px;
      padding: 6px 12px;
      background: var(--emerald-glow);
      border: 1px solid rgba(52, 211, 153, 0.3);
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
      color: var(--emerald);
    }

    .status-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--emerald);
      box-shadow: 0 0 8px var(--emerald);
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.5; transform: scale(0.85); }
    }

    .app-body {
      display: flex;
      flex: 1;
      overflow: hidden;
      position: relative;
    }

    .sidebar {
      width: var(--sidebar-width);
      background: rgba(13, 21, 39, 0.7);
      backdrop-filter: blur(12px);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      padding: 20px;
      gap: 22px;
      overflow-y: auto;
    }

    .section-label {
      font-size: 11px;
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.8px;
      color: var(--primary);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .quick-chips {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .chip-btn {
      width: 100%;
      text-align: left;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      padding: 10px 14px;
      border-radius: 12px;
      font-size: 12.5px;
      line-height: 1.45;
      cursor: pointer;
      transition: all 0.25s ease;
      display: flex;
      align-items: flex-start;
      gap: 10px;
    }

    .chip-btn i {
      margin-top: 3px;
      font-size: 12px;
      color: var(--primary);
      opacity: 0.7;
    }

    .chip-btn:hover {
      background: rgba(56, 189, 248, 0.1);
      border-color: var(--primary);
      transform: translateY(-1px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }

    .metric-card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 14px;
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      backdrop-filter: blur(10px);
    }

    .metric-title {
      font-size: 11px;
      font-weight: 600;
      color: var(--text-muted);
    }

    .metric-val {
      font-size: 13.5px;
      font-weight: 600;
      color: #e2e8f0;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .harness-badge-list {
      display: grid;
      grid-template-columns: 1fr;
      gap: 6px;
    }

    .harness-badge-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 7px 12px;
      border-radius: 8px;
      background: rgba(11, 19, 35, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.04);
      font-size: 11.5px;
      color: var(--text-muted);
    }

    .harness-badge-item span.active-tag {
      color: var(--emerald);
      font-weight: 600;
      font-size: 10.5px;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .chat-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      position: relative;
      background: transparent;
    }

    .messages-scroll {
      flex: 1;
      overflow-y: auto;
      padding: 30px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    .msg-group {
      display: flex;
      gap: 14px;
      max-width: 84%;
      animation: msgAppear 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes msgAppear {
      from { opacity: 0; transform: translateY(12px) scale(0.98); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }

    .msg-group.user {
      align-self: flex-end;
      flex-direction: row-reverse;
    }

    .msg-group.bot {
      align-self: flex-start;
    }

    .avatar-box {
      width: 38px;
      height: 38px;
      border-radius: 12px;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 15px;
      font-weight: 600;
    }

    .msg-group.user .avatar-box {
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      color: white;
      box-shadow: 0 0 16px rgba(37, 99, 235, 0.35);
    }

    .msg-group.bot .avatar-box {
      background: linear-gradient(135deg, #0ea5e9, #10b981);
      color: white;
      box-shadow: 0 0 16px rgba(14, 165, 233, 0.35);
    }

    .bubble-wrapper {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .msg-bubble {
      padding: 16px 20px;
      border-radius: 18px;
      font-size: 14px;
      line-height: 1.68;
      word-break: break-word;
      position: relative;
    }

    .msg-group.user .msg-bubble {
      background: var(--bubble-user);
      color: #ffffff;
      border-bottom-right-radius: 4px;
      box-shadow: 0 4px 18px rgba(37, 99, 235, 0.25);
    }

    .msg-group.bot .msg-bubble {
      background: var(--bubble-bot);
      border: 1px solid var(--border-subtle);
      border-bottom-left-radius: 4px;
      backdrop-filter: blur(14px);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
    }

    /* Markdown Styling */
    .msg-bubble p { margin-bottom: 10px; }
    .msg-bubble p:last-child { margin-bottom: 0; }
    .msg-bubble strong { color: var(--primary); font-weight: 600; }
    .msg-bubble ul, .msg-bubble ol { margin-left: 20px; margin-bottom: 10px; }
    .msg-bubble li { margin-bottom: 4px; }
    
    .msg-bubble table {
      width: 100%;
      border-collapse: collapse;
      margin: 14px 0;
      font-size: 13px;
      border-radius: 10px;
      overflow: hidden;
      border: 1px solid var(--border-subtle);
    }

    .msg-bubble th {
      background: rgba(56, 189, 248, 0.15);
      color: var(--primary);
      text-align: left;
      padding: 10px 12px;
      font-weight: 600;
    }

    .msg-bubble td {
      padding: 8px 12px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      color: #cbd5e1;
    }

    .msg-bubble code {
      font-family: 'JetBrains Mono', monospace;
      font-size: 12.5px;
      background: rgba(15, 23, 42, 0.6);
      padding: 2px 6px;
      border-radius: 6px;
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.2);
    }

    .bubble-meta {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 11px;
      color: var(--text-dim);
      padding: 0 6px;
    }

    .action-icon-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 11px;
      padding: 2px 6px;
      border-radius: 4px;
      transition: all 0.2s ease;
    }

    .action-icon-btn:hover {
      color: var(--primary);
      background: rgba(56, 189, 248, 0.1);
    }

    .typing-box {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 14px 20px;
    }

    .typing-dot {
      width: 6.5px;
      height: 6.5px;
      background: var(--primary);
      border-radius: 50%;
      animation: bounceDot 1.2s infinite ease-in-out;
    }

    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes bounceDot {
      0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
      40% { transform: translateY(-7px); opacity: 1; }
    }

    .input-dock {
      padding: 18px 28px 24px;
      background: rgba(13, 21, 39, 0.85);
      backdrop-filter: blur(16px);
      border-top: 1px solid var(--border-subtle);
    }

    .input-frame {
      display: flex;
      align-items: flex-end;
      gap: 12px;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      padding: 10px 14px 10px 18px;
      transition: all 0.25s ease;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    .input-frame:focus-within {
      border-color: var(--primary);
      box-shadow: 0 0 24px rgba(56, 189, 248, 0.2);
    }

    #chatInput {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: var(--text-main);
      font-size: 14.5px;
      font-family: inherit;
      resize: none;
      max-height: 120px;
      line-height: 1.55;
    }

    #chatInput::placeholder { color: var(--text-dim); }

    .btn-send {
      width: 40px;
      height: 40px;
      border-radius: 12px;
      background: linear-gradient(135deg, #0284c7 0%, #6366f1 100%);
      border: none;
      color: white;
      font-size: 15px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
      flex-shrink: 0;
    }

    .btn-send:hover {
      transform: scale(1.05);
      box-shadow: 0 0 16px var(--primary-glow);
    }

    .btn-send:active { transform: scale(0.95); }
    .btn-send:disabled {
      opacity: 0.35;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }

    .input-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;
      padding: 0 4px;
      font-size: 11px;
      color: var(--text-dim);
    }

    .hero-welcome {
      margin: auto;
      text-align: center;
      max-width: 520px;
      padding: 40px 20px;
      animation: fadeIn 0.5s ease;
    }

    .hero-plane {
      width: 68px;
      height: 68px;
      border-radius: 20px;
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid var(--border-focus);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 32px;
      color: var(--primary);
      margin: 0 auto 20px;
      box-shadow: 0 0 30px var(--primary-glow);
    }

    .hero-welcome h2 {
      font-size: 22px;
      font-weight: 700;
      letter-spacing: -0.4px;
      margin-bottom: 10px;
    }

    .hero-welcome p {
      font-size: 14px;
      color: var(--text-muted);
      line-height: 1.6;
    }

    #toastNotice {
      position: fixed;
      bottom: 90px;
      right: 30px;
      background: rgba(15, 23, 42, 0.95);
      border: 1px solid var(--emerald);
      color: var(--emerald);
      padding: 10px 18px;
      border-radius: 10px;
      font-size: 13px;
      font-weight: 500;
      opacity: 0;
      transform: translateY(10px);
      transition: all 0.3s ease;
      pointer-events: none;
      z-index: 100;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    }

    #toastNotice.active {
      opacity: 1;
      transform: translateY(0);
    }
  </style>
</head>
<body>

  <!-- Top App Bar -->
  <header class="app-header">
    <div class="brand-group">
      <div class="brand-icon">
        <i class="fa-solid fa-plane-departure"></i>
      </div>
      <div class="brand-title">
        <h1>FlightAI Agent</h1>
        <p><i class="fa-solid fa-shield-halved" style="color:var(--emerald);"></i>Agentic Harness Framework</p>
      </div>
    </div>

    <div class="header-actions">
      <!-- Agent Pattern Selector -->
      <div class="custom-select-wrap">
        <select id="agentPicker" class="custom-select">
          <option value="react">⚡ ReAct Pattern (Khuyên dùng)</option>
          <option value="plan">📋 Plan-then-Execute</option>
          <option value="hybrid">🔀 Hybrid Pattern (Mẫu Lai)</option>
        </select>
        <i class="fa-solid fa-chevron-down select-arrow"></i>
      </div>

      <!-- Role Selector -->
      <div class="custom-select-wrap">
        <select id="rolePicker" class="custom-select">
          <option value="user">👤 Role: User</option>
          <option value="guest">👁 Role: Guest (Chỉ xem)</option>
          <option value="admin">👑 Role: Admin</option>
        </select>
        <i class="fa-solid fa-chevron-down select-arrow"></i>
      </div>

      <div class="status-pill">
        <div class="status-dot"></div>
        <span>Online</span>
      </div>
    </div>
  </header>

  <!-- Body -->
  <main class="app-body">
    <!-- Left Navigation Sidebar -->
    <aside class="sidebar">
      <div>
        <div class="section-label"><i class="fa-solid fa-bolt"></i> Câu hỏi thử nghiệm nhanh</div>
        <div class="quick-chips">
          <button class="chip-btn" onclick="sendPrompt(this)">
            <i class="fa-solid fa-magnifying-glass"></i>
            <span>Tìm vé từ SGN đến DAD ngày 2026-10-07 cho 1 người</span>
          </button>
          <button class="chip-btn" onclick="sendPrompt(this)">
            <i class="fa-solid fa-ticket"></i>
            <span>Đặt vé chuyến VN122 ngày 2026-10-07 cho Nguyen Van A SĐT 0901234567 hạng economy và thanh toán</span>
          </button>
          <button class="chip-btn" onclick="sendPrompt(this)">
            <i class="fa-solid fa-filter-dollar"></i>
            <span>Tìm và đặt chuyến rẻ nhất từ SGN đi DAD ngày 2026-10-07 dưới 2 triệu</span>
          </button>
          <button class="chip-btn" onclick="sendPrompt(this)">
            <i class="fa-solid fa-ban"></i>
            <span>Hủy booking mã BK9999 cho tôi</span>
          </button>
          <button class="chip-btn" onclick="sendPrompt(this)">
            <i class="fa-solid fa-circle-info"></i>
            <span>Thông tin sân bay DAD và số ghế chuyến VN201</span>
          </button>
        </div>
      </div>

      <div>
        <div class="section-label"><i class="fa-solid fa-sliders"></i> Cấu hình hoạt động</div>
        <div style="display:flex; flex-direction:column; gap:8px;">
          <div class="metric-card">
            <span class="metric-title">Kiến trúc suy luận</span>
            <span class="metric-val" id="activeAgentDisplay"><i class="fa-solid fa-code-fork" style="color:var(--primary);"></i> ReAct Pattern</span>
          </div>
          <div class="metric-card">
            <span class="metric-title">Mô hình LLM đang kết nối</span>
            <span class="metric-val" style="font-size:12.5px;"><i class="fa-solid fa-microchip" style="color:var(--accent);"></i> {{ current_model }}</span>
          </div>
        </div>
      </div>

      <!-- Hiển thị trọn vẹn 5 Modules của Lớp Harness -->
      <div>
        <div class="section-label"><i class="fa-solid fa-shield-check"></i> Bộ đệm Harness (5 Modules)</div>
        <div class="harness-badge-list">
          <div class="harness-badge-item">
            <span>🛡️ 1. AccessControl (RBAC & Duyệt)</span>
            <span class="active-tag"><i class="fa-solid fa-check"></i> ON</span>
          </div>
          <div class="harness-badge-item">
            <span>📏 2. DataConstraints (Xác thực)</span>
            <span class="active-tag"><i class="fa-solid fa-check"></i> ON</span>
          </div>
          <div class="harness-badge-item">
            <span>🔄 3. LoopDetector (Chặn bế tắc)</span>
            <span class="active-tag"><i class="fa-solid fa-check"></i> ON</span>
          </div>
          <div class="harness-badge-item">
            <span>✅ 4. CompletionCriteria (Soi DB)</span>
            <span class="active-tag"><i class="fa-solid fa-check"></i> ON</span>
          </div>
          <div class="harness-badge-item">
            <span>🤝 5. Handover (Bàn giao 30s)</span>
            <span class="active-tag"><i class="fa-solid fa-check"></i> ON</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Chat Feed -->
    <section class="chat-container">
      <div id="messagesFeed" class="messages-scroll">
        <div class="hero-welcome" id="heroWelcome">
          <div class="hero-plane">
            <i class="fa-solid fa-plane-up"></i>
          </div>
          <h2>Hệ Thống Trợ Lý Đặt Vé FlightAI</h2>
          <p>Trợ lý thông minh hỗ trợ tìm kiếm, so sánh giá vé, giữ chỗ và thanh toán tự động với đầy đủ lớp giám sát an toàn. Hãy gửi yêu cầu để bắt đầu!</p>
        </div>
      </div>

      <!-- Dock Input Bar -->
      <footer class="input-dock">
        <div class="input-frame">
          <textarea 
            id="chatInput" 
            rows="1" 
            placeholder="Nhập yêu cầu chuyến bay (Ví dụ: Đặt vé đi Đà Nẵng ngày 2026-10-07...)"
            onkeydown="checkEnterKey(event)"
            oninput="autoResize(this)"></textarea>
          <button id="sendBtn" class="btn-send" onclick="submitMessage()" title="Gửi tin nhắn">
            <i class="fa-solid fa-paper-plane"></i>
          </button>
        </div>
        <div class="input-footer">
          <span>Nhấn <b>Enter</b> để gửi tin, <b>Shift + Enter</b> để xuống dòng</span>
          <span id="timingIndicator"><i class="fa-regular fa-clock"></i> Sẵn sàng</span>
        </div>
      </footer>
    </section>
  </main>

  <div id="toastNotice">Đã sao chép vào bộ nhớ tạm!</div>

  <script>
    let isProcessing = false;

    const agentPicker = document.getElementById('agentPicker');
    const activeAgentDisplay = document.getElementById('activeAgentDisplay');

    agentPicker.addEventListener('change', function() {
      const names = {
        react: 'ReAct Pattern',
        plan: 'Plan-then-Execute',
        hybrid: 'Hybrid Pattern (Mẫu Lai)'
      };
      activeAgentDisplay.innerHTML = `<i class="fa-solid fa-code-fork" style="color:var(--primary);"></i> ${names[this.value]}`;
    });

    function autoResize(el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 120) + 'px';
    }

    function checkEnterKey(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submitMessage();
      }
    }

    function sendPrompt(btn) {
      const text = btn.querySelector('span').innerText;
      document.getElementById('chatInput').value = text;
      submitMessage();
    }

    function showToast(text = 'Đã sao chép vào bộ nhớ tạm!') {
      const toast = document.getElementById('toastNotice');
      toast.innerText = text;
      toast.classList.add('active');
      setTimeout(() => toast.classList.remove('active'), 2200);
    }

    function copyToClipboard(button, text) {
      navigator.clipboard.writeText(text).then(() => {
        showToast();
      });
    }

    function appendMessage(role, rawContent) {
      const feed = document.getElementById('messagesFeed');
      const hero = document.getElementById('heroWelcome');
      if (hero) hero.remove();

      const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const group = document.createElement('div');
      group.className = `msg-group ${role}`;

      const avatarIcon = role === 'user' 
        ? '<i class="fa-solid fa-user"></i>' 
        : '<i class="fa-solid fa-robot"></i>';

      // Parse markdown cho bot
      const renderedHtml = (role === 'bot') ? marked.parse(rawContent) : escapeText(rawContent);

      const copyBtnHtml = role === 'bot' 
        ? `<button class="action-icon-btn" onclick="copyToClipboard(this, \`${escapeJs(rawContent)}\`)" title="Sao chép"><i class="fa-regular fa-copy"></i> Sao chép</button>` 
        : '';

      group.innerHTML = `
        <div class="avatar-box">${avatarIcon}</div>
        <div class="bubble-wrapper">
          <div class="msg-bubble">${renderedHtml}</div>
          <div class="bubble-meta">
            <span>${timeStr}</span>
            ${copyBtnHtml}
          </div>
        </div>
      `;

      feed.appendChild(group);
      feed.scrollTop = feed.scrollHeight;
    }

    function showTypingIndicator() {
      const feed = document.getElementById('messagesFeed');
      const typingDiv = document.createElement('div');
      typingDiv.className = 'msg-group bot';
      typingDiv.id = 'activeTypingIndicator';
      typingDiv.innerHTML = `
        <div class="avatar-box"><i class="fa-solid fa-robot"></i></div>
        <div class="bubble-wrapper">
          <div class="msg-bubble typing-box">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
          </div>
        </div>
      `;
      feed.appendChild(typingDiv);
      feed.scrollTop = feed.scrollHeight;
    }

    function removeTypingIndicator() {
      const indicator = document.getElementById('activeTypingIndicator');
      if (indicator) indicator.remove();
    }

    function escapeText(str) {
      return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\\n/g, '<br>');
    }

    function escapeJs(str) {
      return str.replace(/`/g, '\\\\`').replace(/\\$/g, '\\\\$').replace(/"/g, '&quot;');
    }

    async function submitMessage() {
      if (isProcessing) return;
      const input = document.getElementById('chatInput');
      const text = input.value.trim();
      if (!text) return;

      const agent = document.getElementById('agentPicker').value;
      const role = document.getElementById('rolePicker').value;
      const timing = document.getElementById('timingIndicator');

      appendMessage('user', text);
      input.value = '';
      input.style.height = 'auto';

      isProcessing = true;
      document.getElementById('sendBtn').disabled = true;
      showTypingIndicator();

      const startTime = performance.now();
      timing.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Đang suy luận...`;

      try {
        const response = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, agent: agent, role: role })
        });

        const data = await response.json();
        removeTypingIndicator();

        const latency = ((performance.now() - startTime) / 1000).toFixed(1);
        timing.innerHTML = `<i class="fa-regular fa-clock"></i> Phản hồi trong ${latency}s`;

        if (data.error) {
          appendMessage('bot', `⚠️ **Lỗi hệ thống:** ${data.error}`);
        } else {
          appendMessage('bot', data.response);
        }
      } catch (err) {
        removeTypingIndicator();
        timing.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color:var(--rose);"></i> Mất kết nối`;
        appendMessage('bot', '❌ **Lỗi mạng:** Không thể kết nối tới server cục bộ. Vui lòng kiểm tra console.');
      }

      isProcessing = false;
      document.getElementById('sendBtn').disabled = false;
      input.focus();
    }
  </script>
</body>
</html>
"""


def get_agent(agent_type: str, role: str):
    if agent_type == "plan":
        return PlanThenExecuteAgent(tools=ALL_TOOLS, harness=harness, role=role)
    elif agent_type == "hybrid":
        return HybridFlightAgent(tools=ALL_TOOLS, harness=harness, role=role)
    else:
        return ReActFlightAgent(tools=ALL_TOOLS, harness=harness, role=role)


def extract_response(result: dict) -> str:
    from langchain_core.messages import AIMessage

    if result.get("response") and isinstance(result["response"], str):
        return result["response"]

    messages = result.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, str) and content.strip():
                return content
            if isinstance(content, list):
                texts = [c.get("text", "") for c in content if isinstance(c, dict)]
                text = " ".join(t for t in texts if t).strip()
                if text:
                    return text

    return "Yêu cầu đã được xử lý xong nhưng không có phản hồi bằng văn bản."


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, current_model=CURRENT_MODEL)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    agent_type = data.get("agent", "react")
    role = data.get("role", "user")

    if not user_message:
        return jsonify({"error": "Tin nhắn không được để trống."})

    try:
        agent = get_agent(agent_type, role)
        result = agent.run(user_message, role=role)
        response = extract_response(result)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("🚀 FLIGHTAI PRO WEB UI — ĐÃ KHỞI CHẠY THÀNH CÔNG!")
    print("📌 Mở trình duyệt tại: http://localhost:5000")
    print("   (Giao diện Dark Mode Glassmorphism + Render Markdown & Bảng)")
    print("=" * 65 + "\n")
    app.run(debug=False, port=5000, host="0.0.0.0")