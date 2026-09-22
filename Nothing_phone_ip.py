# nothing phone
from adbutils import adb
import time
import random
import re

d = adb.device("????")




def adb_cmd(cmd, retries=5, delay=5):
    global d
    for attempt in range(retries):
        try:
            return d.shell(cmd)
        except Exception as e:
            print(f"[adb_cmd] ошибка попытка {attempt+1}/{retries}: {e}")
            time.sleep(delay)
            try:
                d = adb.device("????")  # переподключаемся
            except:
                pass
    raise Exception(f"[adb_cmd] устройство недоступно после {retries} попыток")


def get_phone_state():
    res = adb_cmd("dumpsys power | grep mWakefulness")
    word="Dozing"
    try:
        res2=re.search(word,res).group(0)
        if res2:
            print("🤖 UNLOCK")
            adb_cmd("input keyevent 26 power")
            time.sleep(2)
            adb_cmd("input swipe 500 1200 500 500")
            return

    except AttributeError:
        print(2)
        adb_cmd("input swipe 500 1200 500 500")
        time.sleep(2)
        return






def touch(x1, y1, x2, y2, ):
    """Тап в случайную точку внутри области"""
    x = random.randint(x1, x2)
    y = random.randint(y1, y2)
    print(f"Тап:  {x}, {y}")
    d.shell(f"input tap {x} {y}")
    time.sleep(3)




def rotate_ip_NOTMAIN():
    get_phone_state()
    time.sleep(2)

    adb_cmd("am start -n com.android.chrome/com.google.android.apps.chrome.Main")
    time.sleep(6)
    adb_cmd('am start -a android.intent.action.VIEW -d "http://api.ipify.org"')
    time.sleep(6)
    check_ip()
    print("[*] Отключаем мобильные данные...")
    adb_cmd("am start -a android.settings.NETWORK_OPERATOR_SETTINGS")

    time.sleep(2)
    touch(334, 730, 335, 731, )
    time.sleep(2)
    touch(802, 1240, 840, 1280, )#2
    time.sleep(10)
    touch(334, 730, 335, 731, )
    time.sleep(5)

    print("[*] Включаем мобильные данные...")
    adb_cmd("am start -n com.android.chrome/com.google.android.apps.chrome.Main")
    time.sleep(6)
    adb_cmd('am start -a android.intent.action.VIEW -d "http://api.ipify.org"')
    time.sleep(5)
    if check_ip()==None:
        rotate_ip_NOTMAIN()



def check_ip():
    for i in range(2):
        adb_cmd("input swipe 400 300 400 900 500")
        output = adb_cmd("uiautomator dump /dev/tty")
        match = re.search(r'WebView[^>]*>.*?text="(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"', output, re.DOTALL)
        if match:
            ip = match.group(1)
            print(f"IP найден: {ip}")
            return ip
            
        else:

            print("IP не найден")
            time.sleep(5)
    return None

