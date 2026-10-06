from collections import deque


class LoopDetector:
    def __init__(self, window: int = 6, repeat_k: int = 2, stall_n: int = 4):
        self.recent = deque(maxlen=window)
        self.k = repeat_k
        self.n = stall_n
        self.last_progress = None
        self.stall_count = 0

    def check(self, tool_name: str, tool_args: dict, progress: any = None) -> str | None:
        """
        Kiểm tra sau mỗi vòng lặp:
        - fp: fingerprint (tool, args đã sắp xếp)
        - Trả về 'LOOP' nếu trùng hành động >= k lần
        - Trả về 'STALL' nếu progress metric đứng yên >= n lần
        """
        # Chuẩn hóa tham số để so sánh chính xác
        norm_args = tuple(sorted((k, str(v)) for k, v in tool_args.items()))
        fingerprint = (tool_name, norm_args)

        if self.recent.count(fingerprint) + 1 >= self.k:
            return "LOOP"
        self.recent.append(fingerprint)

        if progress is not None:
            if progress == self.last_progress:
                self.stall_count += 1
            else:
                self.stall_count = 0
            self.last_progress = progress

            if self.stall_count >= self.n:
                return "STALL"

        return None

    def reset(self):
        self.recent.clear()
        self.last_progress = None
        self.stall_count = 0