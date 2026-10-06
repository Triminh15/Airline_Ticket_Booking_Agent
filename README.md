# XÂY DỰNG AGENT ĐẶT VÉ MÁY BAY TÍCH HỢP HỆ THỐNG 5 LỚP HARNESS VÀ 3 MẪU THIẾT KẾ SUY LUẬN BẰNG LANGCHAIN & LANGGRAPH

> **TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN – ĐHQG TP. HỒ CHÍ MINH (UIT)**
> **KHOA CÔNG NGHỆ PHẦN MỀM**
> **Môn học**: SE373 · Kỹ thuật Xây dựng Hệ thống Agentic AI (Buổi 03: Agent Fundamentals)
> **Sinh viên thực hiện**: Nguyễn Minh Trí
> **Thời điểm hoàn thành**: Tháng 10/2026

---

## MỤC LỤC

1. [TỔNG QUAN YÊU CẦU & BÀI TOÁN NGHIỆP VỤ](https://www.google.com/search?q=%231-t%E1%BB%95ng-quan-y%C3%AAu-c%E1%BA%A7u--b%C3%A0i-to%C3%A1n-nghi%E1%BB%87p-v%E1%BB%A5)
2. [RANH GIỚI KIẾN TRÚC: MODEL VS. HARNESS](https://www.google.com/search?q=%232-ranh-gi%E1%BB%9Bi-ki%E1%BA%BFn-tr%C3%BAc-model-vs-harness)
3. [THIẾT KẾ VÀ CÀI ĐẶT 5 LỚP HARNESS CHUYÊN SÂU](https://www.google.com/search?q=%233-thi%E1%BA%BFt-k%E1%BA%BF-v%C3%A0-c%C3%A0i-%C4%91%E1%BA%B7t-5-l%E1%BB%9Bp-harness-chuy%C3%AAn-s%C3%A2u)
* 3.1. Lớp 1: Ràng buộc là dữ liệu (`DataConstraintsHarness`)
* 3.2. Lớp 2: Tiêu chí hoàn thành kiểm bằng code (`CompletionCriteriaHarness`)
* 3.3. Lớp 3: Kiểm soát phân quyền & Phê duyệt trước thực thi (`AccessControlHarness`)
* 3.4. Lớp 4: Phát hiện lặp & Bế tắc tiến trình (`LoopDetector`)
* 3.5. Lớp 5: Bàn giao chuẩn hóa cho con người (`HandoverHarness`)


4. [CÀI ĐẶT 3 MẪU THIẾT KẾ SUY LUẬN (REASONING PATTERNS)](https://www.google.com/search?q=%234-c%C3%A0i-%C4%91%E1%BA%B7t-3-m%E1%BA%ABu-thi%E1%BA%BFt-k%E1%BA%BF-suy-lu%E1%BA%ADn-reasoning-patterns)
* 4.1. Mẫu 1: ReAct Agent (Reasoning + Acting)
* 4.2. Mẫu 2: Plan-then-Execute Agent (LangGraph StateGraph)
* 4.3. Mẫu 3: Mẫu Lai (Hybrid Agent / Phân cấp Goals + ReAct Sub-agents)


5. [KẾT QUẢ THỰC NGHIỆM VÀ BENCHMARK ĐỊNH LƯỢNG](https://www.google.com/search?q=%235-k%E1%BA%BFt-qu%E1%BA%A3-th%E1%BB%B1c-nghi%E1%BB%87m-v%C3%A0-benchmark-%C4%91%E1%BB%8Bnh-l%C6%B0%E1%BB%A3ng)
* 5.1. Thiết kế bộ 10 Test Cases kiểm thử đa chiều
* 5.2. Bảng tổng hợp so sánh các chỉ tiêu khoa học
* 5.3. Ma trận chi tiết kết quả thực nghiệm (Detailed Matrix)
* 5.4. Phân tích chuyên sâu các đánh đổi (Trade-offs Analysis) & Failure Modes


6. [CÁC THÁCH THỨC KỸ THUẬT & GIẢI PHÁP ĐỘT PHÁ](https://www.google.com/search?q=%236-c%C3%A1c-th%C3%A1ch-th%E1%BB%A9c-k%E1%BB%B9-thu%E1%BA%ADt--gi%E1%BA%A3i-ph%C3%A1p-%C4%91%E1%BB%99t-ph%C3%A1)
* 6.1. Tách biệt chu trình Giữ chỗ (`book_flight`) và Thanh toán (`pay_booking`)
* 6.2. Kiểm soát bùng nổ ngữ cảnh và khắc phục cắt cụt dữ liệu trong Plan-then-Execute
* 6.3. Kiến trúc LLM Factory linh hoạt đa nền tảng (Groq / Gemini)


7. [HƯỚNG DẪN CÀI ĐẶT & TÁI HIỆN KẾT QUẢ (REPRODUCTION GUIDE)](https://www.google.com/search?q=%237-h%C6%B0%E1%BB%9Bng-d%E1%BA%ABn-c%C3%A0i-%C4%91%E1%BA%B7t--t%C3%A1i-hi%E1%BB%87n-k%E1%BA%BFt-qu%E1%BA%A3-reproduction-guide)
8. [KẾT LUẬN](https://www.google.com/search?q=%238-k%E1%BA%BFt-lu%E1%BA%ADn)

---

## 1. TỔNG QUAN YÊU CẦU & BÀI TOÁN NGHIỆP VỤ

Trong công nghệ Agentic AI, **AI Agent** được định nghĩa là một hệ thống phần mềm có khả năng tự chủ hoạt động, tiếp nhận mục tiêu, tự lựa chọn công cụ và ra quyết định hành động trong môi trường mà không cần con người can thiệp liên tục (*Slide 4*). Công thức nền tảng của một Agent hoàn chỉnh được xác lập bởi:

$$\text{Agent} = \text{Goal} + \text{Tools} + \text{Loop} + \text{Termination}$$

Bài tập BTVN#3 đặt ra bài toán thực tế: **Xây dựng hệ thống Agent tự động tra cứu, giữ chỗ và thanh toán vé máy bay** đáp ứng các ràng buộc kinh doanh thực tế và các tình huống biên (Edge Cases):

1. **Chuyến bay hết sạch ghế (`available_seats = 0`)**: Đòi hỏi Agent phải nhận biết trạng thái thực tế của môi trường thông qua observation, không rơi vào vòng lặp cố chấp đặt lại vé đã hết ghế.
2. **Chuyến bay có điều kiện vé không hoàn tiền (`refundable == False`)**: Đòi hỏi hệ thống phải kích hoạt chốt chặn an toàn tài chính, không tự ý thanh toán khi chưa có sự phê duyệt của con người (*Human-in-the-loop*).
3. **Phân quyền truy cập theo vai trò (Role-Based Access Control - RBAC)**: Khách vãng lai (`guest`) chỉ được phép tra cứu thông tin; các thao tác nhạy cảm như đặt chỗ (`book_flight`) hay thanh toán (`pay_booking`) chỉ dành cho người dùng đã xác thực (`user`) hoặc quản trị viên (`admin`).
4. **Đoàn đông người hoặc vượt ngân sách**: Tự động kích hoạt cơ chế bàn giao minh bạch cho con người (*Handover*) theo chuẩn 30 giây.
5. **Dữ liệu đầu vào không hợp lệ**: Chặn ngày bay trong quá khứ, số điện thoại sai định dạng ngay từ tầng tiền xử lý dữ liệu.

---

## 2. RANH GIỚI KIẾN TRÚC: MODEL VS. HARNESS

Một trong những bài học cốt lõi nhất của môn học SE373 (*Slide 10, 11*) là **sự phân định ranh giới rành mạch giữa Model và Harness**:

```
+──────────────────────────────────────────────────────────────────────────────+
|                       HỆ THỐNG KIỂM SOÁT AGENT (HARNESS)                     |
|                                                                              |
|  [01. Dựng ngữ cảnh] ───────► (Gửi Prompt, Context & Tools)                 |
|         ▲                                   │                                |
|         │                                   ▼                                |
|  [05. Xét điều kiện dừng]         +───────────────────+                      |
|         ▲                         |  FOUNDATION LLM   |                      |
|         │                         | (Groq / Gemini)   | ──► Sinh tool_calls  |
|  [04. Computational Sensor        +───────────────────+           │          |
|       Soi Database thực tế]                                       │          |
|         ▲                                                         │          |
|         │                 (Lớp 3: AccessControl Intercept)        ▼          |
|  [03. Harness gọi Tool] ◄─────────────────────────────────────────+          |
|         │                                                                    |
|         ▼                                                                    |
|  (Lớp 4: LoopDetector quét lặp & bế tắc sau observation)                     |
+──────────────────────────────────────────────────────────────────────────────+

```

* **Foundation Model (LLM)**: Đóng vai trò là "bộ não suy luận" (Groq Qwen 3.8-27b hoặc Gemini 1.5-Flash). Model đọc ngữ cảnh hội thoại và đề xuất bước hành động tiếp theo thông qua tool calling hoặc đưa ra câu trả lời. Model **không trực tiếp thao tác Database**, **không tự quyết định việc dừng an toàn**, và **không thể tin cậy tuyệt đối** vào lời tự tuyên bố của nó.
* **Lớp Vỏ Kiểm Soát (Harness)**: Là 100% mã nguồn Python truyền thống do lập trình viên thiết kế để bọc bên ngoài chu trình của Agent:
* Kiểm tra tính hợp lệ của dữ liệu đầu vào (`DataConstraintsHarness`).
* Đánh chặn và kiểm quyền trước khi gọi công cụ (`AccessControlHarness`).
* Thực thi tool nội bộ an toàn và chuẩn hóa kết quả đầu ra dạng JSON (`flight_tools.py`).
* Bắt các chu kỳ lặp và tình trạng bế tắc không tiến triển (`LoopDetector`).
* Kiểm chứng chéo trạng thái hoàn thành trực tiếp vào cơ sở dữ liệu (`CompletionCriteriaHarness`).
* Xuất báo cáo bàn giao chuẩn mực cho con người khi gặp sự cố (`HandoverHarness`).



---

## 3. THIẾT KẾ VÀ CÀI ĐẶT 5 LỚP HARNESS CHUYÊN SÂU

Trong thư mục `harness/`, chúng tôi cài đặt trọn vẹn 5 lớp kiểm soát độc lập được kết nối qua bộ điều phối trung tâm `base_harness.py`:

### 3.1. Lớp 1: Ràng buộc là dữ liệu (`DataConstraintsHarness`) 

* **Vấn đề giải quyết**: Ngăn chặn dữ liệu rác hoặc dữ liệu phi lý đi vào chuỗi suy luận của Agent, đồng thời chống hiện tượng trôi mục tiêu (*Goal Drift*) khi hội thoại kéo dài.
* **Cài đặt kỹ thuật**: Thực hiện thẩm định định dạng dữ liệu hoàn toàn bằng logic Python thuần (0 token, 0 ms):
* Kiểm tra ngày bay: Ngày khởi hành không được nằm trong quá khứ so với thời điểm hiện tại.
* Kiểm tra số lượng hành khách: Phải thuộc khoảng từ 1 đến 9 khách.
* Kiểm tra số điện thoại liên hệ: Phải tuân theo định dạng chuẩn 10 chữ số của Việt Nam (bắt đầu bằng đầu số hợp lệ `03`, `05`, `07`, `08`, `09`).
* Kiểm tra mã sân bay: Chuẩn hóa 3 ký tự viết hoa thuộc danh mục sân bay IATA khả dụng.



### 3.2. Lớp 2: Tiêu chí hoàn thành kiểm bằng code (`CompletionCriteriaHarness`) 

* **Vấn đề giải quyết**: LLM thường sinh ảo giác (*hallucination*), tự khẳng định đã đặt vé thành công trong khi chưa thực hiện gọi tool hoặc giao dịch thất bại.
* **Cài đặt kỹ thuật**: Đóng vai trò là một **Computational Sensor**. Hàm đánh giá bỏ qua văn bản trả lời của LLM và kiểm tra chéo trực tiếp vào bộ nhớ cơ sở dữ liệu `BOOKINGS`:
1. Mã booking (`BKxxxx`) phải tồn tại thực sự trong Database.
2. Trường `status == 'confirmed'`.
3. Trường `paid == True` (đã thực thi thành công tool `pay_booking`).
4. Thông tin chuyến bay, họ tên hành khách và hạng ghế phải khớp tuyệt đối với yêu cầu của kịch bản.



### 3.3. Lớp 3: Kiểm soát phân quyền & Phê duyệt trước thực thi (`AccessControlHarness`) 

* **Vấn đề giải quyết**: Ngăn chặn rủi ro tài chính và việc người dùng vượt quyền gọi các công cụ nhạy cảm.
* **Cài đặt kỹ thuật**:
* **Phân quyền RBAC**: Lọc danh sách công cụ được phép hiển thị cho Agent dựa trên vai trò người dùng:
* `guest`: Chỉ được gọi các công cụ tra cứu (`search_flights`, `get_flight_details`, `check_seat_availability`, `get_airport_info`).
* `user`: Được phép thêm `book_flight`, `pay_booking`, `cancel_booking`.
* `admin`: Toàn quyền hệ thống.


* **Pre-execution Authorization Guardrail**: Hàm `intercept_and_authorize` can thiệp **TRƯỚC** khi tool nhạy cảm được chạy:
* Vé có thuộc tính `refundable == False` $\rightarrow$ Tạm ngưng, yêu cầu Human Approval.
* Tổng giá trị đơn hàng vượt ngưỡng tự duyệt (`> 1.500.000 VNĐ`) $\rightarrow$ Kích hoạt phê duyệt con người.





### 3.4. Lớp 4: Phát hiện lặp & Bế tắc tiến trình (`LoopDetector`) 

* **Vấn đề giải quyết**: Agent rơi vào bế tắc (Stall) hoặc lặp vô tận (gọi đi gọi lại cùng một tool với cùng bộ tham số khi gặp chuyến bay hết chỗ hoặc lỗi mạng).
* **Cài đặt kỹ thuật**: Sử dụng cửa sổ trượt (Sliding Window) giám sát 3 tín hiệu độc lập:
1. *Trùng hành động (Action Repetition)*: Dấu vân tay băm `(tool_name, sorted_args)` xuất hiện lặp lại $\ge 2$ lần.
2. *Trùng quan sát (Observation Repetition)*: Các hành động trả về nội dung quan sát giống hệt nhau liên tiếp.
3. *Bế tắc không tiến triển (Stall Detection)*: Số lượng thông tin mới hoặc trạng thái bài toán đứng yên qua $\ge 3$ vòng lặp liên tục.



### 3.5. Lớp 5: Bàn giao chuẩn hóa cho con người (`HandoverHarness`) 

* **Vấn đề giải quyết**: Khi gặp sự cố bất khả thi hoặc cần con người phê duyệt, hệ thống không được dừng đột ngột mà phải cung cấp đầy đủ thông tin để người vận hành xử lý trong vòng 30 giây.
* **Cấu trúc biên bản bàn giao chuẩn 3 phần (`create_handover_summary`)**:
1. *Trạng thái hiện tại*: Tóm tắt chi tiết các thông số nghiệp vụ đã thu thập (Mã chuyến, hành khách, giá tiền, tình trạng hoàn vé, trạng thái thanh toán).
2. *Những gì đã thử*: Ghi nhận hành động gần nhất và phản hồi thực tế từ hệ thống.
3. *Hành động cần quyết định*: Đưa ra câu hỏi hành động trực diện để người vận hành trả lời (ví dụ: *"Phê duyệt xác nhận thanh toán cho booking BK1003?"*).



---

## 4. CÀI ĐẶT 3 MẪU THIẾT KẾ SUY LUẬN (REASONING PATTERNS)

Dự án cài đặt độc lập 3 mẫu thiết kế đại diện cho các kiến trúc Agentic Engineering phổ biến:

### 4.1. Mẫu 1: ReAct Agent (Reasoning + Acting)

* **Cơ sở khoa học**: Vận hành theo chu trình liên hoàn khép kín:

$$\text{Thought} \longrightarrow \text{Action} \longrightarrow \text{Observation} \longrightarrow \text{Lặp lại...}$$


* **Đặc điểm cài đặt trong `agents/react_agent.py**`:
* Agent tự do quyết định gọi tool nào dựa trên quan sát tức thời của môi trường.
* Tích hợp lớp kiểm quyền `intercept_and_authorize` trước mỗi lần gọi tool.
* Nạp kết quả vào ngữ cảnh và kiểm tra ngắt dừng thông qua `LoopDetector` và `CompletionCriteria` ngay sau mỗi bước.


* **Ưu điểm**: Khả năng thích ứng tức thời rất cao, tự đổi hướng mượt mà khi dữ liệu thay đổi.
* **Nhược điểm**: Lịch sử trao đổi tích lũy liên tục làm gia tăng độ dài ngữ cảnh và chi phí token.

### 4.2. Mẫu 2: Plan-then-Execute Agent (LangGraph StateGraph)

* **Cơ sở khoa học**: Tách biệt hoàn toàn pha Lập kế hoạch (Planning) và pha Thực thi (Execution).
* **Đặc điểm cài đặt trong `agents/plan_execute_agent.py**`:
* Xây dựng bằng `StateGraph` với 3 nodes: `Planner` $\rightarrow$ `Executor` $\rightarrow$ `Replanner`.
* Node `Planner` phân tích yêu cầu ban đầu và tạo danh sách các bước tuần tự (Ví dụ: Bước 1: Tìm chuyến $\rightarrow$ Bước 2: Kiểm tra ghế $\rightarrow$ Bước 3: Giữ chỗ $\rightarrow$ Bước 4: Thanh toán).
* Node `Executor` thực thi từng bước thông qua một sub-agent.
* Node `Replanner` đánh giá lại tiến trình sau mỗi bước để quyết định tiếp tục thực hiện bước kế tiếp hay kết thúc với thông điệp `DONE:`.


* **Ưu điểm**: Kế hoạch rõ ràng, cấu trúc minh bạch, số lần gọi công cụ ít.
* **Nhược điểm (Tính dễ gãy - Plan Brittleness)**: Kế hoạch lập từ đầu dễ bị lỗi thời (*Stale Plan*) khi môi trường trả về kết quả không lường trước.

### 4.3. Mẫu 3: Mẫu Lai (Hybrid Agent / Phân cấp Goals + ReAct Sub-agents)

* **Cơ sở khoa học**: Kết hợp phân rã mục tiêu cấp cao và suy luận phản xạ cấp thấp.
* **Đặc điểm cài đặt trong `agents/hybrid_agent.py**`:
* **Tầng ngoài (Outer Loop)**: High-level Planner chia yêu cầu phức tạp thành 2–3 Mục tiêu độc lập (Goals) theo định dạng chuẩn `GOAL: [tên] | TASK: [mô tả]`.
* **Tầng trong (Inner Loop)**: Mỗi Goal được bàn giao cho một ReAct Sub-agent độc lập thực thi và giải quyết trọn vẹn.
* **Chốt chặn Handover**: Sau mỗi Goal, hệ thống rà soát trạng thái booking và gọi `HandoverHarness` để phát hiện các điều kiện cần con người can thiệp.
* **Synthesizer**: LLM tổng hợp kết quả của toàn bộ các Goals thành văn bản phản hồi hoàn chỉnh cho người dùng.


* **Ưu điểm**: Cân bằng tối ưu giữa việc giữ vững định hướng mục tiêu dài hạn và khả năng thích ứng linh hoạt trước biến cố.

---

## 5. KẾT QUẢ THỰC NGHIỆM VÀ BENCHMARK ĐỊNH LƯỢNG

Hệ thống sử dụng file `evaluation/run_evaluation.py` để chạy benchmark tự động và đo đạc định lượng hiệu năng của cả 3 mẫu Agent trên bộ **10 Test Cases** chuẩn hóa.

### 5.1. Thiết kế bộ 10 Test Cases kiểm thử đa chiều

| Mã Case | Nhóm Thử Nghiệm | Kịch Bản & Thử Thách Kỹ Thuật |
| --- | --- | --- |
| **`TC01`** | **Happy Path (Search)** | Tìm chuyến bay từ SGN đi DAD ngày 2026-10-07 cho 1 người. Kiểm tra khả năng tra cứu cơ bản. |
| **`TC02`** | **Happy Path (Book & Pay)** | Đặt vé VN122 ngày 2026-10-07 cho Nguyen Van A và thanh toán. Đo lường chu trình đầy đủ `book_flight` $\rightarrow$ `pay_booking`. |
| **`TC03`** | **Error Handling (Cancel)** | Yêu cầu hủy booking mã BK9999 không tồn tại. Kiểm tra khả năng xử lý ngoại lệ và trả lời minh bạch. |
| **`TC04`** | **Complex Constraints** | Tìm và đặt vé SGN đi DAD sáng ngày 2026-10-07 dưới 2 triệu, bay trước 12:00 cho Le Thi B. Kiểm tra lọc đa ràng buộc. |
| **`TC05`** | **Access Control (RBAC)** | Role `guest` cố tình đặt vé VN101. Thử thách cơ chế chặn quyền của Lớp 3 Harness. |
| **`TC06`** | **Human Approval** | Đặt chuyến VJ101 ngày 2026-10-20 (vé không hoàn tiền `refundable: False`). Kiểm tra chốt chặn duyệt con người. |
| **`TC07`** | **Data Constraints** | Tìm vé HAN đi SGN ngày 2020-01-01 (trong quá khứ). Kiểm tra bộ lọc dữ liệu của Lớp 1 Harness. |
| **`TC08`** | **Stall & Sold-Out Case** | Đặt vé chuyến VJ604 ngày 2026-10-07 (`available_seats = 0`). Kiểm tra xử lý tình huống hết chỗ. |
| **`TC09`** | **Handover (Nhóm đông)** | Đặt 6 vé chuyến VN201 ngày 2026-10-20. Kiểm tra kích hoạt Handover khi số lượng khách $> 5$. |
| **`TC10`** | **Multi-step Info** | Tra cứu thông tin terminal sân bay DAD và số ghế còn lại của chuyến VN201. Kiểm tra gọi kết hợp 2 tools tra cứu. |

---

### 5.2. Bảng tổng hợp so sánh các chỉ tiêu khoa học

*Dữ liệu thực nghiệm đo đạc thực tế từ quá trình chạy tự động 10 test cases trên nền tảng Groq (Qwen 3.8-27b):*

| Chỉ số đánh giá | ReAct Pattern | Plan-then-Execute | Hybrid Pattern (Mẫu Lai) |
| --- | --- | --- | --- |
| **Tỷ lệ hoàn thành (Success Rate)** | **70.0%** (7/10) | **20.0%** (2/10) | **50.0%** (5/10) |
| **Thời gian phản hồi TB (Latency)** | 37.60 giây | **29.92 giây** | 57.31 giây |
| **Số lần gọi Tool TB (Tool Calls)** | 5.1 lượt | **2.2 lượt** | 5.6 lượt |
| **Số tin nhắn ngữ cảnh TB (Context Messages)** | 8.1 tin nhắn | **5.6 tin nhắn** | 11.2 tin nhắn |
| **Số ca kiểm thử vượt qua (Passed)** | **7/10** | **2/10** | **5/10** |

```text
Biểu đồ trực quan tỷ lệ thành công (Success Rate):
  • ReAct             ██████████████░░░░░░  70% (Linh hoạt, thích ứng tốt nhất)
  • Plan-then-Execute ████░░░░░░░░░░░░░░░░  20% (Nhanh nhất nhưng dễ gãy kế hoạch)
  • Hybrid (Mẫu Lai)  ██████████░░░░░░░░░░  50% (Cân bằng, hỗ trợ Handover tốt)

```

---

### 5.3. Ma trận chi tiết kết quả thực nghiệm (Detailed Matrix)

Bảng chi tiết 30 lượt chạy thực nghiệm độc lập (10 Test Cases $\times$ 3 Mẫu Agent):

| Case ID | ReAct Pattern | Plan-then-Execute | Hybrid Pattern (Mẫu Lai) | Đánh Giá Vai Trò Harness |
| --- | --- | --- | --- | --- |
| `TC01` | ✅ Pass (3.2s, 2 calls) | ✅ Pass (26.2s, 2 calls) | ❌ Fail (61.9s, 4 calls) | Harness ghi nhận báo cáo Handover vé không hoàn tiền tại Hybrid. |
| `TC02` | ✅ Pass (35.3s, 9 calls) | ❌ Fail (58.8s, 8 calls) | ✅ Pass (48.7s, 6 calls) | Sensor xác thực thành công mã booking BK1001 và BK1005 trong Database. |
| `TC03` | ❌ Fail (19.9s, 2 calls) | ❌ Fail (22.6s, 2 calls) | ❌ Fail (40.8s, 2 calls) | Sensor nhận diện đúng: Mã BK9999 không tồn tại nên không có thao tác hủy vé. |
| `TC04` | ✅ Pass (84.0s, 9 calls) | ❌ Fail (27.6s, 2 calls) | ❌ Fail (43.0s, 2 calls) | ReAct lọc đúng chuyến rẻ nhất dưới 2 triệu và tự động đặt vé BK1002. |
| `TC05` | ❌ Fail (12.1s, 2 calls) | ❌ Fail (14.6s, 2 calls) | ❌ Fail (35.9s, 2 calls) | **Lớp 3 AccessControl chặn thành công**: Role `guest` không được phép đặt vé. |
| `TC06` | ✅ Pass (69.5s, 9 calls) | ❌ Fail (RateLimit) | ❌ Fail (39.2s, 2 calls) | ReAct kích hoạt giữ chỗ BK1003 cho chuyến VJ101 sau khi có phê duyệt. |
| `TC07` | ✅ Pass (23.3s, 2 calls) | ✅ Pass (21.6s, 2 calls) | ✅ Pass (36.4s, 4 calls) | **Lớp 1 DataConstraints chặn đúng**: Báo rõ ngày bay trong quá khứ không hợp lệ. |
| `TC08` | ❌ Fail (35.7s, 4 calls) | ❌ Fail (25.1s, 0 calls) | ✅ Pass (138.0s, 21 calls) | Chuyến VJ604 hết chỗ (`seats: 0`); Hybrid kiên trì tìm giải pháp và đặt vé BK1006. |
| `TC09` | ✅ Pass (71.0s, 9 calls) | ❌ Fail (57.6s, 4 calls) | ✅ Pass (86.6s, 9 calls) | Đặt 6 vé kích hoạt Handover nhóm đông; ReAct và Hybrid đặt thành công BK1004/BK1007. |
| `TC10` | ✅ Pass (22.0s, 3 calls) | ❌ Fail (RateLimit) | ✅ Pass (42.7s, 4 calls) | Cả ReAct và Hybrid tra cứu thành công thông tin terminal và số ghế trống. |

---

### 5.4. Phân tích chuyên sâu các đánh đổi (Trade-offs Analysis) & Failure Modes

Từ kết quả thực nghiệm định lượng trên, nhóm nghiên cứu rút ra 4 phát hiện khoa học:

#### 1. Sự linh hoạt của ReAct trước môi trường biến động

* ReAct đạt tỷ lệ thành công cao nhất (**70.0%**) nhờ cơ chế liên tục đối thoại với môi trường qua từng observation.
* Tại các ca phức tạp như **TC04** (nhiều ràng buộc giá và giờ bay) hoặc **TC06**, ReAct nhận diện chuyến bay phù hợp, tuần tự gọi `book_flight` để lấy mã giữ chỗ rồi gọi tiếp `pay_booking` để hoàn tất thanh toán. Nhược điểm của ReAct là thời gian xử lý tích lũy theo số bước lặp và số lần gọi LLM tăng cao.

#### 2. Tính dễ gãy của Plan-then-Execute khi gặp biến cố

* Plan-then-Execute đạt tốc độ trung bình nhanh nhất (**29.92s**) và số lượt gọi tool ít nhất (**2.2 lượt**), nhưng tỷ lệ thành công chỉ đạt **20.0%**.
* *Nguyên nhân cốt tử*: Khi lập kế hoạch trước, Planner sinh ra một danh sách hành động tĩnh. Khi bước 1 trả về danh sách chuyến bay nhưng người dùng chưa cung cấp đủ dữ liệu thanh toán hoặc chuyến bay có ràng buộc phát sinh, chuỗi thực thi tuần tự bị gãy hoàn toàn. Hơn nữa, việc gọi LLM nhiều lần độc lập trong thời gian ngắn (Planner $\rightarrow$ Executor $\rightarrow$ Replanner) khiến mô hình dễ chạm trần hạn mức Rate Limit (TC06, TC10).

#### 3. Mẫu Lai (Hybrid) và sự bùng nổ ngữ cảnh

* Mẫu Lai đạt tỷ lệ thành công trung bình (**50.0%**), thể hiện khả năng vượt trội ở các ca khó như **TC08** (giải quyết tình huống hết chỗ) và **TC09** (xử lý đoàn đông người).
* Tuy nhiên, do cấu trúc đa tầng (High-level Planner $\rightarrow$ Goals $\rightarrow$ ReAct Sub-agents $\rightarrow$ Synthesizer), số lượng tin nhắn trao đổi tích lũy lên tới **11.2 messages**, đẩy độ trễ trung bình lên **57.31 giây** (cao nhất trong 3 mô hình).

#### 4. Hiệu quả kiểm soát an toàn của Lớp Harness

* **Bảo vệ quyền hạn (TC05)**: Lớp `AccessControlHarness` đã chặn đứng lệnh gọi công cụ đặt vé của role `guest`, bảo vệ hệ thống khỏi việc tạo booking trái phép.
* **Chống ảo giác bằng Computational Sensor (TC03, TC08)**: Lớp `CompletionCriteriaHarness` truy vấn trực tiếp vào Database thực tế, ngăn chặn việc LLM tự nhận hoàn thành khi giao dịch chưa được ghi nhận.
* **Kích hoạt Handover chuẩn 30 giây (TC01 - Hybrid)**: Hệ thống nhận diện chính xác vé không hoàn tiền và xuất biên bản bàn giao đầy đủ 3 phần cho con người phê duyệt.

---

## 6. CÁC THÁCH THỨC KỸ THUẬT & GIẢI PHÁP ĐỘT PHÁ

### 6.1. Tách biệt chu trình Giữ chỗ (`book_flight`) và Thanh toán (`pay_booking`)

* **Vấn đề**: Trong các hệ thống thông thường, tool đặt vé thường trừ tiền ngay trong một bước, khiến cơ chế kiểm quyền không thể can thiệp kịp thời.
* **Giải pháp**: Tách quy trình nghiệp vụ thành 2 pha độc lập:
* `book_flight`: Chỉ tạo bản ghi giữ chỗ ở trạng thái `held`, sinh mã `BKxxxx` và khóa chỗ tạm thời.
* `pay_booking`: Yêu cầu mã booking hợp lệ để xác nhận trừ tiền và chuyển trạng thái thành `confirmed`.
Nhờ cấu trúc này, Lớp 3 Harness có thể chặn bắt chính xác hành vi thanh toán hoặc vé không hoàn tiền để xin phê duyệt của con người trước khi trừ tiền.



### 6.2. Kiểm soát bùng nổ ngữ cảnh và khắc phục cắt cụt dữ liệu trong Plan-then-Execute

* **Vấn đề**: Ban đầu, Node Executor cắt ngắn kết quả của bước trước ở mức 300 ký tự (`[:300]`), khiến dữ liệu danh sách chuyến bay dạng JSON bị đứt đoạn, dẫn đến việc Replanner báo lỗi thiếu dữ liệu.
* **Giải pháp**: Mở rộng dung lượng lưu trữ ngữ cảnh lên 1500 ký tự, đồng thời tinh chỉnh prompt của Node Planner để chỉ lập các bước tra cứu khi người dùng có nhu cầu tìm kiếm, tránh việc lập kế hoạch thanh toán thừa thãi khi chưa có đủ thông tin hành khách.

### 6.3. Kiến trúc LLM Factory linh hoạt đa nền tảng (Groq / Gemini)

* **Vấn đề**: Cần một giải pháp quản lý khởi tạo mô hình tập trung, dễ dàng chuyển đổi qua lại giữa Groq (tốc độ suy luận cao, miễn phí) và Google Gemini mà không phải sửa đổi mã nguồn ở từng agent.
* **Giải pháp**: Xây dựng module `llm_factory.py` áp dụng Factory Pattern. Module tự động đọc biến môi trường từ `.env` để cấu hình tham số `temperature=0`, `max_retries` và nạp instance tương ứng của `ChatGroq` hoặc `ChatGoogleGenerativeAI` một cách trong suốt.

---

## 7. HƯỚNG DẪN CÀI ĐẶT & TÁI HIỆN KẾT QUẢ (REPRODUCTION GUIDE)

Mã nguồn được cấu trúc theo chuẩn module hóa bằng môi trường ảo Python (`.venv`).

### 7.1. Cấu trúc thư mục dự án

```text
BTVN3/
├── agents/                      # 3 Kiến trúc Agent (ReAct, Plan-then-Execute, Hybrid)
├── harness/                     # 5 Lớp Harness và bộ điều phối trung tâm
├── tools/                       # 8 công cụ nghiệp vụ và Mock Database (15 sân bay, 24 chuyến)
├── evaluation/                  # 10 Test Cases, Metrics và Script chạy benchmark
├── llm_factory.py               # Quản trị khởi tạo mô hình tập trung
├── main.py                      # Giao diện CLI dòng lệnh tương tác
├── app.py                       # Giao diện Web UI hiện đại (Flask)
├── requirements.txt             # Danh mục thư viện phụ thuộc
├── .env.example                 # File mẫu cấu hình biến môi trường
└── README.md                    # Hướng dẫn chi tiết sử dụng

```

### 7.2. Các bước tái hiện kết quả thực nghiệm

1. **Khởi tạo môi trường ảo và cài đặt thư viện**:
```powershell
cd Airline_ticket_booking_Agent
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

```


2. **Cấu hình biến môi trường (`.env`)**:
Tạo file `.env` tại thư mục gốc với nội dung:
```env
GROQ_API_KEY="gsk_your_groq_api_key_here"
GROQ_MODEL="qwen/qwen3.8-27b"

```


3. **Chạy Benchmark tự động đánh giá 3 Agent Patterns**:
```powershell
python evaluation/run_evaluation.py

```


Hệ thống sẽ chạy tuần tự 10 test cases qua 3 Agent, in bảng so sánh hiệu năng ASCII ra màn hình console và tự động lưu kết quả vào file `evaluation/results.json`.
4. **Trải nghiệm giao diện Web UI tương tác**:
```powershell
python app.py

```


Mở trình duyệt truy cập địa chỉ `http://localhost:5000` để trải nghiệm giao diện chat thời gian thực hỗ trợ chọn Role, chọn Agent Pattern và hiển thị trạng thái 5 modules Harness.
5. **Trải nghiệm giao diện dòng lệnh (CLI Terminal)**:
```powershell
python main.py

```



---

## 8. KẾT LUẬN

Dự án Airline Ticket Booking Agent đã hoàn thành trọn vẹn các mục tiêu đề ra của môn học **SE373 - Kỹ thuật Xây dựng Hệ thống Agentic AI**:

1. **Khẳng định vai trò thiết yếu của Lớp Harness**: Chứng minh rằng mô hình ngôn ngữ lớn (LLM) chỉ là công cụ tạo sinh suy luận; một hệ thống Agentic AI an toàn và đáng tin cậy trong môi trường doanh nghiệp bắt buộc phải có **lớp vỏ Harness kiểm soát độc lập bằng code truyền thống** để quản trị rủi ro tài chính, ngăn ngừa vòng lặp và đảm bảo tính toán vẹn dữ liệu.
2. **Làm chủ 3 kiến trúc suy luận Agent**: Hiện thực hóa thành công các mẫu thiết kế ReAct, Plan-then-Execute và Hybrid bằng LangChain và LangGraph.
3. **Chứng minh thực nghiệm khoa học**: Cung cấp số liệu benchmark định lượng rõ ràng, minh chứng cho các luận điểm trong bài giảng:
* ReAct linh hoạt nhất trong môi trường động nhưng chi phí ngữ cảnh tích lũy cao.
* Plan-then-Execute tiết kiệm tài nguyên nhất khi bài toán tĩnh, nhưng dễ bị gãy luồng khi gặp tình huống phát sinh.
* Mẫu Lai (Hybrid) phân cấp mục tiêu rõ ràng và tích hợp cơ chế Handover chuẩn mực, là kiến trúc phù hợp cho các bài toán phức tạp có sự tham gia của con người (*Human-in-the-loop*).



---

*Báo cáo được hoàn thành và nộp theo chuẩn học thuật của Khoa Công nghệ Phần mềm – Trường Đại học Công nghệ Thông tin (UIT).*