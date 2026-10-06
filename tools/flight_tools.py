import json
from datetime import datetime
from langchain_core.tools import tool
from tools.mock_data import FLIGHTS, AIRPORTS, BOOKINGS, get_flight_by_id, next_booking_id

@tool
def search_flights(origin: str, destination: str, date: str, passengers: int = 1) -> str:
    """Tìm kiếm danh sách chuyến bay theo điểm đi, điểm đến và ngày bay."""
    results = []
    for f in FLIGHTS:
        if (
            f["origin"].upper() == origin.upper()
            and f["destination"].upper() == destination.upper()
            and f["date"] == date
            and f["seats_economy"] >= passengers
        ):
            results.append({
                "flight_id": f["flight_id"],
                "airline": f["airline"],
                "departure_time": f["departure_time"],
                "arrival_time": f["arrival_time"],
                "price_economy": f["price_economy"],
                "price_business": f["price_business"],
                "refundable": f["refundable"],
                "seats_economy": f["seats_economy"],
            })

    if not results:
        return json.dumps({
            "status": "not_found",
            "message": f"Không tìm thấy chuyến bay từ {origin.upper()} đến {destination.upper()} ngày {date}.",
            "hint": "Hãy thử đổi ngày bay hoặc kiểm tra lại mã sân bay (IATA)."
        }, ensure_ascii=False)

    return json.dumps({"status": "ok", "flights": results}, ensure_ascii=False)


@tool
def get_flight_details(flight_id: str) -> str:
    """Lấy thông tin chi tiết đầy đủ của một chuyến bay cụ thể."""
    flight = get_flight_by_id(flight_id.upper())
    if not flight:
        return json.dumps({
            "status": "error",
            "error_code": "FLIGHT_NOT_FOUND",
            "hint": "Mã chuyến bay không tồn tại."
        }, ensure_ascii=False)

    return json.dumps({"status": "ok", "flight": flight}, ensure_ascii=False)


@tool
def check_seat_availability(flight_id: str, seat_class: str = "economy") -> str:
    """Kiểm tra số ghế còn trống và chính sách vé của một chuyến bay."""
    flight = get_flight_by_id(flight_id.upper())
    if not flight:
        return json.dumps({"status": "error", "message": f"Không tìm thấy chuyến bay {flight_id}."}, ensure_ascii=False)

    seat_class = seat_class.lower()
    if seat_class not in ["economy", "business"]:
        return json.dumps({
            "status": "invalid_param",
            "param": "seat_class",
            "allowed": ["economy", "business"]
        }, ensure_ascii=False)

    count = flight["seats_economy"] if seat_class == "economy" else flight["seats_business"]
    return json.dumps({
        "status": "ok",
        "flight_id": flight_id.upper(),
        "seat_class": seat_class,
        "available_seats": count,
        "refundable": flight["refundable"]
    }, ensure_ascii=False)


@tool
def calculate_price(flight_id: str, passengers: int = 1, seat_class: str = "economy") -> str:
    """Tính tổng giá vé máy bay bao gồm thuế phí sân bay."""
    flight = get_flight_by_id(flight_id.upper())
    if not flight:
        return json.dumps({"status": "error", "message": "Chuyến bay không tồn tại."}, ensure_ascii=False)

    seat_class = seat_class.lower()
    base_price = flight["price_economy"] if seat_class == "economy" else flight["price_business"]
    if seat_class == "business" and base_price == 0:
        return json.dumps({"status": "error", "message": "Chuyến bay không có hạng Business."}, ensure_ascii=False)

    airport_tax = 100_000
    total = (base_price + airport_tax) * passengers

    return json.dumps({
        "status": "ok",
        "flight_id": flight_id.upper(),
        "passengers": passengers,
        "base_price": base_price,
        "airport_tax": airport_tax,
        "total_price": total
    }, ensure_ascii=False)


