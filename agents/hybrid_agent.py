from llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent


HIGH_LEVEL_PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Bạn là kiến trúc sư quy trình đặt vé máy bay.
Hãy phân rã yêu cầu thành 2 - 3 MỤC TIÊU LỚN (GOALS) độc lập.
Format bắt buộc:
GOAL: [tên] | TASK: [chi tiết việc cần làm]

Ví dụ:
GOAL: tim_chuyen_bay | TASK: Tìm chuyến bay từ SGN đến DAD sáng 2026-10-07 dưới 2 triệu
GOAL: giu_cho_va_thanh_toan | TASK: Giữ chỗ chuyến tìm được và gọi thanh toán pay_booking

Chỉ trả về danh sách GOAL, không giải thích."""),
    ("human", "Yêu cầu: {input}")
])

GOAL_EXECUTOR_PROMPT = """Bạn là trợ lý giải quyết mục tiêu cụ thể trong đặt vé máy bay.
Hãy sử dụng tools được cấp để hoàn thành đúng nhiệm vụ.
Ngữ cảnh từ các mục tiêu trước:
{previous_context}
"""

SYNTHESIZER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Bạn là người tổng hợp kết quả cuối cùng cho người dùng từ kết quả của các mục tiêu.
Hãy trình bày ngắn gọn, rõ ràng, nêu rõ mã booking và trạng thái đặt vé."""),
    ("human", """Yêu cầu ban đầu: {input}
Kết quả từng mục tiêu:
{goal_results}
Hãy tổng hợp kết quả cuối cùng.""")
])


class HybridFlightAgent:
    """Agent thiết kế theo Mẫu Lai (Hybrid Pattern)."""

    def __init__(self, tools: list, harness, role: str = "user"):
        self.role = role
        self.harness = harness
        self.agent_name = "Hybrid"
        self.tools = tools

        allowed_tools = harness.access.wrap_tools(role, tools)
        llm = get_llm(temperature=0)
        self.llm = llm
        self.allowed_tools = allowed_tools

        self.planner_chain = HIGH_LEVEL_PLANNER_PROMPT | llm | StrOutputParser()
        self.synthesizer_chain = SYNTHESIZER_PROMPT | llm | StrOutputParser()

    def _parse_goals(self, planner_output: str) -> list[dict]:
        goals = []
        for line in planner_output.strip().split("\n"):
            line = line.strip()
            if not line or not line.startswith("GOAL:"):
                continue
            if "| TASK:" in line:
                parts = line.split("| TASK:")
                goals.append({"name": parts[0].replace("GOAL:", "").strip(), "task": parts[1].strip()})
            else:
                goals.append({"name": f"goal_{len(goals)+1}", "task": line.replace("GOAL:", "").strip()})
        return goals or [{"name": "main_goal", "task": planner_output.strip()}]

    def _execute_goal(self, goal: dict, previous_context: str) -> dict:
        executor = create_react_agent(
            model=self.llm,
            tools=self.allowed_tools,
            prompt=GOAL_EXECUTOR_PROMPT.format(previous_context=previous_context or "(Bắt đầu mục tiêu đầu tiên)")
        )

        try:
            result = executor.invoke({"messages": [("user", goal["task"])]})
            messages = result.get("messages", [])
            final_text = ""
            for msg in reversed(messages):
                if isinstance(msg, AIMessage) and isinstance(msg.content, str):
                    final_text = msg.content
                    break
            return {"goal_name": goal["name"], "result": final_text, "messages": messages, "success": True}
        except Exception as e:
            return {"goal_name": goal["name"], "result": f"Lỗi: {str(e)}", "messages": [], "success": False}

    def run(self, user_input: str, role: str = None) -> dict:
        all_messages = [HumanMessage(content=user_input)]
        goal_results = []

        # 1. Sinh các mục tiêu cấp cao
        planner_output = self.planner_chain.invoke({"input": user_input})
        goals = self._parse_goals(planner_output)

        previous_context = ""
        for goal in goals:
            # 2. Thực thi từng Goal bằng ReAct Sub-agent
            goal_res = self._execute_goal(goal, previous_context)
            goal_results.append(goal_res)
            all_messages.extend(goal_res.get("messages", []))
            previous_context += f"\n- {goal['name']}: {goal_res['result'][:250]}"

            # 3. Kiểm tra bàn giao sang con người 
            # Rà soát xem trong DB hiện có vé nào cần duyệt không
            from tools.mock_data import BOOKINGS
            for b_id, b_data in BOOKINGS.items():
                needs_handover, reason = self.harness.handover.should_handover(b_data)
                if needs_handover and not b_data.get("human_approved"):
                    handoff_summary = self.harness.handover.create_handover_summary(
                        reason=reason,
                        last_action=f"Đặt vé {b_id}",
                        last_observation=str(b_data),
                        specific_question=f"Phê duyệt xác nhận thanh toán cho booking {b_id}?",
                        state=b_data
                    )
                    print(handoff_summary)
                    # Giả lập hoặc hỏi người
                    approved = self.harness.handover.simulate_human_approval(b_data)
                    b_data["human_approved"] = approved
                    if not approved:
                        fail_msg = f"Dừng giao dịch: Người dùng từ chối phê duyệt do {reason}."
                        all_messages.append(AIMessage(content=fail_msg))
                        return {"messages": all_messages, "response": fail_msg}

        # 4. Tổng hợp kết quả
        goal_summary = "\n".join([f"Mục tiêu '{r['goal_name']}': {r['result'][:250]}" for r in goal_results])
        final_response = self.synthesizer_chain.invoke({"input": user_input, "goal_results": goal_summary})
        all_messages.append(AIMessage(content=final_response))

        return {"messages": all_messages, "response": final_response}