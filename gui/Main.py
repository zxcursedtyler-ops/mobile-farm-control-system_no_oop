# ==========================================================
# FUNCTIONS
# ==========================================================
import requests
import time
import threading













successful_creations = 0
logs_box = None





from tkinter import *
import customtkinter as ctk

# customtkinter.set_appearance_mode("dark")
# customtkinter.set_default_color_theme("dark-blue")

root=ctk.CTk()
root.title("Phone farm HIKIKOMORI")
root.geometry("1200x720")


# ==========================================================
# TOP
# ==========================================================

top = ctk.CTkFrame(root, height=60)
top.pack(fill="x", padx=15, pady=10)

title = ctk.CTkLabel(
    top,
    text="PHONE FARM MANAGER",
    font=("Segoe UI", 26, "bold")
)
title.pack(side="left", padx=20, pady=10)

#todo
status_label = ctk.CTkLabel(
    master=top,
    text="Checking...",
    font=("Segoe UI", 16),
    text_color='orange'
)
status_label.pack(side="right", padx=20)


# ==========================================================
# ip adress
# ==========================================================


ip_var = ctk.StringVar(value="1.1.1.1")
ip_entry = ctk.CTkEntry(master=top, textvariable=ip_var, width=100)
ip_entry.pack(side='right',padx=10, pady=10)


# ==========================================================
# LEFT
# ==========================================================


left = ctk.CTkFrame(master=root, width=350)
left.pack(side='left', fill='y', padx=15, pady=15)
left.pack_propagate(False)  # Фиксируем ширину 350px

# Главный заголовок панели
left_lable = ctk.CTkLabel(master=left, font=("Segoe UI", 24, "bold"), text="Добавить задачу")
left_lable.pack(padx=15, pady=(20, 20))




# --- 1. Выбор телефона ---
phone_label = ctk.CTkLabel(master=left, font=("Segoe UI", 14), text="Телефон", anchor="w")
phone_label.pack(fill="x", padx=30, pady=(10, 2))

phone_var = ctk.StringVar(value="")
phone_menu = ctk.CTkOptionMenu(
    master=left, 
    variable=phone_var,
    values=[""],
    fg_color="#1B1C1C",          # Темный цвет как на скрине
    button_color="#B9751C",
    button_hover_color="#765119"
)
phone_menu.pack(fill="x", padx=30, pady=(0, 10))


# --- 2. тип задачи ---


task_mapping = {
"Outlook": "ou",
"Facebook": "fb",
"Gmail": "gm",
"Instagram": "ins",
"Facebook Page": "fp"}


ctk.CTkLabel(left, text="Тип задачи").pack(anchor="w", padx=25,pady=(30, 0))

task_var = ctk.StringVar(value="")
tasks = ctk.CTkOptionMenu(
    master=left, 
    variable=task_var,
    fg_color="#1B1C1C",          # Темный цвет как на скрине
    button_color="#B9751C",
    button_hover_color="#765119",
    values=list(task_mapping.keys())
)
tasks.pack(fill="x", padx=30, pady=(0, 10))



# # --- 3. button ---
# task_button=ctk.CTkButton(
#     left,
#     text="Добавить",
#     width=250,
#     height=45,command=add_Task
# ).pack(pady=30)

# ==========================================================
# RIGHT
# ==========================================================
right=ctk.CTkFrame(master=root,height=1200)
right.pack(fill='both',padx=5, pady=5,expand=False)
right.propagate(False)

# ----------------------------------------------------------
# 1. Фрейм Phones
# ----------------------------------------------------------
right1 = ctk.CTkFrame(master=right)
right1.pack(fill="both", expand=True)

right1_label = ctk.CTkLabel(master=right1, text='Phones', font=("Segoe UI", 19, "bold"))
right1_label.pack(padx=5, pady=2)#!можно изменить

# Текстовое поле для телефонов
phones_box = ctk.CTkTextbox(master=right1)
phones_box.pack(fill="both", padx=10, pady=(0, 10), expand=True)

