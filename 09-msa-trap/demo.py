"""서점 서비스 넷의 설정 두 개를 진단한다: 분산 모놀리스와 고친 모양."""
from trap import diagnose, load


def report(name, cfg):
    r = diagnose(cfg)
    print(f"   배포 {len(cfg['deploys'])}번 기록, 서비스 {len(cfg['dbs'])}개")
    for a, b, n in r["lockstep"]:
        print(f"   [같이 배포] {a} + {b}: {n}번 모두 함께")
    for c in r["chains"]:
        print(f"   [호출 사슬] {' -> '.join(c)} ({len(c) - 1}홉)")
    for db, svcs in r["shared"].items():
        print(f"   [공유 DB] {db}: {', '.join(svcs)}")
    n = sum(len(v) for v in r.values())
    print(f"   => {name}: 신호 {n}개" + (" (분산 모놀리스 의심)" if n else " (독립 배포 가능)"))


def main():
    print("1) 기준: 늘 같이 배포 / 동기 호출 2홉 초과 / DB 공유")
    print("2) 지금 서점 (distributed.json)")
    report("distributed", load("distributed.json"))
    print("3) 고친 서점 (fixed.json)")
    report("fixed", load("fixed.json"))


if __name__ == "__main__":
    main()
