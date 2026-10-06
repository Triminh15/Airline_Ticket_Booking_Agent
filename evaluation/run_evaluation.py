import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Thêm thư mục gốc vào đường dẫn import
sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv()

from tools.flight_tools import ALL_TOOLS
from harness.base_harness import FlightBookingHarness
from agents.react_agent import ReActFlightAgent
from agents.plan_execute_agent import PlanThenExecuteAgent
from agents.hybrid_agent import HybridFlightAgent
from evaluation.test_cases import TEST_CASES
from evaluation.metrics import compare_agents


def run_all():
    print("\n" + "=" * 70)
    print("  BTVN#3 — ĐÁNH GIÁ THỰC NGHIỆM 3 KIẾN TRÚC AGENT VỚI HARNESS")
    print("=" * 70 + "\n")

    # Khởi tạo Harness với auto_approve=True để chạy test tự động mượt mà
    harness = FlightBookingHarness(max_iterations=8)
    harness.access.auto_approve = True

    # Wrapper hàm chạy cho từng agent
    def react_runner(user_input: str, role: str = "user") -> dict:
        agent = ReActFlightAgent(tools=ALL_TOOLS, harness=harness, role=role)
        return agent.run(user_input, role=role)

    def plan_runner(user_input: str, role: str = "user") -> dict:
        agent = PlanThenExecuteAgent(tools=ALL_TOOLS, harness=harness, role=role)
        return agent.run(user_input, role=role)

    def hybrid_runner(user_input: str, role: str = "user") -> dict:
        agent = HybridFlightAgent(tools=ALL_TOOLS, harness=harness, role=role)
        return agent.run(user_input, role=role)

    # 1. Chạy ReAct
    react_suite = harness.run_suite(react_runner, TEST_CASES, agent_name="ReAct Pattern")

    # 2. Chạy Plan-then-Execute
    plan_suite = harness.run_suite(plan_runner, TEST_CASES, agent_name="Plan-then-Execute Pattern")

    # 3. Chạy Mẫu Lai
    hybrid_suite = harness.run_suite(hybrid_runner, TEST_CASES, agent_name="Hybrid Pattern")

    # 4. In bảng so sánh đối chiếu
    react_res = react_suite.to_dict()["results"]
    plan_res = plan_suite.to_dict()["results"]
    hybrid_res = hybrid_suite.to_dict()["results"]

    summary_text = compare_agents(react_res, plan_res, hybrid_res)
    print(summary_text)

    # 5. Lưu báo cáo ra file JSON
    output_data = {
        "ReAct": react_suite.to_dict(),
        "PlanThenExecute": plan_suite.to_dict(),
        "Hybrid": hybrid_suite.to_dict(),
    }

    results_file = Path(__file__).parent / "results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"📁 Dữ liệu đánh giá chi tiết đã được lưu thành công vào: {results_file}\n")


if __name__ == "__main__":
    run_all()