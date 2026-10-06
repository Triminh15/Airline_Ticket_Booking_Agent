
# 1. Danh mục sân bay mở rộng (IATA Codes)
AIRPORTS = {
    "HAN": {"name": "Sân bay Quốc tế Nội Bài", "city": "Hà Nội", "terminals": ["T1", "T2"], "checkin_open_hours": 2},
    "SGN": {"name": "Sân bay Quốc tế Tân Sơn Nhất", "city": "Hồ Chí Minh", "terminals": ["T1", "T2"], "checkin_open_hours": 2},
    "DAD": {"name": "Sân bay Quốc tế Đà Nẵng", "city": "Đà Nẵng", "terminals": ["T1", "T2"], "checkin_open_hours": 2},
    "HUI": {"name": "Sân bay Quốc tế Phú Bài", "city": "Huế", "terminals": ["T1", "T2"], "checkin_open_hours": 1.5},
    "PQC": {"name": "Sân bay Quốc tế Phú Quốc", "city": "Phú Quốc", "terminals": ["T1"], "checkin_open_hours": 1.5},
    "CXR": {"name": "Sân bay Quốc tế Cam Ranh", "city": "Nha Trang", "terminals": ["T1", "T2"], "checkin_open_hours": 2},
    "DLI": {"name": "Sân bay Liên Khương", "city": "Đà Lạt", "terminals": ["T1"], "checkin_open_hours": 1.5},
    "UIH": {"name": "Sân bay Phù Cát", "city": "Quy Nhơn", "terminals": ["T1"], "checkin_open_hours": 1.5},
    "VCA": {"name": "Sân bay Quốc tế Cần Thơ", "city": "Cần Thơ", "terminals": ["T1"], "checkin_open_hours": 1.5},
    "HPH": {"name": "Sân bay Quốc tế Cát Bi", "city": "Hải Phòng", "terminals": ["T1"], "checkin_open_hours": 1.5},
    "VII": {"name": "Sân bay Quốc tế Vinh", "city": "Vinh", "terminals": ["T1"], "checkin_open_hours": 1.5},
    "BMV": {"name": "Sân bay Buôn Ma Thuột", "city": "Buôn Ma Thuột", "terminals": ["T1"], "checkin_open_hours": 1.5},
    "VCL": {"name": "Sân bay Chu Lai", "city": "Quảng Nam", "terminals": ["T1"], "checkin_open_hours": 1.5},
    "VDH": {"name": "Sân bay Đồng Hới", "city": "Đồng Hới", "terminals": ["T1"], "checkin_open_hours": 1.5},
    "TBB": {"name": "Sân bay Tuy Hòa", "city": "Phú Yên", "terminals": ["T1"], "checkin_open_hours": 1.5},
}

