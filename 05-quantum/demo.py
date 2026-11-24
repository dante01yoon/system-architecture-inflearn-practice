"""서점 서비스의 퀀텀을 세고, 동기 호출 하나와 공유 DB 하나를 바꿔 본다."""
from pathlib import Path

from quanta import parse, quanta


def show(title, text):
    groups = quanta(*parse(text))
    print(title)
    for i, g in enumerate(groups, 1):
        print(f"   퀀텀 {i}: {' + '.join(g)}")
    print(f"   -> 서비스 {sum(map(len, groups))}개, 퀀텀 {len(groups)}개")


def main():
    shop = Path(__file__).with_name("shop.txt").read_text(encoding="utf-8")
    show("1) 지금 서점 (shop.txt)", shop)

    step2 = shop.replace("sync   order    notify", "async  order    notify")
    show("2) order -> notify 를 동기 호출에서 메시지로", step2)

    split_db = "db     catalog_db  catalog\ndb     stock_db    stock"
    step3 = step2.replace("db     shop_db  catalog  stock", split_db)
    show("3) catalog 와 stock 이 DB를 따로 가지면", step3)


if __name__ == "__main__":
    main()