# ----------------------------------------------------------
# 2. Фрейм Tasks  статистика
# ----------------------------------------------------------
right2 = ctk.CTkFrame(master=right)
right2.pack(fill="both", padx=5, pady=10, expand=True)

header_frame2 = ctk.CTkFrame(master=right2, fg_color="transparent") # прозрачный, чтобы не выделялся
header_frame2.pack(fill="x", padx=2, pady=2)

right2_label = ctk.CTkLabel(master=header_frame2, text='Statistic Stats', font=("Segoe UI", 19, "bold"))
right2_label.pack(padx=5, pady=2,side='left')



# Текстовое поле для задач
tasks_box = ctk.CTkTextbox(master=right2)
tasks_box.pack(fill="both", padx=10, pady=(0, 10), expand=True)




# ----------------------------------------------------------
# 3. Фрейм Queue задачи
# ----------------------------------------------------------
right3 = ctk.CTkFrame(master=right)
right3.pack(fill="both",  expand=True)

header_frame3 = ctk.CTkFrame(master=right3, fg_color="transparent") # прозрачный, чтобы не выделялся
header_frame3.pack(fill="x", padx=2, pady=2)

right3_label = ctk.CTkLabel(master=header_frame3, text='Queue Tasks', font=("Segoe UI", 19, "bold"))
right3_label.pack(side='left',padx=5, pady=2)



# Текстовое поле для логов
Queue_box = ctk.CTkTextbox(master=right3)
Queue_box.pack(fill="both", padx=10, pady=(0, 10), expand=True)









# ----------------------------------------------------------
# funtcions
# ----------------------------------------------------------
def update_textbox_phones(textbox, data):
    # 1. Разрешаем редактирование
    textbox.configure(state="normal",)
    
    # 2. Очищаем старый текст в ноль
    textbox.delete("1.0", "end")
    
    text_to_insert = ""
    
    # 3. Проверяем, если прилетел список кортежей/списков из БД
    if isinstance(data, list):
        for device in data:
            # Из SQLite приходит: (id, model, battery, screen, status, current_task, last_seen)
            # Распаковываем нужные элементы (пропускаем id, индекс 0)
            _, model, battery, screen, status, current_task, last_seen = device
            
            # Подбираем красивый эмодзи под статус девайса
            if status == "done":
                status_emoji = "🟢 done"
            elif status == "working" or status == "waiting":
                status_emoji = "🟡 working"
            else:
                status_emoji = "🔴 offline"
                
            # Форматируем в аккуратную строчку (табуляциями или пробелами)
            text_to_insert += f"{model:<15}    {status_emoji:<12}           {battery}%🔋           Экран: {screen}           Задачa: {current_task}           Время: {last_seen}\n"
    else:
        # Если пришла обычная строка — пишем как есть
        text_to_insert = str(data)

    # 4. Вставляем СТРОКУ, а не объект списка
    textbox.insert("end", text_to_insert)
    
    # 5. Замораживаем обратно, чтобы юзер не редактировал логи руками
    textbox.configure(state="disabled")


def update_textbox_stats(textbox, data):
    """
    Обновляет текстовое поле статистикой выполненных задач из таблицы task_stats
    """
    # 1. Разрешаем редактирование поля
    textbox.configure(state="normal")
    
    # 2. Очищаем старое содержимое
    textbox.delete("1.0", "end")
    
    # Красивая шапка для таблицы, чтобы ГУИ выглядел аккуратно
    text_to_insert = f"{'Устройство':<50} | {'Задача':<50} | {'Выполнено':<50}\n"
    text_to_insert += "-" * 48 + "\n"
    
    # 3. Парсим прилетевший JSON/список из БД
    if isinstance(data, list) and data:
        for row in data:
            # Структура из SQL: (id, model, task_completed, completed_count)
            # Игнорируем id (индекс 0) через заглушку '_'
            _, model, task_completed, completed_count = row
            
            # Сопоставляем короткие имена задач с красивыми тегами
            task_mapping = {
                "fb": "Facebook",
                "gm": "Gmail",
                "fp": "Facebook Page",
                "ou": "Outlook",
                "ins": "Instagram"
            }
            friendly_task = task_mapping.get(task_completed, task_completed.upper())
            
            # Собираем строчку с выравниванием по левому краю (<)
            text_to_insert += f"{model:<50} | {friendly_task:<50} | {completed_count:<50} шт. ✅\n"
    elif not data:
        text_to_insert += "\n   Статистика пока пуста. Задачи не выполнялись."
    else:
        # Если прилетела ошибка или обычная строка
        text_to_insert = str(data)

    # 4. Вставляем сгенерированный текст в виджет
    textbox.insert("end", text_to_insert)
    
    # 5. Снова блокируем поле от ручного изменения пользователем
    textbox.configure(state="disabled")


