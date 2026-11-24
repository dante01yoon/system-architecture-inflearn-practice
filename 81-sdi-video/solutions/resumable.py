"""연습 풀이: 이어 올리기. 파일을 조각(part)으로 나눠 올리고, 끊긴 조각만 다시 보낸다(S3 multipart upload와 같은 생각)."""
import random

SIZE_MB, PART_MB, FAIL = 1000, 50, 0.15   # 1GB 파일 · 50MB 조각 · 조각마다 15% 끊김(가정)


def whole(rnd):
    """한 번에 올리기: 어디서든 끊기면 처음부터 다시."""
    sent = 0
    while True:
        for mb in range(0, SIZE_MB, PART_MB):
            sent += PART_MB
            if rnd.random() < FAIL:
                break
        else:
            return sent


def parts(rnd):
    """조각 올리기: 끊긴 조각만 다시. 서버는 받은 조각 번호를 기억한다."""
    sent, done = 0, set()
    n = SIZE_MB // PART_MB
    while len(done) < n:
        for i in range(n):
            if i in done:
                continue
            sent += PART_MB
            if rnd.random() >= FAIL:
                done.add(i)
    return sent


if __name__ == "__main__":
    w = sum(whole(random.Random(s)) for s in range(20)) / 20
    p = sum(parts(random.Random(s)) for s in range(20)) / 20
    print(f"1GB 올리기, 20번 평균 보낸 양: 처음부터 다시 {w:,.0f}MB · 조각 이어 올리기 {p:,.0f}MB")
    assert p < w
