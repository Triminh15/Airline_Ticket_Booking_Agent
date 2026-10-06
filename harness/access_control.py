from langchain_core.tools import BaseTool
from tools.mock_data import FLIGHTS


class AccessControlHarness:
    """
    1. Phân quyền theo Role (guest < user < admin).
    2. Kiểm soát hành động vượt thẩm quyền (Vé không hoàn, vượt hạn mức, thanh toán tiền).
    """

    ROLE_PERMISSIONS: dict[str, list[str]] = {
        "guest": [
            "search_flights",
            "get_flight_details",
            "get_airport_info",
        ],
        "user": [
            "search_flights",
            "get_flight_details",
            "get_airport_info",
            "check_seat_availability",
            "calculate_price",
            "book_flight",
            "pay_booking",
            "cancel_booking",
            "get_booking_status",
        ],
        "admin": ["*"],
    }

    AUTO_APPROVE_PRICE_LIMIT = 1_500_000

    def __init__(self, auto_approve: bool = False):
        self.auto_approve = auto_approve

    def check_permission(self, role: str, tool_name: str) -> bool:
        """Kiểm tra role có quyền gọi tool không."""
        role = role.lower()
        if role not in self.ROLE_PERMISSIONS:
            return False

        allowed = self.ROLE_PERMISSIONS[role]
        if "*" in allowed:
            return True

        return tool_name in allowed

    def wrap_tools(self, role: str, all_tools: list) -> list:
        """Lọc danh sách tool cung cấp cho Agent dựa trên role."""
        role = role.lower()
        if role not in self.ROLE_PERMISSIONS:
            return []

        allowed = self.ROLE_PERMISSIONS[role]
        if "*" in allowed:
            return all_tools

        filtered = []
        for tool in all_tools:
            tool_name = tool.name if hasattr(tool, "name") else str(tool)
            if tool_name in allowed:
                filtered.append(tool)

        return filtered

    def intercept_and_authorize(self, role: str, tool_name: str, tool_args: dict) -> tuple[bool, str]:
        """
        Cơ chế kiểm soát chạy TRƯỚC KHI THỰC THI TOOL:
        1. Kiểm tra quyền của Role.
        2. Nếu là hành động nhạy cảm (pay, vé không hoàn, giá cao) -> Kích hoạt Human Approval.
        """
        # Bước 1: Kiểm tra Role
        if not self.check_permission(role, tool_name):
            return False, f"⛔ Truy cập bị từ chối: Role '{role}' không có quyền gọi tool '{tool_name}'."

        # Bước 2: Bắt các hành động nhạy cảm 
        # Trường hợp A: Hành động thanh toán trừ tiền (pay_booking)
        if tool_name == "pay_booking":
            if self.auto_approve:
                return True, "Hệ thống tự động duyệt thanh toán trong môi trường thử nghiệm."

            print(f"\n⚠️  [ACCESS CONTROL] Phát hiện yêu cầu thanh toán trừ tiền: {tool_name}({tool_args})")
            confirm = input("👉 Phê duyệt thanh toán trừ tiền thật? (y/n): ").strip().lower()
            if confirm in ["y", "yes", "đồng ý"]:
                return True, "Người dùng đã duyệt thanh toán."
            return False, "Bị từ chối: Người dùng không đồng ý thanh toán."

        # Trường hợp B: Đặt vé có giá cao hoặc vé không hoàn tiền
        if tool_name == "book_flight":
            flight_id = tool_args.get("flight_id", "").upper()
            flight = next((f for f in FLIGHTS if f["flight_id"] == flight_id), None)

            if flight:
                price = flight.get("price_economy", 0)
                refundable = flight.get("refundable", True)

                # Điều kiện kích hoạt hỏi người (Slide 41)
                is_non_refundable = (refundable is False)
                is_over_limit = (price > self.AUTO_APPROVE_PRICE_LIMIT)

                if is_non_refundable or is_over_limit:
                    reasons = []
                    if is_non_refundable:
                        reasons.append("vé KHÔNG ĐƯỢC HOÀN TIỀN")
                    if is_over_limit:
                        reasons.append(f"giá vé ({price:,}đ) vượt hạn mức tự duyệt ({self.AUTO_APPROVE_PRICE_LIMIT:,}đ)")

                    reason_str = " và ".join(reasons)

                    if self.auto_approve:
                        return True, f"Tự động duyệt ({reason_str})."

                    print(f"\n⚠️  [ACCESS CONTROL - SLIDE 41] Cần duyệt đặt vé: Chuyến {flight_id} ({reason_str})")
                    confirm = input("👉 Phê duyệt tiếp tục đặt chuyến này? (y/n): ").strip().lower()
                    if confirm in ["y", "yes", "đồng ý"]:
                        return True, "Người dùng đã phê duyệt điều kiện đặc biệt."
                    return False, f"Bị từ chối: Người dùng không chấp nhận {reason_str}."

        return True, "Thao tác hợp lệ."