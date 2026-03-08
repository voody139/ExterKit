# ExterKit

Вам не нужно засорять свой плагин сторонними файлами. Просто вставьте этот "Магический загрузчик" в самое начало вашего `main.py` (сразу после метаданных).

Он автоматически скачает актуальную версию `ExterKit` с GitHub в скрытый кэш Telegram (только при первом запуске) и моментально подключит её к вашему плагину!

```python
# --- МАГИЧЕСКИЙ ЗАГРУЗЧИК EXTERKIT ---
import sys, os, urllib.request
from org.telegram.messenger import ApplicationLoader

def _load_exterkit():
    cache_dir = ApplicationLoader.applicationContext.getCacheDir().getAbsolutePath()
    ek_path = os.path.join(cache_dir, "exterkit.py")
    
    # Скачиваем библиотеку, если её еще нет в кэше телефона
    if not os.path.exists(ek_path):
        try:
            # Ссылка на RAW файл с вашего GitHub
            url = "https://raw.githubusercontent.com/voodyminingg/exterkit/main/exterkit.py"
            urllib.request.urlretrieve(url, ek_path)
        except Exception as e:
            print(f"ExterKit download failed: {e}")
            return
            
    # Добавляем кэш в пути Python, чтобы можно было импортировать
    if cache_dir not in sys.path:
        sys.path.append(cache_dir)

_load_exterkit()
# --------------------------------------

# Теперь вы можете спокойно импортировать всё что угодно!
from exterkit import Dialogs, HookManager, AccountStorage, UIBuilder, Events, Action
from base_plugin import BasePlugin

class MySuperPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.hooks = HookManager(self)
        self.db = AccountStorage(self)
        
    # Ваш код плагина...```
