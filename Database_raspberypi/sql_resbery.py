import sqlite3
#!!!DB=sqlite3.connect("RASPBERY_PIE.db")#установили связь с дб


#*создали таблицу для задач для телефонов
def create_tasks_table_sql_():
    DB=sqlite3.connect("RASPBERY_PIE.db") 
    coursor=DB.cursor() 
    coursor.execute("""CREATE TABLE IF NOT EXISTS tasks_phones 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model TEXT,
                    task_name TEXT,
                    status TEXT)
                    """)
    DB.commit()
    DB.close()




#*сделали функцию которая добовляет задачу определеному телефону
#* status будет waiting

def add_task_sql_GUI(model,task,status):
    DB=sqlite3.connect("RASPBERY_PIE.db") 
    coursor=DB.cursor() 
    coursor.execute("""INSERT INTO tasks_phones (task_name,status,model)
VALUES(?,?,?)""",(task,status,model))
    DB.commit()
    DB.close()


#!1. Очистить очередь задач (tasks_phones) for gui
def clear_tasks_table_sql_():
    DB = sqlite3.connect("RASPBERY_PIE.db")
    cursor = DB.cursor()

    cursor.execute("DELETE FROM tasks_phones")

    DB.commit()
    DB.close()

#!Очистить статистику (task_stats) for gui
def clear_task_stats_table_sql_():
    DB = sqlite3.connect("RASPBERY_PIE.db")
    cursor = DB.cursor()

    cursor.execute("DELETE FROM task_stats")

    DB.commit()
    DB.close()












#* task/get клиент отправляет запрос на сервер и тот ему вытаскивает из бд задачу
def get_next_task_sql_client(model,):
    DB=sqlite3.connect("RASPBERY_PIE.db") 
    coursor=DB.cursor() 
    coursor.execute("""SELECT id, task_name FROM tasks_phones WHERE model=? AND status='waiting' ORDER BY id LIMIT 1""",(model,)) 
    data=coursor.fetchone()
    if data:
        task_id = data[0]
        task_name = data[1]
        coursor.execute("""UPDATE tasks_phones SET status='working' WHERE id=?""",(task_id,))
        DB.commit()
        DB.close()
        return task_id,task_name

    DB.close()
    return None


#*/tasks клиент сделал запросо о том что задача выполененa и статус true      DELETE
def finish_task_sql_client(id):
    DB=sqlite3.connect("RASPBERY_PIE.db") 
    coursor=DB.cursor() 
    coursor.execute("""DELETE FROM tasks_phones WHERE id=? """,(id,))
    DB.commit()
    DB.close()


#!смотрим таблицу задач 
def get_tasks_table_sql_():
    DB=sqlite3.connect("RASPBERY_PIE.db") 
    coursor=DB.cursor() 
    coursor.execute("""SELECT * FROM tasks_phones""")
    data=coursor.fetchall()
    DB.commit()
    DB.close()
    return data



















#!
#*создали таблицу для счетчика выполенынх задач
def create_task_stats_table_sql_():
    DB=sqlite3.connect("RASPBERY_PIE.db") 
    coursor=DB.cursor() 
    coursor.execute("""CREATE TABLE IF NOT EXISTS task_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model TEXT,
                    task_completed TEXT,
                    completed_count INTEGER,
                    UNIQUE(model, task_completed))""")
    DB.commit()
    DB.close()

#*return таблицу для выполенынх задач
def return_task_stats_table_sql_():
    DB=sqlite3.connect("RASPBERY_PIE.db") 
    coursor=DB.cursor() 
    coursor.execute("""SELECT * FROM task_stats""")
    data=coursor.fetchall()
    DB.commit()
    DB.close()
    return data



#*вызывеаем нашу функцию после finish_task_sql_client или после того как телефон сделал запрос о том что выполнил задачу.делаем {task} count+1 для выполненой задачи
def increase_task_counter_sql_(model,task,):
    DB=sqlite3.connect("RASPBERY_PIE.db") 
    coursor=DB.cursor() 

    coursor.execute("""SELECT id FROM task_stats WHERE model=? AND task_completed=?""",(model,task,))
    data=coursor.fetchone()

    if data==None:
        coursor.execute("""INSERT INTO task_stats (model,task_completed,completed_count) VALUES (?,?,?)""",(model,task,int(0),))         
        coursor.execute("""UPDATE task_stats
                            SET completed_count = completed_count + 1 WHERE model=? AND task_completed=?""",(model,task,))

    else:                                   
        coursor.execute("""UPDATE task_stats
                            SET completed_count = completed_count + 1 WHERE model=? AND task_completed=?""",(model,task,))
    DB.commit()
    DB.close()



























#*функция которая создает таблицу под все данные телефона
def create_devices_table_sql_():
    DB=sqlite3.connect("RASPBERY_PIE.db") 
    coursor=DB.cursor() 
    coursor.execute("""CREATE TABLE IF NOT EXISTS devices 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model TEXT UNIQUE,
                    battery INTEGER,
                    screen TEXT,
                    status TEXT,
                    current_task TEXT,
                    last_seen TEXT)""")
    DB.commit()
    DB.close()



#*функция которая проверяет есть ли модель телефона в таблице.если нет создаем данные для телефона и передаем их в таблицу и потом заполняем их после ответа клиента.
#*если модель телефона присутсвует то просто обновляем данные от клиента
def save_device_sql_(model,battery,screen,status,current_task,last_seen,):


    DB=sqlite3.connect("RASPBERY_PIE.db")#установили связь с дб
    coursor=DB.cursor()#сделали курсор какойто
    coursor.execute(f"""SELECT id FROM devices WHERE model=?""",(model,))
    data = coursor.fetchone()
    if data==None:
        coursor.execute("""INSERT INTO devices (model,
                                                battery,
                                                screen,
                                                status,
                                                current_task,
                                                last_seen)
                                                VALUES ( 
                                                ?,
                                                ?,
                                                ?,
                                                ?,
                                                ?,
                                                ?   )""",
(
    model,
    battery,
    screen,
    status,
    current_task,
    last_seen

))
    else:
        coursor.execute(f"""UPDATE devices SET battery=?,
                                                screen=?,
                                                status=?,
                                                current_task=?,
                                                last_seen=?
                                                WHERE model=?
""",
(
    battery,
    screen,
    status,
    current_task,
    last_seen,
    model
))
    DB.commit()
    DB.close()








def get_devices_sql_():
    DB=sqlite3.connect("RASPBERY_PIE.db") 
    coursor=DB.cursor()#сделали курсор какойто
    coursor.execute("""SELECT * FROM devices
""")
    data=coursor.fetchall()
    DB.commit()
    DB.close()
    return data

