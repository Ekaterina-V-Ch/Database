import sqlite3
from sqlite3 import Error

db_file = r'Database\purchasereq.db'


def create_connection():
    '''
    Create a database connection to a SQLite database
    :param db_file: db_file name
    :return: Connection object or None
    '''
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


conn = create_connection()
cur = conn.cursor()


def select_items(tab_name, info='*', k1=None, v1=None, k2=None, v2=None):
    '''
    Получение элементов из таблицы базы данных
    :return: запрашиваемый элемент
    '''
    i_list = []
    if v2:
        cur.execute(f'''SELECT {info} FROM {tab_name} WHERE {k1} = "{v1}" and {k2} = "{v2}"''')
    elif v1:
        cur.execute(f'''SELECT {info} FROM {tab_name} WHERE {k1} = "{v1}"''')
    else:
        cur.execute('''SELECT {0} FROM {1}'''.format(info, tab_name))
    reader = cur.fetchall()
    for row in reader:
        if len(row) > 1:
            i_list.append(row)
        else:
            i_list.append(row[0])
    return i_list


def check(tab_name_check, info):
    '''
    Проверяет, есть ли указанные элементы в ключевой таблице,
    если его нет - создается.
    :param tab_name_check: имя проверяемой таблицы
    '''
    # x = info[1]
    print(info)
    cur.execute("SELECT rowid FROM Equipment WHERE Name = ?", (info,))
    data = cur.fetchone()
    if data is None:
        insert_info(tab_name_check, (info,))


def insert_info(tab_name, info):
    '''
    Добавляет в таблицу новые значения или заменяет.
    :return: устанавливается идентификатор последней измененной строки
    '''
    if tab_name == 'Procurement':
        cur.execute(f''' INSERT OR REPLACE INTO Procurement VALUES(NULL, "{info[0]}", "{info[1]}", "{info[2]}", {info[3]}, {info[4]})''')
    elif len(info) > 1:
        cur.execute(f''' INSERT OR REPLACE INTO {tab_name} VALUES{info}''')
    else:
        cur.execute(f''' INSERT OR REPLACE INTO {tab_name} VALUES("{info[0]}")''')
    conn.commit()
    return cur.lastrowid


def update_info(tab_name, k1, v1, k2, v2):
    '''
    Изменяет в таблице значение
    '''
    cur.execute(''' UPDATE {0} SET {1} = {2} WHERE {3} = {4} '''.format(tab_name, k1, v1, k2, v2))
    conn.commit()
    print('Значение было изменено')


def make_tab(Equipment=None, Name_dep=None):
    '''Создает таблицу, в которой заявки от структурных подразделений
    пересекаются с программой развития'''
    cur.execute("DROP VIEW IF EXISTS during_for_Dep;")
    query = '''CREATE VIEW during_for_Dep(Equipment, Point, Name_dep, Requested, Satisfied, amt, Budget)
                AS 
                SELECT
                    Equipment.Name,
                    (SELECT Point FROM Development_program WHERE Extra!='для учебных аудиторий' and Equipment=Equipment.Name),
                    Procurement.Name_dep,
                    Procurement.Requested,
                    Procurement.Satisfied,
                    (SELECT amt FROM Development_program WHERE Extra<>'для учебных аудиторий' and Equipment=Equipment.Name),
                    (SELECT Budget FROM Development_program WHERE Extra<>'для учебных аудиторий' and Equipment=Equipment.Name)
                FROM
                    Equipment
                INNER JOIN Development_program ON Development_program.Equipment = Equipment.Name
                INNER JOIN Procurement ON Procurement.Equipment = Equipment.Name'''
    cur.execute(query)
    if Equipment is None and Name_dep is None:
        query = '''SELECT * FROM during_for_Dep'''
    elif Equipment is not None and Name_dep is not None:
        query = f'''SELECT * FROM during_for_Dep WHERE Equipment="{Equipment}" and Name_dep="{Name_dep}"'''
    elif Equipment is not None:
        query = f'''SELECT * FROM during_for_Dep WHERE Equipment="{Equipment}"'''
    elif Name_dep is not None:
        query = f'''SELECT * FROM during_for_Dep WHERE Name_dep="{Name_dep}"'''
    result = cur.execute(query)
    return result


