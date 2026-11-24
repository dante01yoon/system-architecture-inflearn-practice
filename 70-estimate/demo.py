"""서점 리뷰 기능의 규모 어림셈. 1 = 글만 있는 리뷰, 2 = 사진 두 장을 붙인 리뷰."""
import sys

from est import DAY, bits, estimate, rough, size

DAU, WRITES, RATIO, YEARS, COPIES, PEAK = 10_000_000, 0.1, 100, 5, 3, 5   # 모두 가정
TEXT, PHOTO = 1_000, 1_000 + 2 * 500_000                                  # 리뷰 한 건: 글 1 KB · 사진 500 KB × 2


def show(name, payload):
    e = estimate(DAU, WRITES, RATIO, payload, YEARS, COPIES, PEAK)
    print(f"[{name}] 리뷰 한 건 {size(payload)}")
    print(f"가정: DAU {DAU:,} · 한 명이 하루 {WRITES}건 쓰기 · 읽기:쓰기 {RATIO}:1")
    print(f"      보관 {YEARS}년 · 복제 {COPIES}벌 · 최대 = 평균 × {PEAK}")
    print(f"1) 하루 쓰기 {e['per_day']:,.0f}건 ÷ {DAY:,}초")
    print(f"   쓰기 QPS {e['write_qps']:.1f} → 어림 {rough(e['write_qps']):,}")
    print(f"2) 읽기 QPS {e['read_qps']:,.0f} → 어림 {rough(e['read_qps']):,}")
    print(f"3) 최대 QPS 쓰기 {e['peak_write']:,.0f} · 읽기 {e['peak_read']:,.0f}")
    print(f"4) 저장 1년 {size(e['year'])}")
    print(f"   × {YEARS}년 × {COPIES}벌 = {size(e['total'])} → 어림 {size(rough(e['total']))}")
    print(f"5) 대역폭 들어옴 {size(e['in'])}/s · 나감 {size(e['out'])}/s")
    print(f"   가장 몰릴 때 나감 {size(e['peak_out'])}/s = {bits(e['peak_out'])}")
    return e


if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else '1'
    if part == '1':
        show('글만', TEXT)
    else:
        e = show('사진 두 장', PHOTO)
        t = estimate(DAU, WRITES, RATIO, TEXT, YEARS, COPIES, PEAK)
        print(f"글만일 때보다 저장 약 {rough(e['total'] / t['total']):,}배 · QPS는 그대로")