# 2. Danh sách chuyến bay mở rộng (24 chuyến bay đa dạng kịch bản)
FLIGHTS = [
    {
        "flight_id": "VN101", "airline": "Vietnam Airlines", "origin": "HAN", "destination": "SGN",
        "date": "2026-10-20", "departure_time": "06:00", "arrival_time": "08:15", "duration_min": 135,
        "seats_economy": 120, "seats_business": 16, "price_economy": 1_200_000, "price_business": 3_800_000,
        "refundable": True
    },
    {
        "flight_id": "VJ101", "airline": "VietJet Air", "origin": "HAN", "destination": "SGN",
        "date": "2026-10-20", "departure_time": "08:30", "arrival_time": "10:45", "duration_min": 135,
        "seats_economy": 180, "seats_business": 0, "price_economy": 890_000, "price_business": 0,
        "refundable": False  # Giá rẻ nhưng không hoàn tiền -> Cần Human Approval nếu đặt quy tắc
    },
    {
        "flight_id": "QH201", "airline": "Bamboo Airways", "origin": "HAN", "destination": "SGN",
        "date": "2026-10-20", "departure_time": "14:00", "arrival_time": "16:15", "duration_min": 135,
        "seats_economy": 90, "seats_business": 12, "price_economy": 1_050_000, "price_business": 3_200_000,
        "refundable": True
    },

    {
        "flight_id": "VN122", "airline": "Vietnam Airlines", "origin": "SGN", "destination": "DAD",
        "date": "2026-10-07", "departure_time": "07:30", "arrival_time": "08:50", "duration_min": 80,
        "seats_economy": 3, "seats_business": 2, "price_economy": 1_750_000, "price_business": 3_100_000,
        "refundable": True  # Chuyến lý tưởng: sáng sớm, giá < 2tr (cộng phí 100k là 1.850k), có hoàn tiền
    },
    {
        "flight_id": "VJ604", "airline": "VietJet Air", "origin": "SGN", "destination": "DAD",
        "date": "2026-10-07", "departure_time": "09:00", "arrival_time": "10:20", "duration_min": 80,
        "seats_economy": 0, "seats_business": 0, "price_economy": 1_450_000, "price_business": 0,
        "refundable": False  # Đã hết chỗ hoàn toàn
    },
    {
        "flight_id": "QH118", "airline": "Bamboo Airways", "origin": "SGN", "destination": "DAD",
        "date": "2026-10-07", "departure_time": "10:15", "arrival_time": "11:35", "duration_min": 80,
        "seats_economy": 45, "seats_business": 6, "price_economy": 2_350_000, "price_business": 4_200_000,
        "refundable": True  # Vượt trần ngân sách 2.000.000đ
    },
    {
        "flight_id": "VN134", "airline": "Vietnam Airlines", "origin": "SGN", "destination": "DAD",
        "date": "2026-10-07", "departure_time": "15:45", "arrival_time": "17:05", "duration_min": 80,
        "seats_economy": 50, "seats_business": 8, "price_economy": 1_300_000, "price_business": 2_600_000,
        "refundable": True  # Chiều tối (lệch ràng buộc bay sáng)
    },
    # Tuyến SGN -> DAD vào ngày 2026-10-25
    {
        "flight_id": "VN301", "airline": "Vietnam Airlines", "origin": "SGN", "destination": "DAD",
        "date": "2026-10-25", "departure_time": "09:00", "arrival_time": "10:20", "duration_min": 80,
        "seats_economy": 110, "seats_business": 12, "price_economy": 800_000, "price_business": 2_400_000,
        "refundable": True
    },
    {
        "flight_id": "VJ301", "airline": "VietJet Air", "origin": "SGN", "destination": "DAD",
        "date": "2026-10-25", "departure_time": "15:00", "arrival_time": "16:20", "duration_min": 80,
        "seats_economy": 170, "seats_business": 0, "price_economy": 620_000, "price_business": 0,
        "refundable": False
    },

    # ── Tuyến SGN -> HUI (Huế - để test chuyển hướng sai sân bay ở slide 40) ─
    {
        "flight_id": "VN250", "airline": "Vietnam Airlines", "origin": "SGN", "destination": "HUI",
        "date": "2026-10-07", "departure_time": "08:15", "arrival_time": "09:40", "duration_min": 85,
        "seats_economy": 80, "seats_business": 8, "price_economy": 1_100_000, "price_business": 2_500_000,
        "refundable": True
    },
    {
        "flight_id": "VJ252", "airline": "VietJet Air", "origin": "SGN", "destination": "HUI",
        "date": "2026-10-07", "departure_time": "13:30", "arrival_time": "14:55", "duration_min": 85,
        "seats_economy": 120, "seats_business": 0, "price_economy": 720_000, "price_business": 0,
        "refundable": False
    },

    # ── Tuyến HAN -> DAD ────────────────────────
    {
        "flight_id": "VN201", "airline": "Vietnam Airlines", "origin": "HAN", "destination": "DAD",
        "date": "2026-10-20", "departure_time": "07:30", "arrival_time": "08:50", "duration_min": 80,
        "seats_economy": 100, "seats_business": 12, "price_economy": 950_000, "price_business": 2_800_000,
        "refundable": True
    },
    {
        "flight_id": "VJ201", "airline": "VietJet Air", "origin": "HAN", "destination": "DAD",
        "date": "2026-10-20", "departure_time": "12:00", "arrival_time": "13:20", "duration_min": 80,
        "seats_economy": 160, "seats_business": 0, "price_economy": 750_000, "price_business": 0,
        "refundable": False
    },

    # ── Tuyến HAN / SGN -> PQC (Phú Quốc) ───────
    {
        "flight_id": "VN401", "airline": "Vietnam Airlines", "origin": "HAN", "destination": "PQC",
        "date": "2026-11-01", "departure_time": "08:00", "arrival_time": "10:10", "duration_min": 130,
        "seats_economy": 130, "seats_business": 16, "price_economy": 1_500_000, "price_business": 4_200_000,
        "refundable": True
    },
    {
        "flight_id": "QH401", "airline": "Bamboo Airways", "origin": "HAN", "destination": "PQC",
        "date": "2026-11-01", "departure_time": "16:00", "arrival_time": "18:10", "duration_min": 130,
        "seats_economy": 85, "seats_business": 10, "price_economy": 1_350_000, "price_business": 3_900_000,
        "refundable": True
    },
    {
        "flight_id": "VJ401", "airline": "VietJet Air", "origin": "SGN", "destination": "PQC",
        "date": "2026-11-01", "departure_time": "11:00", "arrival_time": "12:05", "duration_min": 65,
        "seats_economy": 0, "seats_business": 0, "price_economy": 700_000, "price_business": 0,
        "refundable": False  # Edge case: hết vé chặng ngắn
    },
    {
        "flight_id": "VN405", "airline": "Vietnam Airlines", "origin": "SGN", "destination": "PQC",
        "date": "2026-11-01", "departure_time": "15:30", "arrival_time": "16:35", "duration_min": 65,
        "seats_economy": 40, "seats_business": 4, "price_economy": 950_000, "price_business": 2_100_000,
        "refundable": True
    },

    # ── Tuyến SGN -> UIH (Quy Nhơn) ─────────────
    {
        "flight_id": "VN501", "airline": "Vietnam Airlines", "origin": "SGN", "destination": "UIH",
        "date": "2026-10-22", "departure_time": "09:30", "arrival_time": "10:45", "duration_min": 75,
        "seats_economy": 100, "seats_business": 8, "price_economy": 850_000, "price_business": 2_100_000,
        "refundable": True
    },
    {
        "flight_id": "VJ501", "airline": "VietJet Air", "origin": "SGN", "destination": "UIH",
        "date": "2026-10-22", "departure_time": "14:00", "arrival_time": "15:15", "duration_min": 75,
        "seats_economy": 150, "seats_business": 0, "price_economy": 550_000, "price_business": 0,
        "refundable": False
    },

    # ── Tuyến miền Trung & Tây Nguyên (CXR, DLI, BMV, VCL) ───
    {
        "flight_id": "VN601", "airline": "Vietnam Airlines", "origin": "HAN", "destination": "CXR",
        "date": "2026-10-25", "departure_time": "10:00", "arrival_time": "11:55", "duration_min": 115,
        "seats_economy": 120, "seats_business": 12, "price_economy": 1_100_000, "price_business": 3_000_000,
        "refundable": True
    },
    {
        "flight_id": "VJ601", "airline": "VietJet Air", "origin": "SGN", "destination": "DLI",
        "date": "2026-10-28", "departure_time": "07:00", "arrival_time": "07:55", "duration_min": 55,
        "seats_economy": 180, "seats_business": 0, "price_economy": 450_000, "price_business": 0,
        "refundable": False
    },
    {
        "flight_id": "VN702", "airline": "Vietnam Airlines", "origin": "SGN", "destination": "BMV",
        "date": "2026-10-28", "departure_time": "08:15", "arrival_time": "09:15", "duration_min": 60,
        "seats_economy": 70, "seats_business": 6, "price_economy": 790_000, "price_business": 1_850_000,
        "refundable": True
    },
    {
        "flight_id": "VJ708", "airline": "VietJet Air", "origin": "SGN", "destination": "VCL",
        "date": "2026-10-29", "departure_time": "11:20", "arrival_time": "12:35", "duration_min": 75,
        "seats_economy": 140, "seats_business": 0, "price_economy": 590_000, "price_business": 0,
        "refundable": False
    },
]

# 3. Database lưu trữ Booking (In-memory)
BOOKINGS: dict = {}
BOOKING_COUNTER: list = [1000]

def next_booking_id() -> str:
    """Tạo booking ID tự tăng dạng BK1001, BK1002..."""
    BOOKING_COUNTER[0] += 1
    return f"BK{BOOKING_COUNTER[0]}"

def get_flight_by_id(flight_id: str) -> dict | None:
    """Tìm thông tin chuyến bay theo mã hiệu flight_id."""
    for f in FLIGHTS:
        if f["flight_id"] == flight_id.upper():
            return f
    return None