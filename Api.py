
from Nothing_phone_ip import rotate_ip_NOTMAIN
from pathlib import Path
from datetime import datetime
import re
import json
from loguru import logger
import threading
import sys
logger.remove()
import requests
# Настраиваем красивый вывод в консоль (время, уровень и цветное сообщение)
logger.add(
    sys.stderr, 
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>", 
    colorize=True
)

# Настраиваем запись ошибок в файл (только уровень ERROR и выше)
logger.add(
    "server_errors.log", 
    level="ERROR", 
    rotation="10 MB", 
    compression="zip", # Архив лога при достижении 10 МБ
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {file}:{line} | {message}"
)



from Database_raspberypi.sql_resbery import create_tasks_table_sql_,add_task_sql_GUI,get_next_task_sql_client,finish_task_sql_client,get_tasks_table_sql_,create_task_stats_table_sql_,increase_task_counter_sql_,create_devices_table_sql_,save_device_sql_,get_devices_sql_,return_task_stats_table_sql_,clear_task_stats_table_sql_,clear_tasks_table_sql_


from fastapi import FastAPI, Body
app = FastAPI()
lock=threading.Lock()
BASE_DIR = Path("dumps")  # корневая папка, потом можно поменять на путь к расшаренной папке на Raspberry

tasks={}
stats = {}
devices={}
completed = {}


create_tasks_table_sql_()
create_task_stats_table_sql_()
create_devices_table_sql_()
#===========================================================FUNCTIONS_GUI=================================================================0



@app.post("/save_account")
#TODO
def passs():
    pass
#save json to rasbpey


last_logs_hash = {}  # model -> hash последнего принятого блока, чтобы не писать повторно один и тот же кусок
import hashlib
#* сначала бд должна создатсья-тоесть телефон должен отправить логи и только потом нижняя функция заработает
#?client
@app.post("/logs_client")
def logs_from_client(data: dict):
    path = Path("phone_logs.log")
    model = data["model"]
    logs = data["logs"]

    # клиент шлёт последние 70 строк каждые 30 сек — если ничего не изменилось, пропускаем запись
    h = hashlib.md5(logs.encode("utf-8")).hexdigest()
    if last_logs_hash.get(model) == h:
        return
    last_logs_hash[model] = h

    if not logs.endswith("\n"):
        logs += "\n"

    with lock:
        with open(path, "a", encoding="utf-8") as file:
            file.write(logs)
        # ротация: если файл слишком большой — оставляем только хвост
        if path.stat().st_size > 5 * 1024 * 1024:  # 5 MB
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
            path.write_text("".join(lines[-2000:]), encoding="utf-8")

#TODO gui
@app.post("/send_phone_logs_GUI")
def send_logs_from_client_to_GUI():
    path = Path("phone_logs.log")
    if not path.exists():
        return {"logs": ""}
    with lock:
        content = path.read_text(encoding="utf-8")
    return {"logs": content}



#TODO GUI
@app.post("/tasks/add")
def add_task_GUI(data: dict):

    model = data.get("model")
    task = data.get("task")
    status = data.get("status")

    create_tasks_table_sql_()
    add_task_sql_GUI(model,task,status)
    logger.info({"status": "success", "message": "Task added to DB"})




#?client gui
@app.get("/health") #0
def health():
    logger.debug("server working")
    return "OK"



#пофиксить!.если телефон отключился то гуи все еще его почемуто показывает в таблице
#!client
@app.post("/phones") #1
def info( data: dict):
    model=data["model"]
    battery=data["battery"]
    screen=data["screen"]
    status=data["status"]
    current_task=data["task"]
    last_seen=data["last_seen"]
    
    create_devices_table_sql_()
    save_device_sql_(model,battery,screen,status,current_task,last_seen,)

    logger.debug(f"Request by: {model}")

    return {"ok": True}

#!gui
@app.get("/devices")
def get_devices():
    data=get_devices_sql_()
    return data

#!gui tasks STATISTIK!!!!
@app.get("/tasks_STATS_for_GUI")
def get_STATS_tasks_for_GUI():
    data=return_task_stats_table_sql_()
    return data


#!gui tasks QUEUES!!!!!!
@app.get("/tasks_QUEQS_for_GUI")
def get_QUQES_tasks_for_GUI():
    data=get_tasks_table_sql_()
    return data



#!gui clear stats
@app.get("/clear_stats")
def Clear_statTasks():
    clear_task_stats_table_sql_()
    return {"ok":True}


#!gui clear TASKS
@app.get("/clear_tasks")
def Clear_Tasks():
    clear_tasks_table_sql_()
    return {"ok":True}



#!client
#*чисто удаляем выполненую задачу при запрсое тела
@app.post("/tasks")  #3      ОТПРОЛЯЕМ НА СЕРВЕР СТРОГО ПОСЛЕ ВЫОЛНЕНИЯ КАКОЙТО ЗАДАЧИ НА ТЕЛЕ!  
def tasks_for_phones(data:dict):
    create_tasks_table_sql_()

    model=data["model"]
    id=data["id"]
    task=data["task"]
    finish_task_sql_client(id)

    increase_task_counter_sql_(model,task,)
    logger.debug(f"Task: {task} completed by: {model}")
    return {"ok": True}

#? server
def rotate_ip():
    if all(completed.values()):
        print("айпи сменился задание выполнено")
        # rotate_ip_NOTMAIN()
    else:
        pass






#!client
@app.post("/tasks/get")  #2
def send_tasks_for_phones(data:dict):
    model=data["model"]

    data2=get_next_task_sql_client(model)
    logger.debug(f"Sended task to: {model}")
    return data2

