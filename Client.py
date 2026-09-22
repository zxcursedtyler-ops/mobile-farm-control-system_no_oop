import sys
import requests
import subprocess
import re
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading
from threading import Lock
from loguru import logger
from pathlib import Path
import json




#===========================================================FOLDERS=================================================================




BASE = Path(__file__).resolve().parent
#===========================================================server_functions=================================================================

def collect_logs_for_period():

    log_file_path = "phone_errors.log"
    collected_logs = []
    
    path = Path(log_file_path)
    if not path.exists():
        logger.critical(f"Файл логов {log_file_path} не найден.")
        return "Log file empty or not found."

    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                collected_logs.append(line)
    except Exception as e:
        logger.error(f"Ошибка при чтении файла логов: {e}")
        return f"Error reading logs: {e}"
    
    return "".join(collected_logs[-20:]) if collected_logs else "No logs found for this period."

def send_logs_to_server():
    logger.success("send_logs thread started")
    while True:
        logger.info("collect logs")

        logs_data = collect_logs_for_period()

        if "No logs found" in logs_data:
            time.sleep(10)
            continue # Зачем гонять пустые запросы
        logger.info("sending logs")
        try:
            url=f"http://{IP}:8000/logs_client"
            payload = {
                "model": model,
                "logs": logs_data
            }
            response = requests.post(url, json=payload, timeout=15)
            if response.status_code==200:
                logger.info("sended logs")
        except Exception as e:
            logger.critical(e)
        time.sleep(30)





#===========================================================IP=================================================================

IP="1.1.1.1"

#===========================================================MAIN_LOCK_THREADs==========================================================
from threading import Event
server_alive = Event()
server_alive.set()









#===========================================================ADB iniciliziation=================================================================

    

