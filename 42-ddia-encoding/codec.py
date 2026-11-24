"""번호 + 길이 + 값으로 적는 교육용 바이너리 인코딩(프로토콜 버퍼 흉내)."""
import struct

V1 = {1: ("order_id", "int"), 2: ("customer", "str"), 3: ("books", "list"), 4: ("total", "int")}
V2 = {**V1, 5: ("gift_wrap", "bool")}            # 새 필드는 새 번호로
DEFAULT = {"int": 0, "str": "", "list": [], "bool": False}


def _pack(kind, v):
    if kind == "int":
        return struct.pack(">I", v)                 # 4바이트 정수
    if kind == "bool":
        return b"\x01" if v else b"\x00"
    return v.encode("utf-8")


def _unpack(kind, b):
    if kind == "int":
        return struct.unpack(">I", b)[0]
    if kind == "bool":
        return b == b"\x01"
    return b.decode("utf-8")


def encode(order, schema):
    out = b""
    for tag, (name, kind) in schema.items():
        if name not in order:
            continue
        values = order[name] if kind == "list" else [order[name]]
        for v in values:                            # 같은 번호를 여러 번(repeated)
            body = _pack("str" if kind == "list" else kind, v)
            out += struct.pack(">BB", tag, len(body)) + body
    return out


def fields(data):
    """바이트를 (번호, 값 바이트) 조각으로 자른다. 이름은 바이트 어디에도 없다."""
    i = 0
    while i < len(data):
        tag, n = struct.unpack(">BB", data[i:i + 2])
        yield tag, data[i + 2:i + 2 + n]
        i += 2 + n


def decode(data, schema):
    """모르는 번호는 길이만큼 건너뛰고, 없는 필드는 기본값으로 채운다."""
    order, skipped = {}, []
    for tag, body in fields(data):
        if tag not in schema:
            skipped.append(tag)
            continue
        name, kind = schema[tag]
        if kind == "list":
            order.setdefault(name, []).append(_unpack("str", body))
        else:
            order[name] = _unpack(kind, body)
    for name, kind in schema.values():
        order.setdefault(name, [] if kind == "list" else DEFAULT[kind])
    return order, skipped
