from llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from tools.flight_tools import ALL_TOOLS


REACT_SYSTEM_PROMPT = """Bạn là trợ lý đặt vé máy bay thông minh của hệ thống FlightAI.

Bạn có quyền truy cập vào các công cụ:
- search_flights, get_flight_details, check_seat_availability, calculate_price
- book_flight (Giữ chỗ - status: held)
- pay_booking (Thanh toán để xác nhận vé - status: confirmed)
- cancel_booking, get_booking_status, get_airport_info

QUY TRÌNH BẮT BUỘC KHI ĐẶT VÉ:
1. Tìm kiếm và kiểm tra ghế/giá vé phù hợp.
2. Gọi book_flight để giữ chỗ -> Nhận mã booking ID (dạng BKxxxx).
3. Gọi pay_booking(booking_id) để hoàn tất thanh toán.
4. Trả lời xác nhận đầy đủ mã booking và trạng thái confirmed cho khách hàng.

QUY TẮC AN TOÀN:
- Tuyệt đối không tự bịa đặt mã booking, giá vé hoặc chuyến bay khi tool chưa trả về.
- Trả lời bằng tiếng Việt, rõ ràng và chuẩn xác.
"""


class ReActFlightAgent:
    """Agent ReAct có tích hợp giám sát vòng lặp và kiểm quyền từ Harness."""

    def __init__(self, tools: list, harness, role: str = "user"):
        self.role = role
        self.harness = harness
        self.agent_name = "ReAct"
        self.tools_map = {t.name: t for t in tools}
        self.llm = get_llm(temperature=0)

    def run(self, user_input: str, role: str = None) -> dict:
        effective_role = role or self.role
        allowed_tools = self.harness.access.wrap_tools(effective_role, list(self.tools_map.values()))
        llm_with_tools = self.llm.bind_tools(allowed_tools)

        messages = [
            SystemMessage(content=REACT_SYSTEM_PROMPT),
            HumanMessage(content=user_input)
        ]

        self.harness.loop_detector.reset()
        step = 0
        max_steps = self.harness.max_iterations

        while step < max_steps:
            step += 1
            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)

            # Model tự cho rằng đã xong (không gọi tool nữa)
            if not ai_msg.tool_calls:
                break

            for tool_call in ai_msg.tool_calls:
                t_name = tool_call["name"]
                t_args = tool_call["args"]
                call_id = tool_call["id"]

                # 1. Kiểm quyền trước khi gọi tool 
                allowed, auth_msg = self.harness.access.intercept_and_authorize(effective_role, t_name, t_args)
                if not allowed:
                    obs_content = f'{{"status": "permission_denied", "message": "{auth_msg}"}}'
                else:
                    tool_func = self.tools_map.get(t_name)
                    try:
                        obs_content = tool_func.invoke(t_args)
                    except Exception as ex:
                        obs_content = f'{{"status": "error", "message": "{str(ex)}"}}'

                # 2. Ghi observation vào context 
                messages.append(ToolMessage(tool_call_id=call_id, content=str(obs_content)))

                # 3. Xét điều kiện dừng bất thường 
                should_stop, reason = self.harness.evaluate_termination(
                    iteration=step,
                    tool_name=t_name,
                    tool_args=t_args,
                    observation=str(obs_content)
                )
                if should_stop:
                    messages.append(AIMessage(content=f"Dừng thực thi do: {reason}"))
                    return {"messages": messages, "response": reason}

        return {"messages": messages}