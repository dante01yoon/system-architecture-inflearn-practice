"""같은 서점을 두 가지로 짰을 때, 모듈끼리 얼마나 얽혔는지 센다."""
from coupling import dependents, imports, show


def names(mods):
    return f" ({', '.join(sorted(mods))})" if mods else ""


def main():
    tight, loose = imports("shop_tight"), imports("shop_loose")

    print("1) 촘촘한 서점 shop_tight: 누가 누구를 import 하나")
    show(tight)

    print("2) 느슨한 서점 shop_loose: 누가 누구를 import 하나")
    show(loose)

    print("3) payment.py를 고치면 같이 확인할 모듈")
    for label, graph in (("shop_tight", tight), ("shop_loose", loose)):
        direct, reach = dependents(graph, "payment")
        print(f"   {label}: 바로 {len(direct)}개, 거쳐서 {len(reach)}개{names(reach)}")

    print("4) 대가: events.py를 고치면")
    direct, _ = dependents(loose, "events")
    print(f"   shop_loose: 바로 {len(direct)}개{names(direct)}")


if __name__ == "__main__":
    main()
