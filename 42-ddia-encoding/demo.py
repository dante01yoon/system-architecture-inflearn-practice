"""python3 demo.py 1 → JSON 대 바이너리,  2 → 새 필드 더하기(상위·하위 호환),  3 → 이름 바꾸기 대 번호 바꾸기"""
import base64
import json
import sys

from codec import V1, V2, decode, encode, fields

ORDER = {"order_id": 1042, "customer": "minji", "books": ["DDIA", "Clean Code"], "total": 57600}


def one():
    js = json.dumps(ORDER).encode()
    bi = encode(ORDER, V1)
    print(f"1) 같은 주문, JSON {len(js)}바이트 / 바이너리 {len(bi)}바이트")
    print("2) 바이너리 안: 번호 · 길이 · 값 (이름은 없음)")
    for tag, body in fields(bi):
        print(f"   번호 {tag}  길이 {len(body):2d}  {body.hex(' ')}")
    big = 2 ** 53 + 1
    print(f"3) JSON 숫자 {big}")
    print(f"   double로 읽으면 {int(float(big))}  (1이 사라짐)")
    cover = bytes(range(200, 230))
    print(f"4) 표지 그림 {len(cover)}바이트 → JSON에는 Base64 {len(base64.b64encode(cover))}글자로")


def two():
    new = {**ORDER, "gift_wrap": True}
    data = encode(new, V2)
    old, skipped = decode(data, V1)
    print("1) 새 코드(v2)가 쓴 주문을 옛 코드(v1)가 읽기")
    print(f"   모르는 번호 {skipped} 건너뜀 → total={old['total']}  [상위 호환]")
    data = encode(ORDER, V1)
    got, _ = decode(data, V2)
    print("2) 옛 코드(v1)가 쓴 주문을 새 코드(v2)가 읽기")
    print(f"   gift_wrap 없음 → 기본값 {got['gift_wrap']}  [하위 호환]")
    print("3) 배포 중: v1 서버와 v2 서버가 같은 DB를 쓰고 읽는다")
    for w in ("v1", "v2"):
        for r in ("v1", "v2"):
            o, _ = decode(encode(new, {"v1": V1, "v2": V2}[w]), {"v1": V1, "v2": V2}[r])
            print(f"   {w} 서버가 쓰고 {r} 서버가 읽음 → 주문 {o['order_id']}, {o['total']}원")


def three():
    data = encode(ORDER, V1)
    renamed = {**V1, 4: ("amount", "int")}          # 이름만 바꿈, 번호 4 그대로
    got, _ = decode(data, renamed)
    print(f"1) 바이너리, 이름 total→amount (번호 4 그대로): amount={got['amount']}")
    js = json.loads(json.dumps(ORDER))
    print(f"2) JSON, 같은 이름 바꾸기: amount={js.get('amount', '없음')}")
    moved = {**V1}
    moved.pop(4)
    moved[6] = ("total", "int")                     # 번호를 4→6으로 바꿈
    got, skipped = decode(data, moved)
    print(f"3) 바이너리, 번호 4→6: 번호 {skipped} 건너뜀 → total={got['total']} (원래 57600)")


if __name__ == "__main__":
    {"1": one, "2": two, "3": three}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
