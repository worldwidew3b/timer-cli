
from app.utils.notification import show_notification
import time

print("Тестируем уведомление...")
show_notification("Тестовое уведомление", "Это тестовое сообщение для проверки уведомлений")

# Подождем немного времени, чтобы убедиться, что уведомление появилось
time.sleep(2)
print("Тест завершен.")