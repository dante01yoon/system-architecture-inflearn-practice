"""주도되는 어댑터: 알림을 메일 대신 화면에 찍는다."""


class ConsoleNotifier:
    def send(self, text):
        print(f"   알림(콘솔): {text}")
