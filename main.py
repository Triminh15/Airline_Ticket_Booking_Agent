import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load env và setup path
load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from tools.flight_tools import ALL_TOOLS
from harness.base_harness import FlightBookingHarness
from agents.react_agent import ReActFlightAgent
from agents.plan_execute_agent import PlanThenExecuteAgent
from agents.hybrid_agent import HybridFlightAgent

BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║              🛫  FlightAI — Hệ Thống Đặt Vé Máy Bay              ║
║       SE373 Agent Fundamentals | UIT - ĐHQG-HCM (BTVN#3)         ║
╚══════════════════════════════════════════════════════════════════╝
"""

AGENT_CHOICES = {
    "1": ("ReAct Pattern", ReActFlightAgent, "Suy luận -> Hành động -> Quan sát liên tục linh hoạt"),
    "2": ("Plan-then-Execute Pattern", PlanThenExecuteAgent, "Lập kế hoạch trước, thực thi tuần tự có Replanning"),
    "3": ("Hybrid Pattern (Mẫu Lai)", HybridFlightAgent, "High-level Goals + ReAct cấp dưới kèm Human Handover"),
}

EXAMPLE_QUERIES = [
    "Tìm vé từ SGN đến DAD sáng ngày 2026-10-07 cho 1 người",
    "Đặt vé chuyến VN122 ngày 2026-10-07 cho Nguyen Van A SĐT 0901234567 hạng economy và thanh toán",
    "Tìm và đặt chuyến rẻ nhất từ SGN đi DAD ngày 2026-10-07 dưới 2 triệu",
    "Hủy booking mã BK9999 cho tôi",
    "Thông tin sân bay DAD và kiểm tra chuyến VN201 còn bao nhiêu ghế trống?",
]


def check_environment():
    """Kiểm tra sự tồn tại của API keys."""
    groq_key = os.getenv("GROQ_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    if groq_key:
        print(f"🔑 Đã nạp GROQ_API_KEY thành công (***{groq_key[-4:]})")
    else:
        print("⚠️  CẢNH BÁO: Chưa tìm thấy GROQ_API_KEY trong file .env!")
        print("   Hãy chắc chắn file .env ở thư mục gốc có chứa API key hợp lệ.\n")


def run_cli():
    print(BANNER)
    check_environment()

    # Khởi tạo Harness điều phối
    # Trong môi trường tương tác thật, auto_approve=False để kích hoạt hỏi người dùng 
    harness = FlightBookingHarness(max_iterations=8)
    harness.access.auto_approve = False

    # 1. Chọn Role (RBAC)
    print("\n👤 [BƯỚC 1] Chọn Vai Trò (Role) của bạn:")
    print("  [1] guest  — Khách vãng lai (Chỉ xem và tra cứu thông tin)")
    print("  [2] user   — Người dùng (Đặt chỗ, tra cứu, hủy vé)")
    print("  [3] admin  — Quản trị viên (Toàn quyền hệ thống)")

    role_map = {"1": "guest", "2": "user", "3": "admin"}
    role = "user"
    while True:
        choice = input("👉 Nhập số (1/2/3) [Mặc định 2]: ").strip()
        if not choice:
            choice = "2"
        if choice in role_map:
            role = role_map[choice]
            print(f"✅ Vai trò hiện tại: {role.upper()}")
            break
        print("❌ Lựa chọn không hợp lệ, vui lòng thử lại.")

    # 2. Chọn Kiến Trúc Agent
    print("\n🧠 [BƯỚC 2] Chọn Mẫu Thiết Kế Agent:")
    for k, (name, _, desc) in AGENT_CHOICES.items():
        print(f"  [{k}] {name:<26} — {desc}")

    agent_instance = None
    while True:
        choice = input("👉 Nhập số (1/2/3) [Mặc định 1]: ").strip()
        if not choice:
            choice = "1"
        if choice in AGENT_CHOICES:
            name, agent_cls, _ = AGENT_CHOICES[choice]
            print(f"✅ Đã chọn kiến trúc: {name}")
            agent_instance = agent_cls(tools=ALL_TOOLS, harness=harness, role=role)
            break
        print("❌ Lựa chọn không hợp lệ, vui lòng thử lại.")

    # 3. Hướng dẫn và Câu hỏi mẫu
    print("\n💡 Gợi ý câu lệnh mẫu:")
    for idx, q in enumerate(EXAMPLE_QUERIES, 1):
        print(f"   {idx}. {q}")

    print("\n" + "─" * 66)
    print("💬 Nhập yêu cầu đặt vé của bạn (Gõ 'exit' hoặc 'quit' để thoát)")
    print("─" * 66)

    # 4. Vòng lặp REPL
    while True:
        try:
            user_input = input("\n🧑 Bạn: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Tạm biệt!")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "thoát", "bye"]:
            print("👋 Cảm ơn bạn đã sử dụng FlightAI. Tạm biệt!")
            break

        print(f"\n⚙️  Agent ({agent_instance.agent_name}) đang suy luận & gọi tools qua Harness...")

        try:
            # Truyền đúng role vào lời gọi run
            result = agent_instance.run(user_input, role=role)

            messages = result.get("messages", [])
            from langchain_core.messages import AIMessage

            # Trích xuất phản hồi cuối
            final_response = result.get("response", "")
            if not final_response:
                for msg in reversed(messages):
                    if isinstance(msg, AIMessage) and isinstance(msg.content, str) and msg.content.strip():
                        final_response = msg.content
                        break

            print(f"\n🤖 Agent:\n{final_response or '(Đã hoàn thành nhưng không có tin nhắn phản hồi)'}")

        except Exception as e:
            print(f"\n❌ Lỗi thực thi: {e}")
            if "--debug" in sys.argv:
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    run_cli()