def update_textbox_stats_queqs(textbox, data):
    textbox.configure(state="normal")
    textbox.delete("1.0", "end")
    # Красивая шапка для таблицы, чтобы ГУИ выглядел аккуратно
    text_to_insert = f"{'Устройство':<50} | {'Задача':<50} | {'Статус':<50}\n"
    text_to_insert += "-" * 48 + "\n"
    

    if isinstance(data, list) and data:
        for row in data:
            _, model, task_name, status = row
            
            # Сопоставляем короткие имена задач с красивыми тегами
            task_mapping = {
                "fb": "Facebook",
                "gm": "Gmail",
                "fp": "Facebook Page",
                "ou": "Outlook",
                "ins": "Instagram"
            }
            friendly_task = task_mapping.get(task_name, task_name.upper())
            
            # Собираем строчку с выравниванием по левому краю (<)
            text_to_insert += f"{model:<50} | {friendly_task:<50} | {status:<50}  ✅\n"
    elif not data:
        text_to_insert += "\n   Статистика пока пуста. Задачи не выполнялись."
    else:
        # Если прилетела ошибка или обычная строка
        text_to_insert = str(data)

    # 4. Вставляем сгенерированный текст в виджет
    textbox.insert("end", text_to_insert)
    
    # 5. Снова блокируем поле от ручного изменения пользователем
    textbox.configure(state="disabled")


def chech_Tasks_Queue():
    while True:
        try:
            current_ip = ip_var.get()
            res=requests.get(f"http://{current_ip}:8000/tasks_QUEQS_for_GUI",timeout=10)
            if res.status_code==200:
                update_textbox_stats_queqs(Queue_box, res.json())


        except Exception as e:
            print(f"ERRORRRR {e}")
        time.sleep(10)


def check_Server_Health():
    while True:
        try:
            current_ip = ip_var.get()
            res=requests.get(f"http://{current_ip}:8000/health",timeout=10).json()
            if  res=="OK":
                status_label.configure(text="🟢 SERVER ONLINE", text_color="green")
            else:
                status_label.configure(text="🔴 SERVER OFFLINE", text_color="red")
        except Exception as e:
            status_label.configure(text="🔴 SERVER OFFLINE 404", text_color="red")
        time.sleep(20)

def chech_Phones():
    while True:
        try:
            current_ip = ip_var.get()
            res=requests.get(f"http://{current_ip}:8000/devices",timeout=10)
            if res.status_code==200:
                update_textbox_phones(phones_box, res.json())
                

                new_devices = []
                for row in res.json():
                    new_devices.append(row[1]) 
                
                if new_devices:
                    ALL_DEVICES = new_devices  # Записали в глобалку
                    
                    # 3. Передаем этот список в выпадающее меню
                    phone_menu.configure(values=ALL_DEVICES)
                    
                    # Если выбранный телефон внезапно пропал из сети, ставим первый доступный
                    if phone_var.get() not in ALL_DEVICES:
                        phone_var.set(ALL_DEVICES[0])
        except Exception as e:
            print(f"ERRORRRR {e}")
        time.sleep(240)

def chech_Tasks_Stats():
    while True:
        try:
            current_ip = ip_var.get()
            res=requests.get(f"http://{current_ip}:8000/tasks_STATS_for_GUI",timeout=10)
            if res.status_code==200:
                update_textbox_stats(tasks_box, res.json())
            else:
                print("check task stats error")

        except Exception as e:
            print(f"ERRORRRR {e}")
        time.sleep(10)