def del_info(tab_name, k1, v1, k2=None, v2=None):
    if k2:
        sql = f'''DELETE FROM {tab_name} WHERE {k1} = "{v1}" and {k2} = "{v2}"'''
    else:
        sql = f'''DELETE FROM {tab_name} WHERE {k1} = "{v1}"'''
    cur.execute(sql)
    conn.commit()


def check_key():
    key = main_sql('Equipment', 'получить')
    tab1 = main_sql('Procurement', 'получить', 'Equipment')
    tab2 = main_sql('Development_program', 'получить', 'Equipment')
    for i in key:
        if i not in tab1 and i not in tab2:
            main_sql('Equipment', 'удалить', 'Name', i)


def main_sql(tab_name, comand, *args, **kwargs):
    '''
    Распределяющая функция, проверяющая имя файла. Создает связь и курсор.
    Передает значения классу для совершения дальнейших операций с базой данных.
    :param tab_name: название вызываемой таблицы
    :param args or kwargs: значения или команды, передаваемые таблицы
    '''
    with conn:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        r = [i[0] for i in cur.fetchall()]
        if tab_name not in r and tab_name != 'Таблица':
            print('Указанной таблицы нет в базе данных.\nТаблицы:\n', ' | '.join(r))
            return
        if kwargs:
            if comand == 'Таблица':
                if len(kwargs) == 2:
                    return make_tab(kwargs['Equipment'], kwargs['Name_dep'])
                elif len(kwargs) == 1 and 'Equipment' in kwargs.keys():
                    return make_tab(kwargs['Equipment'])
                elif len(kwargs) == 1 and 'Name_dep' in kwargs.keys():
                    return make_tab(None, kwargs['Name_dep'])
            elif comand == 'изменить':
                assert None not in kwargs
                i = []
                for k, v in kwargs.items():
                    i.append(k)
                    i.append(v)
                update_info(tab_name, i[0], i[1], i[2], i[3])
            elif comand == 'получить':
                k_v_list = [i for i in kwargs.items()]
                if len(k_v_list) == 2:
                    return select_items(tab_name, '*', k_v_list[0][0], k_v_list[0][1], k_v_list[1][0], k_v_list[1][1])
                elif len(k_v_list) == 1:
                    return select_items(tab_name, '*', k_v_list[0][0], k_v_list[0][1])
        elif args:
            if comand == 'получить':
                return select_items(tab_name, args[0])
            elif comand == 'добавить':
                if tab_name in ['Procurement', 'Development_program']:
                    check('Equipment', args[agree_dict[1]])
                insert_info(tab_name, args)
            elif comand == 'удалить':
                if len(args) == 2:
                    del_info(tab_name, args[0], args[1])
                else:
                    del_info(tab_name, args[0], args[1], args[2], args[3])
        else:
            if comand == 'получить':
                return select_items(tab_name)
            elif comand == 'Таблица':
                return make_tab()
            elif comand == 'очистить таблицу':
                cur.execute("DELETE FROM " + tab_name)
            if comand == 'проверить ключ':
                check_key()


if __name__ == '__main__':
    main_sql('Equipment', 'получить')
    # main_sql('Procurement', 'добавить', 'Name1', 'Call1', 4, 8)
    # main_sql('Procurement', 'добавить', 'val_Dep', 'val_Call', '', 1, 1)
    # main_sql('Procurement', 'получить', 'Equipment')
    # main_sql('Equipment', 'удалить', 'Name', "")
    # main_sql('Таблица', 'проверить ключ')
    # main_sql('Таблица', 'Таблица', Equipment=None, Name_dep=None)
    # main_sql('Procurement', 'изменить', Satisfied=2, ID=21)
    # main_sql('Departments', 'получить')
    # main_sql('Procurement', 'получить', Name_Dep='Кафедра менеджмента', Equipment='мфу')
    # main_sql('Departments', 'получить', 'Name_Dep, Type_dep')
    pass