def adb_cmd(cmd, timeout=10):
    try:
        result = subprocess.run(
            cmd, shell=True, text=True,
            capture_output=True, timeout=timeout
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.error(f"[shell] Таймаут: {cmd}")
        return ""
    except Exception as e:
        logger.error(f"[shell] Исключение '{cmd}': {e}")
        return ""

def get_battery():
    """Получает заряд и статус батареи через termux-api (dumpsys недоступен без root)."""
    raw = adb_cmd("termux-battery-status")
    try:
        data = json.loads(raw)
        percentage = data.get("percentage", "unknown")
        status = data.get("status", "unknown")  # DISCHARGING / CHARGING / FULL
        return percentage, status
    except json.JSONDecodeError:
        logger.error(f"[get_battery] Не удалось распарсить JSON от termux-battery-status: {raw!r}")
        return "unknown", "unknown"
 
 
def get_model():
    """getprop доступен в Termux без root — читает read-only системное свойство."""
    model = adb_cmd("getprop ro.product.model")
    return model if model else "unknown"
 
 
def phone_info():
    """
    Полностью переписано под Termux:
    - dumpsys / wm недоступны без root (SELinux блокирует доступ к system_server)
    - батарея берётся через termux-api (пакет termux-api + приложение Termux:API)
    - размер экрана недоступен без root, оставлен как заглушка
    """
    battery, charge_status = get_battery()
    model = get_model()
 
    screen = "unavailable"      # dumpsys/wm size недоступны без root
    status = charge_status      # используем статус зарядки вместо "экран вкл/выкл"
 
    timee = time.localtime()
    hour = timee[3]
    minuta = timee[4]
    last_seen = f"{hour}:{minuta}"
 
    return battery, screen, model, status, hour, minuta, last_seen

model = phone_info()[2]
IDS=[]
task_zaprosy=[]
status_of_task={}
tasks_spisok_for_threads = Queue()
task_lock = Lock()
ids_lock = Lock()



#!===========================================================LOGURU-LOGI=================================================================

logger.remove()

# Настраиваем красивый вывод в консоль (время, уровень и цветное сообщение)
logger.add(
    sys.stderr, 
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>", 
    colorize=True
)

# Настраиваем запись ошибок в файл (только уровень ERROR и выше)
logger.add(
    "phone_errors.log", 
    level="INFO", 
    rotation="10 MB", 
    compression="zip",
    retention="1 day", # Архив лога при достижении 10 МБ
    format=f"[{model}] "+"{time:YYYY-MM-DD HH:mm:ss} | {level} | {file}:{line} | {message}",
    colorize=True
)

#*===============================================Application Programming Interface========================================================2


#отправляем наши готовые данные после выполнении задачи серверу-который тот сохроняет в json
def send_account_to_server(account_data):
    while True:
        server_alive.wait() # Ждем, если сервер недоступен
        try:
            url = f"http://{IP}:8000/save_account"
            response = requests.post(url, json=account_data, timeout=12)
            if response.status_code == 200:
                logger.success("Данные аккаунта успешно переданы через Клиент!")
                return True
            if response.status_code != 200:
                logger.critical(response.json())
        except Exception as e:
            logger.error(f"Ошибка отправки аккаунта: {e}")
        time.sleep(10)





def health_check_loop():
    while True:
        try:
            response=requests.get(f"http://{IP}:8000/health", timeout=15)
            if response.status_code != 200:
                logger.critical(response.json())
            if not server_alive.is_set():                               
                logger.warning("Сервер вернулся — возобновляем")
            server_alive.set()
        except:
            if server_alive.is_set():
                logger.warning("Сервер недоступен — замораживаем")
            server_alive.clear()
        time.sleep(30)






#/tasks не вызывается напрямую!   3 отчет после выполнения функции
@logger.catch
def task_done():
    
    if not task_zaprosy:
        logger.warning("<yellow>[task_done] Список задач пуст. Нечего завершать.</yellow>")
        return  

    with task_lock:
        task = task_zaprosy[0]
    if not IDS:
        logger.error(f"<red>Ошибка в task_done:IDS</red>")
        return
    with ids_lock:
        IDD=IDS[0]
    while True:
        server_alive.wait() 
        try:
                                                            #ОТПРОВЛЯТЬ СТРОГО ПОСЛЕ ВЫОЛНЕНИЯ КАКОЙТО ЗАДАЧИ!                             
            response=requests.post(f"http://{IP}:8000/tasks",
                json={
                    "model":model,
                    "id":IDD,
                    "task":task
                },timeout=15
            )
            if response.status_code == 200:
                logger.warning(f" [task_done] Статус задачи '{task}' успешно отправлен на сервер. ")
                with task_lock:
                    task_zaprosy.pop(0)
                with ids_lock:
                    IDS.pop(0)
                    break
            else:
                logger.critical(response.json())
                logger.error(f"Сервер вернул {response.status_code}, ретрай...")
                time.sleep(10)

        except Exception as e:
            logger.error(f"<red>Ошибка в task_done:</red> {e}")
            time.sleep(10)






#/tasks/get  вызывается напрямую! работает в потоке чтобы смлтреть новые задачи для телов по кд
def task_get_zaprosy():
    while True:
        try:
            server_alive.wait()
            if not status_of_task:
                status_of_task[model]="done"
            if not status_of_task[model]=="working":
                
                response_task=requests.post(f"http://{IP}:8000/tasks/get",
                    json={
                        "model":model,
                    },timeout=15
                )
                logger.warning("Запрос /tasks/get отправлен.")
                data=response_task.json()
                if response_task.status_code != 200:
                    logger.critical(response_task.json())

                    
                if data is None:
                    logger.info("data is none/ no tasks")
                    time.sleep(5)
                    continue

                ID=data[0]
                with ids_lock:
                    IDS.append(ID)
                task_from_server=data[1]
                if task_from_server in ("fb", "gm", "fp", "ou", "ins"):
                    tasks_spisok_for_threads.put(task_from_server)
                    with task_lock:
                        status_of_task[model] = "working"
                        task_zaprosy.append(task_from_server)
                    logger.success(f"Добавлена задача в очередь: {task_from_server}")
                else:
                    logger.critical(f"TASK NO FOUND")


            if status_of_task[model]=="working":
                    logger.info('status_of_task[model]=="working"')
                    time.sleep(5)
                    continue
        except Exception as e:
            logger.critical(f"<red>Ошибка в task_get_zaprosy:</red> {e}")
        time.sleep(10)#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1

#/phones/  вызывается напрямую!   1 по кд
def get_info():
    try:
        server_alive.wait()
        battery, screen, model, status, hour, minuta, last_seen = phone_info()
        with task_lock:

            current_task = status_of_task.get(model, "")
        response=requests.post(
            f"http://{IP}:8000/phones",
            json={
                "model":model,
                "battery":battery,
                "screen":screen,
                "status":status,
                "task":current_task,
                "last_seen":last_seen
            },timeout=15
        )
        if response.status_code == 200:
            logger.warning(" Данные /phones успешно отправлены. ")
        if response.status_code != 200:
            logger.critical(response.json())

    except Exception as e:
        logger.error(f"<red>Ошибка в get_info при отправке метрик:</red> {e}")
 




def get_info_loop():

    while True:

        get_info()

        time.sleep(300)


#===========================================================Functions=================================================================1

#TODO:сделать адб функции для телефонов

@logger.catch
def gm():

    logger.success("[GM] Start")
    logger.warning("gm")
    time.sleep(5)
    task_done()
    logger.success("[GM] Finished")
    status_of_task[model]="done"


@logger.catch
def fb():   

    logger.success("[FB] Start")
    logger.warning("fb")
    time.sleep(5)
    task_done()
    logger.success("[FB] Finished")
    status_of_task[model]="done"
















@logger.catch
def ou():

    logger.success("[OU] Start")
    logger.warning("ou")
    time.sleep(5)
    task_done()
    logger.success("[OU] Finished")
    status_of_task[model]="done"













@logger.catch
def fp():

    logger.success("[FP] Start")
    logger.warning("fp")
    time.sleep(5)
    task_done()
    logger.success("[FP] Finished")
    status_of_task[model]="done"


@logger.catch
def ins():

    logger.success("[INS] Start")
    logger.warning("ins")
    time.sleep(5)
    task_done()
    logger.success("[INS] Finished")
    status_of_task[model]="done"





#==========================================================


with ThreadPoolExecutor(max_workers=1) as worker:

    threading.Thread(target=send_logs_to_server, daemon=True).start()
    threading.Thread(target=health_check_loop, daemon=True).start()
    threading.Thread(target=get_info_loop, daemon=True).start()
    threading.Thread(target=task_get_zaprosy, daemon=True).start()
    logger.warning(" Фоновые потоки запущены. Ожидание задач из очереди... ")

    while True:
        logger.success("Ожидание задачи из очереди...")
        task_for_threads = tasks_spisok_for_threads.get()
        if task_for_threads == "fb":
            worker.submit(fb)
            logger.warning(" Задача FB отправлена... ")
        if task_for_threads == "fp":
            worker.submit(fp)
            logger.warning(" Задача FP отправлена... ")
        if task_for_threads == "gm":
            worker.submit(gm)
            logger.warning(" Задача GM отправлена... ")




        if task_for_threads == "ou":
            
            worker.submit(ou)
            logger.warning(" Задача ou отправлена... ")







        if task_for_threads == "ins":
            worker.submit(ins)
            logger.warning(" Задача INS отправлена... ")

        
        tasks_spisok_for_threads.task_done()
        logger.info("ЗАДАЧИ ВЫПОЛНЕНЫ ИДЕТ СБРОС")
        time.sleep(10)


