def compute_summary(results: list[dict]) -> dict:
    if not results:
        return {"success_rate": 0, "avg_latency": 0, "avg_steps": 0, "avg_messages": 0, "per_task_breakdown": {}}

    total = len(results)
    passed = sum(1 for r in results if r.get("success", False))
    total_latency = sum(r.get("latency", 0) for r in results)
    total_steps = sum(r.get("tool_calls", 0) for r in results)
    total_messages = sum(r.get("messages", 0) for r in results)

    # Phân rã theo task_type
    task_types = {}
    for r in results:
        tt = r.get("task_type", "unknown")
        if tt not in task_types:
            task_types[tt] = {"total": 0, "passed": 0}
        task_types[tt]["total"] += 1
        if r.get("success", False):
            task_types[tt]["passed"] += 1

    per_task = {
        tt: {
            "success_rate": round(v["passed"] / v["total"], 2),
            "passed": v["passed"],
            "total": v["total"],
        }
        for tt, v in task_types.items()
    }

    return {
        "success_rate": round(passed / total, 3),
        "avg_latency": round(total_latency / total, 2),
        "avg_steps": round(total_steps / total, 2),
        "avg_messages": round(total_messages / total, 2),
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "per_task_breakdown": per_task,
    }


def ascii_bar(value: float, max_width: int = 20) -> str:
    filled = round(value * max_width)
    empty = max_width - filled
    return "█" * filled + "░" * empty


def compare_agents(react_results: list[dict], plan_results: list[dict], hybrid_results: list[dict]) -> str:
    react_s = compute_summary(react_results)
    plan_s = compute_summary(plan_results)
    hybrid_s = compute_summary(hybrid_results)

    agents = [
        ("ReAct", react_s),
        ("Plan-then-Execute", plan_s),
        ("Hybrid", hybrid_s),
    ]

    lines = [
        "\n" + "=" * 70,
        "       BẢNG SO SÁNH HIỆU NĂNG VÀ ĐÁNH ĐỔI 3 AGENT PATTERNS (BTVN#3)",
        "=" * 70,
        f"{'Metric':<25} {'ReAct':>13} {'Plan-Execute':>15} {'Hybrid':>12}",
        "-" * 70,
        f"{'Tỷ lệ hoàn thành':<25} {react_s['success_rate']:>12.1%} {plan_s['success_rate']:>14.1%} {hybrid_s['success_rate']:>11.1%}",
        f"{'Thời gian TB (giây)':<25} {react_s['avg_latency']:>12.2f}s {plan_s['avg_latency']:>14.2f}s {hybrid_s['avg_latency']:>11.2f}s",
        f"{'Số tool calls TB':<25} {react_s['avg_steps']:>13.1f} {plan_s['avg_steps']:>15.1f} {hybrid_s['avg_steps']:>12.1f}",
        f"{'Số message TB (Context)':<25} {react_s['avg_messages']:>13.1f} {plan_s['avg_messages']:>15.1f} {hybrid_s['avg_messages']:>12.1f}",
        f"{'Số ca Pass':<25} {react_s['passed']:>10}/{react_s['total']} {plan_s['passed']:>12}/{plan_s['total']} {hybrid_s['passed']:>9}/{hybrid_s['total']}",
        "-" * 70,
        "\nBiểu đồ trực quan tỷ lệ thành công (Success Rate):",
        f"  • ReAct             {ascii_bar(react_s['success_rate'])} {react_s['success_rate']:.0%}",
        f"  • Plan-then-Execute {ascii_bar(plan_s['success_rate'])} {plan_s['success_rate']:.0%}",
        f"  • Hybrid (Lai)      {ascii_bar(hybrid_s['success_rate'])} {hybrid_s['success_rate']:.0%}",
        "\nĐánh giá chi tiết từng loại nhiệm vụ:",
    ]

    all_task_types = sorted(list(set().union(
        react_s["per_task_breakdown"].keys(),
        plan_s["per_task_breakdown"].keys(),
        hybrid_s["per_task_breakdown"].keys()
    )))

    for tt in all_task_types:
        r_sr = react_s["per_task_breakdown"].get(tt, {}).get("success_rate", 0)
        p_sr = plan_s["per_task_breakdown"].get(tt, {}).get("success_rate", 0)
        h_sr = hybrid_s["per_task_breakdown"].get(tt, {}).get("success_rate", 0)
        lines.append(f"  - [{tt:<8}] ReAct: {r_sr:>5.0%} | Plan-Execute: {p_sr:>5.0%} | Hybrid: {h_sr:>5.0%}")

    lines.extend([
        "\nNhận xét đánh đổi kiến trúc (Dựa theo slide 23, 26):",
        "  1. ReAct: Cực kỳ linh hoạt, giải quyết nhanh các tác vụ ngắn; rủi ro là tốn nhiều token khi lịch sử dài.",
        "  2. Plan-then-Execute: Tường minh, chi phí dự đoán được trước; nhưng dễ gãy khi gặp tình huống bất ngờ.",
        "  3. Hybrid (Lai): Cân bằng tối ưu giữa việc giữ định hướng mục tiêu và khả năng thích nghi khi gặp lỗi.",
        "=" * 70 + "\n"
    ])

    return "\n".join(lines)