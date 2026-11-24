"""규모 어림셈: 하루 사용자 수(DAU)에서 QPS, 저장 용량, 대역폭까지. 숫자는 모두 설명을 위해 정한 가정이다."""
import math

DAY = 86_400                                   # 하루의 초 — 어림셈에서는 10^5로 본다
UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']    # 1,000배씩 (2^10 = 1,024 ≈ 10^3)


def rough(x):
    """유효숫자 한 자리로 반올림: 1,157 → 1,000, 5,787 → 6,000."""
    if x <= 0:
        return 0
    p = 10 ** math.floor(math.log10(x))
    return round(x / p) * p


def size(n):
    """바이트 수를 KB · MB · GB …로."""
    i = min(int(math.log10(n) // 3), len(UNITS) - 1) if n >= 1 else 0
    return f"{n / 1000 ** i:.3g} {UNITS[i]}"


def bits(bytes_per_s):
    """바이트/초를 네트워크 단위(비트/초)로: × 8."""
    b, i = bytes_per_s * 8, 0
    while b >= 1000 and i < 4:
        b, i = b / 1000, i + 1
    return f"{b:.3g} {['bps', 'Kbps', 'Mbps', 'Gbps', 'Tbps'][i]}"


def estimate(dau, writes_per_user, read_write, payload, years, copies, peak=5):
    """하루 쓰기 건수에서 출발해 QPS, 저장, 대역폭을 낸다(읽기 한 번 = 글 하나를 통째로 받기)."""
    per_day = dau * writes_per_user
    write_qps = per_day / DAY
    read_qps = write_qps * read_write
    yearly = per_day * 365 * payload
    return {
        'per_day': per_day, 'write_qps': write_qps, 'read_qps': read_qps,
        'peak_write': write_qps * peak, 'peak_read': read_qps * peak,
        'year': yearly, 'total': yearly * years * copies,
        'in': write_qps * payload, 'out': read_qps * payload, 'peak_out': read_qps * peak * payload,
    }
