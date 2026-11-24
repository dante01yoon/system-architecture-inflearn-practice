"""복제 지연을 감추는 두 가지 읽기 규칙."""
import zlib


def read_your_writes(user_last_seq, leader, followers, key, now):
    """내가 쓴 번호까지 따라온 팔로워에서만 읽고, 없으면 리더에서 읽는다."""
    for f in followers:
        if f.position(now) >= user_last_seq:
            return f.name, f.read(key, now)
    return "leader", leader.read(key, now)


def sticky(user, followers):
    """같은 사용자는 늘 같은 팔로워로(이름의 해시로 고른다) → 시간이 거꾸로 가지 않는다."""
    return followers[zlib.crc32(user.encode()) % len(followers)]
