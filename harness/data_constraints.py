from datetime import date, datetime
from tools.mock_data import AIRPORTS


class DataConstraintsHarness:
    def validate_date(self, date_str: str) -> tuple[bool, str]:
        """
        Kiểm tra ngày bay hợp lệ:
        - Đúng định dạng YYYY-MM-DD
        - Phải là ngày trong tương lai (> hôm nay)
        """
        try:
            flight_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return False, f"Ngày '{date_str}' không đúng định dạng YYYY-MM-DD."

        today = date.today()
        if flight_date <= today:
            return False, f"Ngày bay {date_str} phải là ngày trong tương lai (sau {today})."

        return True, ""

    def validate_airport_code(self, code: str) -> tuple[bool, str]:
        """
        Kiểm tra mã sân bay IATA hợp lệ:
        - Phải là 3 chữ cái in hoa
        - Phải có trong danh sách AIRPORTS
        """
        if not isinstance(code, str) or len(code) != 3 or not code.isalpha():
            return False, f"Mã sân bay '{code}' không hợp lệ. Phải là 3 ký tự chữ cái."

        code_upper = code.upper()
        if code_upper not in AIRPORTS:
            valid_codes = ", ".join(AIRPORTS.keys())
            return False, f"Mã sân bay '{code_upper}' không tồn tại. Mã hợp lệ: {valid_codes}."

        return True, ""

    def validate_passenger_count(self, count: int) -> tuple[bool, str]:
        """
        Kiểm tra số lượng hành khách hợp lệ: 1 <= count <= 9
        """
        try:
            count = int(count)
        except (TypeError, ValueError):
            return False, "Số hành khách phải là số nguyên."

        if count < 1:
            return False, "Số hành khách phải ít nhất là 1."
        if count > 9:
            return False, "Số hành khách tối đa là 9 người trên một đặt vé."

        return True, ""

    def validate_passenger_name(self, name: str) -> tuple[bool, str]:
        """
        Kiểm tra tên hành khách hợp lệ:
        - Không rỗng
        - Ít nhất 2 từ (họ và tên)
        """
        if not name or not isinstance(name, str):
            return False, "Tên hành khách không được để trống."

        name = name.strip()
        if len(name.split()) < 2:
            return False, f"Tên '{name}' cần ít nhất họ và tên (2 từ trở lên)."

        if len(name) < 4:
            return False, "Tên hành khách quá ngắn."

        return True, ""

    def validate_phone(self, phone: str) -> tuple[bool, str]:
        """
        Kiểm tra số điện thoại Việt Nam:
        - Bắt đầu bằng 0 hoặc +84
        - Có 10 chữ số (sau khi chuẩn hóa)
        """
        if not phone or not isinstance(phone, str):
            return False, "Số điện thoại không được để trống."

        digits = phone.replace(" ", "").replace("-", "")
        if digits.startswith("+84"):
            digits = "0" + digits[3:]

        if not digits.isdigit():
            return False, f"Số điện thoại '{phone}' chứa ký tự không hợp lệ."

        if len(digits) != 10:
            return False, f"Số điện thoại phải có 10 chữ số, nhận được {len(digits)}."

        if not digits.startswith("0"):
            return False, "Số điện thoại Việt Nam phải bắt đầu bằng 0."

        return True, ""

    def validate_seat_class(self, seat_class: str) -> tuple[bool, str]:
        """
        Kiểm tra hạng ghế hợp lệ: 'economy' hoặc 'business'
        """
        valid = ["economy", "business"]
        if not seat_class or seat_class.lower() not in valid:
            return False, f"Hạng ghế '{seat_class}' không hợp lệ. Chọn: economy hoặc business."
        return True, ""

    def validate_booking_state(self, state: dict) -> tuple[bool, list[str]]:
        """
        Kiểm tra state của booking có đủ field bắt buộc không.
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        required_fields = ["flight_id", "passenger_name", "seat_class", "contact_phone"]

        for field in required_fields:
            if field not in state or not state[field]:
                errors.append(f"Thiếu thông tin bắt buộc: {field}")

        if "flight_id" in state and state["flight_id"]:
            # Validate seat class nếu có
            if "seat_class" in state and state["seat_class"]:
                ok, msg = self.validate_seat_class(state["seat_class"])
                if not ok:
                    errors.append(msg)

        return len(errors) == 0, errors

    def validate_all_booking_inputs(
        self, flight_id: str, passenger_name: str, seat_class: str, phone: str
    ) -> tuple[bool, list[str]]:
        """
        Kiểm tra toàn bộ thông tin đặt vé cùng một lúc.
        """
        errors = []

        ok, msg = self.validate_passenger_name(passenger_name)
        if not ok:
            errors.append(msg)

        ok, msg = self.validate_seat_class(seat_class)
        if not ok:
            errors.append(msg)

        ok, msg = self.validate_phone(phone)
        if not ok:
            errors.append(msg)

        return len(errors) == 0, errors
