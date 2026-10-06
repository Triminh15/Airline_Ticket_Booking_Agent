TEST_CASES = [
    # ── 1. CƠ BẢN & HAPPY PATH ──────────────────────────────────────────────
    {
        "id": "TC01",
        "role": "user",
        "task_type": "search",
        "input": "Tìm vé từ SGN đến DAD ngày 2026-10-07 cho 1 người",
        "description": "Tìm kiếm hợp lệ có nhiều chuyến bay trả về",
        "constraints": {"origin": "SGN", "destination": "DAD", "depart_date": "2026-10-07"},
    },
    {
        "id": "TC02",
        "role": "user",
        "task_type": "book",
        "input": "Đặt vé chuyến VN122 ngày 2026-10-07 cho Nguyen Van A SĐT 0901234567 hạng economy và thanh toán luôn.",
        "description": "Happy path: Đặt vé và thanh toán trọn vẹn",
        "constraints": {"max_price": 2_000_000, "depart_date": "2026-10-07"},
    },
    {
        "id": "TC03",
        "role": "user",
        "task_type": "cancel",
        "input": "Hủy booking mã BK9999 cho tôi",
        "description": "Xử lý lỗi: Hủy booking không tồn tại trong hệ thống",
        "constraints": {},
    },

    # ── 2. PHỨC TẠP: RÀNG BUỘC NGÂN SÁCH & GIỜ BAY  ───────────
    {
        "id": "TC04",
        "role": "user",
        "task_type": "book",
        "input": "Tìm và đặt giúp tôi 1 vé máy bay từ SGN đi DAD sáng ngày 2026-10-07 dưới 2 triệu, bay trước 12:00 cho Le Thi B SĐT 0912345678.",
        "description": "Tìm kiếm thỏa nhiều ràng buộc: sáng, dưới 2tr, đặt và trả tiền",
        "constraints": {"max_price": 2_000_000, "latest_departure_time": "12:00", "origin": "SGN", "destination": "DAD"},
    },

    # ── 3. KIỂM QUYỀN ───────────────────────────
    {
        "id": "TC05",
        "role": "guest",
        "task_type": "book",
        "input": "Đặt vé VN101 hạng economy cho Pham Van D SĐT 0978123456",
        "description": "Chặn vi phạm quyền: Role guest không được phép gọi book_flight hay pay_booking",
        "constraints": {},
    },
    {
        "id": "TC06",
        "role": "user",
        "task_type": "book",
        "input": "Đặt vé chuyến VJ101 ngày 2026-10-20 cho Tran Van E SĐT 0988888888 hạng economy",
        "description": "Hành động nhạy cảm: Chuyến VJ101 là vé KHÔNG HOÀN TIỀN -> Kích hoạt kiểm quyền duyệt",
        "constraints": {},
    },

    # ── 4. RÀNG BUỘC DỮ LIỆU ĐẦU VÀO  ──────────
    {
        "id": "TC07",
        "role": "user",
        "task_type": "search",
        "input": "Tìm vé từ HAN đến SGN ngày 2020-01-01 cho 1 người",
        "description": "Ngày bay trong quá khứ -> Harness data constraints chặn báo lỗi",
        "constraints": {},
    },

    # ── 5. BẾ TẮC & HẾT CHỖ  ───────────
    {
        "id": "TC08",
        "role": "user",
        "task_type": "book",
        "input": "Đặt vé chuyến VJ604 ngày 2026-10-07 cho Vu Van F SĐT 0933445566 hạng economy",
        "description": "Chuyến VJ604 có available_seats = 0 -> Kiểm tra cách Agent xử lý khi hết chỗ",
        "constraints": {},
    },

    # ── 6. HANDOVER CHO NHÓM ĐÔNG  ────────────────────────────────
    {
        "id": "TC09",
        "role": "user",
        "task_type": "book",
        "input": "Đặt 6 vé chuyến VN201 ngày 2026-10-20 cho đoàn du lịch, trưởng đoàn Nguyen Van G SĐT 0911223344",
        "description": "Đoàn đông (>5 người) -> Kích hoạt Handover chuyển quyền cho con người",
        "constraints": {},
    },

    # ── 7. KIỂM TRA THÔNG TIN KẾT HỢP (MULTI-STEP) ──────────────────────────
    {
        "id": "TC10",
        "role": "user",
        "task_type": "search",
        "input": "Kiểm tra xem sân bay DAD có những terminal nào và chuyến VN201 còn bao nhiêu ghế trống?",
        "description": "Gọi liên tiếp 2 tool khác nhau: get_airport_info và check_seat_availability",
        "constraints": {},
    },
]