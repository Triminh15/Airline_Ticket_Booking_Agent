from datetime import datetime
from typing import Optional


class HandoverHarness:
    """
    Quản lý các điểm bàn giao từ AI Agent sang human operator.
    Xác định khi nào cần human can thiệp và tạo báo cáo tóm tắt trong 30s.
    """

    # Ngưỡng kích hoạt handover nghiệp vụ
    PRICE_THRESHOLD = 5_000_000         # VND — Vé trên 5 triệu cần xác nhận
    GROUP_THRESHOLD = 5                 # Số hành khách — Đoàn trên 5 người cần xác nhận
    BUSINESS_GROUP_THRESHOLD = 2        # Business class với >2 người cần duyệt

    def should_handover(self, state: dict) -> tuple[bool, str]:
        """
        Kiểm tra trạng thái booking có chạm các điều kiện cần duyệt nghiệp vụ không.
        
        Args:
            state: Dict chứa thông tin booking (total_price, passengers, refundable, ...)
            
        Returns:
            (True, lý_do) nếu cần bàn giao, ngược lại (False, "")
        """
        reasons = []

        # 1. Giá vé vượt ngưỡng
        total_price = state.get("total_price", 0)
        try:
            total_price = float(str(total_price).replace(",", "").replace("VND", "").strip())
        except (ValueError, TypeError):
            total_price = 0

        if total_price > self.PRICE_THRESHOLD:
            reasons.append(f"💰 Tổng giá vé {total_price:,.0f} VND vượt ngưỡng tự duyệt ({self.PRICE_THRESHOLD:,} VND)")

        # 2. Vé không hoàn tiền
        if state.get("refundable") is False:
            reasons.append("⚠️ Vé máy bay KHÔNG HOÀN TIỀN (Non-refundable)")

        # 3. Đoàn đông người
        passengers = state.get("passengers", 1)
        try:
            passengers = int(passengers)
        except (ValueError, TypeError):
            passengers = 1

        if passengers > self.GROUP_THRESHOLD:
            reasons.append(f"👥 Đoàn đông ({passengers} người, vượt ngưỡng {self.GROUP_THRESHOLD})")

        # 4. Hạng thương gia nhóm
        seat_class = str(state.get("seat_class", "")).lower()
        if seat_class == "business" and passengers > self.BUSINESS_GROUP_THRESHOLD:
            reasons.append(f"💼 Đặt hạng Thương gia cho {passengers} người")

        if reasons:
            return True, " | ".join(reasons)

        return False, ""

    def create_handover_summary(
        self,
        reason: str,
        last_action: str = "Không rõ",
        last_observation: str = "",
        specific_question: str = "Bạn có đồng ý phê duyệt tiếp tục không?",
        state: Optional[dict] = None,
        attempted_actions: Optional[list] = None
    ) -> str:
        """
        Tạo báo cáo bàn giao chuẩn mực theo cấu trúc Slide 48.
        Giúp operator nắm bắt toàn cảnh và ra quyết định trong 30 giây.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            "\n" + "=" * 60,
            "🚨 [HARNESS HANDOFF] AGENT CẦN BÀN GIAO CHO CON NGƯỜI",
            f"⏰ Thời gian: {timestamp}",
            "=" * 60,
            f"📌 LÝ DO BÀN GIAO: {reason}",
            "-" * 60,
            "1. TRẠNG THÁI HIỆN TẠI (ĐÃ LÀM TỚI ĐÂU):",
        ]

        # Hiển thị thông tin state nếu có
        if state:
            field_labels = {
                "flight_id": "Mã chuyến bay",
                "passenger_name": "Tên hành khách",
                "seat_class": "Hạng ghế",
                "total_price": "Tổng giá",
                "refundable": "Hoàn tiền",
                "status": "Trạng thái booking",
                "paid": "Đã thanh toán",
            }
            for k, label in field_labels.items():
                if k in state:
                    val = state[k]
                    if k == "refundable":
                        val = "Có" if val else "Không"
                    elif k == "total_price" and isinstance(val, (int, float)):
                        val = f"{val:,} VND"
                    lines.append(f"   • {label}: {val}")
        else:
            lines.append("   • Chưa có dữ liệu booking được ghi nhận.")

        lines.extend([
            "-" * 60,
            "2. NHỮNG GÌ ĐÃ THỬ (HƯỚNG NÀO ĐÃ HỎNG):",
            f"   • Hành động gần nhất: {last_action}",
        ])

        if attempted_actions:
            lines.append(f"   • Số hành động đã thử: {len(attempted_actions)}")
            for idx, act in enumerate(attempted_actions[-3:], 1):  # 3 hành động gần nhất
                lines.append(f"     - Hướng {idx}: {act}")

        clean_obs = str(last_observation).replace("\n", " ").strip()
        if len(clean_obs) > 160:
            clean_obs = clean_obs[:160] + "..."
        lines.append(f"   • Quan sát thực tế: {clean_obs or 'Không có dữ liệu phản hồi'}")

        lines.extend([
            "-" * 60,
            "3. HÀNH ĐỘNG CẦN QUYẾT ĐỊNH (TRẢ LỜI TRONG 30 GIÂY):",
            f"   👉 \"{specific_question}\"",
            "=" * 60 + "\n",
        ])

        return "\n".join(lines)

    def simulate_human_approval(self, state: dict) -> bool:
        """
        Giả lập quyết định của human operator (dùng khi chạy test suite tự động).
        """
        if state.get("force_reject", False):
            return False
        return True

    def resume_from_handover(self, human_decision: str, state: dict) -> dict:
        """
        Cập nhật lại trạng thái dựa trên phản hồi của con người.
        """
        decision = human_decision.lower().strip()
        updated_state = state.copy()

        if decision in ["approve", "yes", "y", "ok", "đồng ý", "duyệt"]:
            updated_state["human_approved"] = True
            updated_state["handover_resolved"] = True
            updated_state["handover_decision"] = "approved"
        else:
            updated_state["human_approved"] = False
            updated_state["handover_resolved"] = True
            updated_state["handover_decision"] = "rejected"

        return updated_state