@tool
def book_flight(flight_id: str, passenger_name: str, seat_class: str = "economy", contact_phone: str = "0901234567") -> str:
    """
    Giữ chỗ chuyến bay (chưa thanh toán). Chuyển trạng thái sang 'held'.
    """
    flight = get_flight_by_id(flight_id.upper())
    if not flight:
        return json.dumps({"status": "error", "message": f"Không tìm thấy chuyến bay {flight_id}."}, ensure_ascii=False)

    seat_class = seat_class.lower()
    seat_key = "seats_economy" if seat_class == "economy" else "seats_business"
    price_key = "price_economy" if seat_class == "economy" else "price_business"

    if flight[seat_key] <= 0:
        return json.dumps({
            "status": "seat_unavailable",
            "message": f"Chuyến {flight_id} hạng {seat_class} đã hết chỗ.",
            "hint": "Hãy chọn chuyến bay khác hoặc hạng ghế khác."
        }, ensure_ascii=False)

    # Trừ ghế giữ chỗ
    flight[seat_key] -= 1
    price = flight[price_key] + 100_000 
    booking_id = next_booking_id()

    BOOKINGS[booking_id] = {
        "booking_id": booking_id,
        "flight_id": flight_id.upper(),
        "passenger_name": passenger_name,
        "seat_class": seat_class,
        "contact_phone": contact_phone,
        "total_price": price,
        "refundable": flight["refundable"],
        "depart_date": flight["date"],
        "depart_time": flight["departure_time"],
        "origin": flight["origin"],
        "destination": flight["destination"],
        "status": "held",     
        "paid": False,         
        "booked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return json.dumps({
        "status": "held",
        "booking_id": booking_id,
        "total_price": price,
        "refundable": flight["refundable"],
        "message": "Đã giữ chỗ thành công. Cần thanh toán để xác nhận vé."
    }, ensure_ascii=False)


@tool
def pay_booking(booking_id: str, payment_method: str = "corp_card") -> str:
    """
    Thanh toán cho mã đặt chỗ để chính thức xác nhận vé (status: confirmed).
    Hành động này có tác dụng phụ trừ tiền, cần được kiểm duyệt.
    """
    booking_id = booking_id.upper()
    booking = BOOKINGS.get(booking_id)
    if not booking:
        return json.dumps({"status": "error", "message": f"Không tìm thấy booking {booking_id}."}, ensure_ascii=False)

    if booking["status"] == "confirmed" and booking["paid"]:
        return json.dumps({"status": "already_paid", "message": "Vé này đã được thanh toán trước đó."}, ensure_ascii=False)

    booking["paid"] = True
    booking["status"] = "confirmed"
    booking["payment_method"] = payment_method
    booking["paid_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return json.dumps({
        "status": "confirmed",
        "booking_id": booking_id,
        "paid": True,
        "message": "Thanh toán thành công! Vé đã được xác nhận."
    }, ensure_ascii=False)


@tool
def cancel_booking(booking_id: str) -> str:
    """Hủy đặt vé máy bay đã có và hoàn lại ghế."""
    booking_id = booking_id.upper()
    booking = BOOKINGS.get(booking_id)
    if not booking:
        return json.dumps({"status": "error", "message": f"Không tìm thấy booking {booking_id}."}, ensure_ascii=False)

    if booking["status"] == "cancelled":
        return json.dumps({"status": "error", "message": f"Booking {booking_id} đã bị hủy từ trước."}, ensure_ascii=False)

    # Hoàn trả lại ghế trống vào kho
    flight = get_flight_by_id(booking["flight_id"])
    if flight:
        seat_key = "seats_economy" if booking["seat_class"] == "economy" else "seats_business"
        flight[seat_key] += 1

    booking["status"] = "cancelled"
    return json.dumps({
        "status": "cancelled",
        "booking_id": booking_id,
        "message": "Hủy đặt vé thành công."
    }, ensure_ascii=False)


@tool
def get_booking_status(booking_id: str) -> str:
    """Tra cứu trạng thái thực tế của booking từ hệ thống."""
    booking_id = booking_id.upper()
    booking = BOOKINGS.get(booking_id)
    if not booking:
        return json.dumps({"status": "not_found", "message": f"Không tìm thấy mã {booking_id}."}, ensure_ascii=False)

    return json.dumps({"status": "ok", "booking": booking}, ensure_ascii=False)


@tool
def get_airport_info(airport_code: str) -> str:
    """Lấy thông tin sân bay theo mã IATA."""
    code = airport_code.upper()
    if code not in AIRPORTS:
        return json.dumps({
            "status": "not_found",
            "message": f"Không có sân bay {airport_code}."
        }, ensure_ascii=False)

    return json.dumps({"status": "ok", "airport": AIRPORTS[code]}, ensure_ascii=False)


ALL_TOOLS = [
    search_flights,
    get_flight_details,
    check_seat_availability,
    calculate_price,
    book_flight,
    pay_booking,       
    cancel_booking,
    get_booking_status,
    get_airport_info,
]