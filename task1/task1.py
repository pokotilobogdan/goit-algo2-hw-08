import random
from time import time, sleep
from collections import deque


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.windows_size = window_size     # in seconds
        self.max_requests = max_requests
        self.users_entries = dict()         # {'user_id': deque([time1, time2, ...])}
        # self.oldest_message = None          # тут буде час найстарішого в черзі повідомлення

    def _cleanup_window(self, current_time: float) -> None:
        '''
        Basically, перед кожною дією з чергою будемо викликати цю функцію, щоб вона видалила користувачів, яким вже можна писати повідомлення
        '''
        for user in list(self.users_entries.keys()):
            # Видаляємо всі застарілі записи про вхід користувачів
            while len(self.users_entries[user]) > 0 and current_time - self.users_entries[user][0] > self.windows_size:
                self.users_entries[user].popleft()
            # Якщо записів не залишилось, то видалимо й користувача зі словника, щоб не займав місця
            # (для цієї задачі це too much, але в цілому дія логічна)
            if len(self.users_entries[user]) == 0:
                del self.users_entries[user]

    def can_send_message(self, user_id: str) -> bool:
        self._cleanup_window(time())
        # Повертаємо True, якщо записів для даного користувача ще немає, або їх кількість не перевищує ліміту
        return user_id not in self.users_entries.keys() or len(self.users_entries[user_id]) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):  # очистка від старих записів відбувається при виклику self.can_send_message()
            current_time = time()
            if user_id not in self.users_entries.keys():
                self.users_entries[user_id] = deque([current_time,])
            else:
                self.users_entries[user_id].append(current_time)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        if self.can_send_message(user_id):  # очистка від старих записів відбувається при виклику self.can_send_message()
            return 0
        else:
            current_time = time()
            return self.windows_size - (current_time - self.users_entries[user_id][0])


# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Випадкова затримка від 0.1 до 1 секунди
        sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()
