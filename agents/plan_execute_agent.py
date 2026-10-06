import operator
from typing import Annotated, TypedDict
from llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent


class PlanExecuteState(TypedDict):
    input: str
    plan: list[str]
    past_steps: Annotated[list[tuple], operator.add]
    response: str
    messages: Annotated[list, operator.add]


PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Bạn là chuyên gia lập kế hoạch cho hệ thống đặt vé máy bay.
QUY TẮC QUAN TRỌNG:
1. Chỉ lập kế hoạch cho ĐÚNG những gì người dùng yêu cầu:
   - Nếu người dùng CHỈ YÊU CẦU TÌM KIẾM/TRA CỨU: Kế hoạch CHỈ gồm 1 bước tìm kiếm/tra cứu thông tin. KHÔNG tự ý thêm các bước giữ chỗ hay thanh toán.
   - Nếu người dùng yêu cầu ĐẶT VÉ: Lập các bước tuần tự (tìm kiếm -> kiểm tra chỗ -> book_flight -> pay_booking).
2. Định dạng output:
Bước 1: [hành động cụ thể]
Bước 2: [hành động cụ thể]
Chỉ liệt kê các bước, không giải thích thêm."""),
    ("human", "Yêu cầu: {input}")
])

EXECUTOR_PROMPT = """Bạn là trợ lý thực thi từng bước trong quy trình đặt vé.
Hãy hoàn thành đúng bước được giao bằng cách sử dụng các tools phù hợp.
Ngữ cảnh từ các bước trước:
{context}
"""

REPLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Bạn là người giám sát tiến độ kế hoạch đặt vé.
Dựa trên kết quả thực tế từ các bước đã làm:
1. Nếu nhiệm vụ ĐÃ HOÀN TẤT hoặc người dùng chỉ hỏi tra cứu thông tin -> Trả về bắt đầu bằng "DONE: " kèm câu trả lời chi tiết cho người dùng.
2. Nếu kế hoạch cần làm tiếp -> Cập nhật các bước CÒN LẠI."""),
    ("human", """Yêu cầu gốc: {input}
Kế hoạch ban đầu:
{original_plan}
Các bước đã làm và kết quả:
{past_steps}

Hãy đánh giá và đưa ra quyết định tiếp theo.""")
])


class PlanThenExecuteAgent:
    """Agent Plan-then-Execute điều phối qua LangGraph."""

    def __init__(self, tools: list, harness, role: str = "user"):
        self.role = role
        self.harness = harness
        self.agent_name = "Plan-then-Execute"
        self.tools = tools

        allowed_tools = harness.access.wrap_tools(role, tools)
        llm = get_llm(temperature=0)

        self.planner_chain = PLANNER_PROMPT | llm | StrOutputParser()
        self.replanner_chain = REPLANNER_PROMPT | llm | StrOutputParser()
        self.executor = create_react_agent(
            model=llm,
            tools=allowed_tools,
            prompt=EXECUTOR_PROMPT
        )
        self.graph = self._build_graph()

    def _parse_plan(self, plan_text: str) -> list[str]:
        lines = plan_text.strip().split("\n")
        steps = []
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("Bước") or line.startswith("Step")):
                import re
                step = re.sub(r'^(Bước\s*\d+[:.]\s*|\d+[:.]\s*|Step\s*\d+[:.]\s*)', '', line).strip()
                if step:
                    steps.append(step)
        return steps if steps else [plan_text]

    def _planner_node(self, state: PlanExecuteState) -> dict:
        plan_text = self.planner_chain.invoke({"input": state["input"]})
        steps = self._parse_plan(plan_text)
        return {"plan": steps, "messages": [HumanMessage(content=state["input"])], "past_steps": []}

    def _executor_node(self, state: PlanExecuteState) -> dict:
        if not state.get("plan"):
            return {"past_steps": [("(no step)", "Hết bước")]}

        current_step = state["plan"][0]
        remaining_plan = state["plan"][1:]

        context = "\n".join([f"- {s}: {r}" for s, r in state.get("past_steps", [])])

        exec_result = self.executor.invoke({
            "messages": [("user", f"Thực hiện bước này: {current_step}\nNgữ cảnh trước: {context}")]
        })

        exec_messages = exec_result.get("messages", [])
        result_text = current_step
        for msg in reversed(exec_messages):
            if isinstance(msg, AIMessage) and isinstance(msg.content, str) and msg.content.strip():
                result_text = msg.content
                break

        return {
            "plan": remaining_plan,
            "past_steps": [(current_step, result_text[:1500])],
            "messages": exec_messages,
        }

    def _replanner_node(self, state: PlanExecuteState) -> dict:
        past_steps = state.get("past_steps", [])
        past_steps_text = "\n".join([f"- {s}: {r}" for s, r in past_steps])
        original_plan = "\n".join(f"{i+1}. {s}" for i, s in enumerate(state.get("plan", [])))

        replanner_output = self.replanner_chain.invoke({
            "input": state["input"],
            "original_plan": original_plan,
            "past_steps": past_steps_text or "(Chưa có bước nào)",
        })

        output_clean = replanner_output.strip()

        if output_clean.startswith("DONE:") or "hoàn thành" in output_clean.lower()[:50] or not state.get("plan"):
            resp = output_clean.replace("DONE:", "").strip()
            if not resp and past_steps:
                resp = past_steps[-1][1]
            return {"response": resp or "Đã hoàn thành yêu cầu.", "messages": [AIMessage(content=resp)]}

        new_steps = self._parse_plan(output_clean)
        if not new_steps:
            return {"response": output_clean, "plan": []}

        return {"plan": new_steps}

    def _should_continue(self, state: PlanExecuteState) -> str:
        if state.get("response"):
            return "end"
        plan = state.get("plan", [])
        if not plan or len(plan) == 0:
            return "end"
        if len(state.get("past_steps", [])) >= 6:
            return "end"
        return "executor"

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(PlanExecuteState)
        graph.add_node("planner", self._planner_node)
        graph.add_node("executor", self._executor_node)
        graph.add_node("replanner", self._replanner_node)

        graph.add_edge(START, "planner")
        graph.add_edge("planner", "executor")
        graph.add_edge("executor", "replanner")
        graph.add_conditional_edges(
            "replanner",
            self._should_continue,
            {"executor": "executor", "end": END}
        )
        return graph.compile()

    def run(self, user_input: str, role: str = None) -> dict:
        initial_state = {
            "input": user_input,
            "plan": [],
            "past_steps": [],
            "response": "",
            "messages": [],
        }
        result = self.graph.invoke(initial_state, {"recursion_limit": 20})
        return {"messages": result.get("messages", []), "response": result.get("response", "")}