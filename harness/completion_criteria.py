import re
from langchain_core.messages import AIMessage
from tools.mock_data import BOOKINGS


class CompletionCriteriaHarness:
    BOOKING_ID_PATTERN = re.compile(r"\bBK\d{4,}\b", re.IGNORECASE)
    FLIGHT_ID_PATTERN = re.compile(r"\b(VN|VJ|QH)\d{3}\b", re.IGNORECASE)
    SUCCESS_KEYWORDS = ["thành công", "confirmed", "đã đặt", "hoàn tất"]

    def _extract_last_ai_text(self, messages: list) -> str:
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                if isinstance(msg.content, str):
                    return msg.content
                if isinstance(msg.content, list):
                    texts = [c.get("text", "") for c in msg.content if isinstance(c, dict)]
                    return " ".join(texts)
        return ""

    def evaluate(self, task_type: str, messages: list, context_constraints: dict = None) -> dict:
        last_text = self._extract_last_ai_text(messages)

        if task_type == "search":
            has_flight = bool(self.FLIGHT_ID_PATTERN.search(last_text))
            not_found = "không tìm thấy" in last_text.lower() or "hết vé" in last_text.lower()
            success = has_flight or not_found
            reason = "Tìm thấy chuyến bay hợp lệ" if has_flight else ("Báo rõ không có chuyến" if not_found else "Chưa đưa ra kết quả tìm kiếm rõ ràng")
            return {"success": success, "reason": reason}

        if task_type == "book":
            match = self.BOOKING_ID_PATTERN.search(last_text)
            if not match:
                return {"success": False, "reason": "Không tìm thấy mã booking ID trong câu trả lời"}

            booking_id = match.group(0).upper()

            # KIỂM CHỨNG CHÉO: Soi trực tiếp vào Mock Database 
            if booking_id not in BOOKINGS:
                return {"success": False, "reason": f"ẢO GIÁC: Mã {booking_id} được sinh ra nhưng không có trong Database"}

            booking = BOOKINGS[booking_id]
            if booking.get("status") != "confirmed" or not booking.get("paid"):
                return {"success": False, "reason": f"Vé {booking_id} chưa được thanh toán thành công (Status: {booking.get('status')})"}

            # Đối chiếu ràng buộc ngân sách (nếu có truyền vào)
            if context_constraints and "max_price" in context_constraints:
                if booking.get("total_price", 0) > context_constraints["max_price"]:
                    return {"success": False, "reason": f"Giá vé {booking.get('total_price')} vượt ngân sách trần"}

            return {"success": True, "reason": f"Đặt vé thành công và đã xác thực trong Database ({booking_id})"}

        if task_type == "cancel":
            success = any(kw in last_text.lower() for kw in ["đã hủy", "hủy thành công", "cancelled"])
            return {"success": success, "reason": "Đã thực hiện hủy booking" if success else "Chưa hoàn tất hủy vé"}

        return {"success": True, "reason": "Tác vụ hoàn thành"}