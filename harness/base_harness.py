import time
import json
from dataclasses import dataclass, field
from harness.data_constraints import DataConstraintsHarness
from harness.completion_criteria import CompletionCriteriaHarness
from harness.access_control import AccessControlHarness
from harness.handover import HandoverHarness
from harness.loop_detector import LoopDetector


@dataclass
class TestResult:
    test_id: str
    task_type: str
    role: str
    success: bool
    latency: float
    message_count: int
    tool_call_count: int
    reason: str
    input: str
    final_output: str = ""
    error: str = ""


@dataclass
class SuiteResult:
    agent_name: str
    results: list = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def success_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0

    @property
    def avg_latency(self) -> float:
        return sum(r.latency for r in self.results) / len(self.results) if self.results else 0.0

    @property
    def avg_steps(self) -> float:
        return sum(r.tool_call_count for r in self.results) / len(self.results) if self.results else 0.0

    def to_dict(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "total": self.total,
            "passed": self.passed,
            "failed": self.total - self.passed,
            "success_rate": round(self.success_rate, 3),
            "avg_latency_sec": round(self.avg_latency, 2),
            "avg_tool_calls": round(self.avg_steps, 2),
            "results": [
                {
                    "test_id": r.test_id,
                    "success": r.success,
                    "latency": round(r.latency, 2),
                    "tool_calls": r.tool_call_count,
                    "messages": r.message_count,
                    "reason": r.reason,
                    "error": r.error,
                }
                for r in self.results
            ],
        }


class FlightBookingHarness:
    """Harness điều phối trung tâm cho toàn bộ vòng đời của Agent."""

    def __init__(self, max_iterations: int = 8):
        self.data = DataConstraintsHarness()
        self.completion = CompletionCriteriaHarness()
        self.access = AccessControlHarness()
        self.handover = HandoverHarness()
        self.loop_detector = LoopDetector(window=4, repeat_k=2, stall_n=3)
        self.max_iterations = max_iterations

    def check_pre_execution_permission(self, role: str, tool_name: str, tool_args: dict) -> tuple[bool, str]:
        """Bước 0 trong slide 35: Kiểm quyền trước khi gọi tool."""
        if not self.access.check_permission(role, tool_name):
            return False, f"Role '{role}' không có quyền gọi tool '{tool_name}'."
        return True, ""

    def evaluate_termination(self, iteration: int, tool_name: str, tool_args: dict, observation: str) -> tuple[bool, str]:
        """
        Checklist sau mỗi observation (slide 35):
        1. Phát hiện lặp (Loop / Stall)
        2. Hết ngân sách (vòng lặp, token)
        """
        # Kiểm tra lặp / bế tắc
        loop_status = self.loop_detector.check(tool_name, tool_args, progress=len(observation))
        if loop_status == "LOOP":
            handoff = self.handover.create_handover_summary(
                reason="Phát hiện lặp hành vi (Loop)",
                last_action=f"{tool_name}({tool_args})",
                last_observation=observation,
                specific_question="Agent gọi lặp cùng tham số nhưng không có kết quả mới. Bạn có muốn đổi tham số không?"
            )
            print(handoff)
            return True, "DỪNG BẤT THƯỜNG: Phát hiện lặp hành động (Loop)"

        if loop_status == "STALL":
            return True, "DỪNG BẤT THƯỜNG: Bế tắc tiến trình (Stall)"

        # Kiểm tra ngân sách (phải kiểm cuối cùng theo slide 35)
        if iteration >= self.max_iterations:
            return True, f"DỪNG BẤT THƯỜNG: Hết ngân sách vòng lặp ({self.max_iterations} vòng)"

        return False, ""

    def run_test_case(self, agent_fn, test_case: dict) -> TestResult:
        self.loop_detector.reset()
        test_id = test_case.get("id", "unknown")
        user_input = test_case.get("input", "")
        role = test_case.get("role", "user")
        task_type = test_case.get("task_type", "search")
        constraints = test_case.get("constraints", {})

        start_time = time.time()
        try:
            result = agent_fn(user_input, role)
            latency = time.time() - start_time
            messages = result.get("messages", [])

            # Đếm số lần gọi tool
            tool_calls = sum(1 for m in messages if getattr(m, "type", "") == "tool" or (hasattr(m, "tool_calls") and m.tool_calls))
            
            # Lấy output cuối
            from langchain_core.messages import AIMessage
            final_output = ""
            for m in reversed(messages):
                if isinstance(m, AIMessage) and m.content:
                    final_output = m.content if isinstance(m.content, str) else str(m.content)
                    break

            eval_result = self.completion.evaluate(task_type, messages, context_constraints=constraints)

            return TestResult(
                test_id=test_id,
                task_type=task_type,
                role=role,
                success=eval_result["success"],
                latency=latency,
                message_count=len(messages),
                tool_call_count=tool_calls,
                reason=eval_result["reason"],
                input=user_input,
                final_output=final_output[:500],
            )
        except Exception as e:
            return TestResult(
                test_id=test_id,
                task_type=task_type,
                role=role,
                success=False,
                latency=time.time() - start_time,
                message_count=0,
                tool_call_count=0,
                reason=f"❌ Exception: {type(e).__name__}",
                input=user_input,
                error=str(e),
            )

    def run_suite(self, agent_fn, test_cases: list, agent_name: str = "Agent") -> SuiteResult:
        suite = SuiteResult(agent_name=agent_name)
        total = len(test_cases)
        print(f"\n{'='*55}\n  Chạy test suite: {agent_name} ({total} test cases)\n{'='*55}")

        for i, tc in enumerate(test_cases, 1):
            print(f"  [{i:02d}/{total}] {tc['id']}: {tc['input'][:50]}...")
            res = self.run_test_case(agent_fn, tc)
            suite.results.append(res)
            icon = "✅" if res.success else "❌"
            print(f"         {icon} {res.reason} (⏱ {res.latency:.1f}s, 🔧 {res.tool_call_count} calls)")

        print(f"\n  📊 Kết quả: {suite.passed}/{suite.total} passed ({suite.success_rate:.0%})")
        print(f"  ⏱ Avg latency: {suite.avg_latency:.1f}s | 🔧 Avg tool calls: {suite.avg_steps:.1f}\n{'='*55}\n")
        return suite