def add_Task():
    global successful_creations
    try:
        selected = task_var.get()
        short_name = task_mapping[selected]
        selected_phone = phone_var.get()          # Например: "Redmi 7"
        current_ip = ip_var.get()




        url=f"http://{current_ip}:8000/tasks/add"





        # Формируем JSON тело запроса
        payload = {
            "model": selected_phone,
            "task": short_name,
            "status": "waiting"  # Новая задача всегда создается со статусом waiting
        }
        
        try:
            # Шлем POST запрос с аргументом json=
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                successful_creations += 1
            else:
                print(f"Ошибка сервера: {response.status_code} | {response.text}")
                return # Если сервер выдал ошибку, прерываем цикл
        except Exception as e:
            print(f"Не удалось связаться с сервером: {e}")
            return

    except Exception as e:
        print(f"ERRORRRR {e}")

def add_task_async():
    threading.Thread(target=add_Task, daemon=True).start()

def get_logs_and_insert(textbox, data):
    textbox.configure(state="normal")
    textbox.delete("1.0", "end")

    textbox.insert("end", data)
    
    # 5. Снова блокируем поле от ручного изменения пользователем
    textbox.configure(state="disabled")


#* ----------------------------------------------------------

# --- 1. button to add task ---
task_button=ctk.CTkButton(
    left,
    text="Добавить",
    width=250,
    height=45,command=add_task_async,
    fg_color="#B9751C",
).pack(pady=30)



def update_logs(textbox):
    if not textbox.winfo_exists():
        return
    try:
        current_ip = ip_var.get()
        res = requests.post(f"http://{current_ip}:8000/send_phone_logs_GUI",timeout=5)
        textbox.delete("1.0", "end")
        textbox.insert("1.0", res.json()["logs"])
    except Exception as e:
        print(e)

    textbox.after(10000, lambda: update_logs(textbox))

def open_logs_window():
    new_window = ctk.CTkToplevel(root)
    new_window.title("Logs")
    new_window.geometry("900x600")

    log_frame = ctk.CTkFrame(master=new_window)
    log_frame.pack(expand=True,fill='both' )

    log_frame_label = ctk.CTkLabel(master=log_frame, text='Logs', font=("Segoe UI", 19, "bold"))
    log_frame_label.pack(padx=15, pady=15)

    
    log_frame_box = ctk.CTkTextbox(master=log_frame)
    log_frame_box.pack(fill="both", padx=10, pady=(0, 10), expand=True)

    update_logs(log_frame_box)



# --- 2. button for logs ---
btn = ctk.CTkButton(master=left, text="Открыть логи", command=open_logs_window,fg_color="#B9751C").pack(pady=30)

# *----------------------------------------------------------
def clear_task_stats():
    try:
        current_ip = ip_var.get()
        res=requests.get(f"http://{current_ip}:8000/clear_stats",timeout=5)
        if res.status_code==200:
            return
    except Exception as e:
        print(e)

def clear_task_():
    try:
        current_ip = ip_var.get()
        res=requests.get(f"http://{current_ip}:8000/clear_tasks",timeout=5)
        if res.status_code==200:
            return
    except Exception as e:
        print(e)


# --- 3. button for erase stats ---
right2_reset_button_stats=ctk.CTkButton(master=header_frame2,text="Сбросить статистику",font=("Segoe UI", 19, "bold"),fg_color="#B9751C",command=clear_task_stats).pack(side='right',padx=5, pady=2,)

# --- 4. button for erase tasks ---
right3_reset_button_tasks=ctk.CTkButton(master=header_frame3,text="Сбросить задачи",font=("Segoe UI", 19, "bold"),fg_color="#B9751C",command=clear_task_).pack(side='right',padx=5, pady=2,)


# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------

threading.Thread(target=check_Server_Health, daemon=True).start()
threading.Thread(target=chech_Phones, daemon=True).start()
threading.Thread(target=chech_Tasks_Stats, daemon=True).start()
threading.Thread(target=chech_Tasks_Queue, daemon=True).start()
root.mainloop()