import sqlite3
from datetime import datetime


class DatatabaseConnections:
    def __init__(self, host):
        self.connection = None
        self.host = host

    def __enter__(self):
        self.connection = sqlite3.connect(self.host)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb or exc_type or exc_val:
            self.connection.close()
        else:
            self.connection.commit()
            self.connection.close()


def create_table_attack_results():
    with DatatabaseConnections("razboi_db.db") as connection:
        cursor = connection.cursor()
        sql = "CREATE TABLE IF NOT EXISTS attack_results(" \
              "id_attack integer primary key," \
              "attacked_user text," \
              "weu_stolen integer," \
              "weu_in_total integer," \
              "enemy_attack_power integer," \
              "my_attack_power integer," \
              "time_attacked text)"
        cursor.execute(sql)


def add_attack_statistics_to_db(attacked_user, weu_stolen, weu_in_total, enemy_attack_power,
                                my_attack_power, time_attacked):
    with DatatabaseConnections("razboi_db.db") as connections:
        cursor = connections.cursor()
        sql = "INSERT INTO attack_results VALUES(null, ?, ?, ?, ?, ?, ?)"
        cursor.execute(
            sql, (attacked_user, weu_stolen,  weu_in_total, enemy_attack_power,
                  my_attack_power, time_attacked)
        )


def create_table_forbidden_user():
    with DatatabaseConnections("razboi_db.db") as connection:
        cursor = connection.cursor()
        sql = "CREATE TABLE IF NOT EXISTS forbidden_users(" \
              "forbidden_user_id integer primary key," \
              "forbidden_user text)"
        cursor.execute(sql)


def add_forbidden_user(user_f):
    with DatatabaseConnections('razboi_db.db') as connection:
        cursor = connection.cursor()
        sql = f"INSERT INTO forbidden_users VALUES(null, {user_f})"
        cursor.execute(sql)


def get_money_stolen_today():
    with DatatabaseConnections('razboi_db.db') as connection:
        date = datetime.now()
        date = str(date).split()
        today = str(date[0][:10])
        cursor = connection.cursor()
        sql = f"SELECT weu_stolen FROM attack_results WHERE time_attacked like '{today}%'"
        cursor.execute(sql)
        attacks = [row[0] for row in cursor.fetchall()]
    total = 0
    total_100000 = 0
    count = 0
    for attack in attacks:
        total += attack
        if attack > 100000:
            count += 1
            total_100000 += attack

    try:
        print(f' A total of {str(total)} from {str(len(attacks))} attacks have been made today. Media = '
              f'{str(int(total/len(attacks)))}')
        print(f' A total of {str(total_100000)} from {str(count)} attacks over 100000 have been made today. Media = '
              f'{str(int(total_100000/count))}')
        print(f' A total of {str(total-total_100000)} from {str(len(attacks)-count)} ware mass attacks. Media = '
          f'{str(int((total-total_100000)/(len(attacks)-count)))}')
    except ZeroDivisionError:
        print("No attacks made Today")


def get_money_stolen_all_time():
    print("Money made with BotRazboiSoFar:")
    with DatatabaseConnections('razboi_db.db') as connection:
        cursor = connection.cursor()
        sql = f"SELECT weu_stolen FROM attack_results"
        cursor.execute(sql)
        attacks = [row[0] for row in cursor.fetchall()]
    total_1000_alltime = 0
    count_total_time = 0
    total = 0
    for attack in attacks:
        total += attack
        if attack > 100000:
            count_total_time += 1
            total_1000_alltime += attack
    print(f' A total of {str(total)} from {str(len(attacks))} attacks have been made. Media = '
          f'{str(int(total/len(attacks)))}')
    print(f' A total of {str(total_1000_alltime)} from {str(count_total_time)} attacks over 100000 have been made. Media = '
          f'{str(int(total_1000_alltime/count_total_time))}')
    print(f' A total of {str(total-total_1000_alltime)} from {str(len(attacks)-count_total_time)} ware mass attacks. Media = '
          f'{str(int((total-total_1000_alltime)/(len(attacks)-count_total_time)))}')
# today = '[0-9]*\-[0-9]*\-[16]*'


# def remove_column():
#     with DatatabaseConnections('razboi_db.db') as connection:
#         cursor = connection.cursor()
#         sql = "CREATE TEMPORARY TABLE t1_backup(" \
#               "id_attack integer primary key," \
#               "attacked_user text," \
#               "weu_stolen integer," \
#               "weu_in_total integer," \
#               "enemy_attack_power integer," \
#               "my_attack_power integer," \
#               "time_attacked text)"
#         cursor.execute(sql)
#
#         sql = "INSERT INTO t1_backup SELECT id_attack, attacked_user, weu_stolen, weu_in_total,
#         enemy_attack_power,my_attack_power, time_attacked FROM attack_results"
#         cursor.execute(sql)
#
#         sql = "DROP TABLE attack_results"
#         cursor.execute(sql)
#
#         sql = "CREATE TABLE attack_results(" \
#               "id_attack integer primary key," \
#               "attacked_user text," \
#               "weu_stolen integer," \
#               "weu_in_total integer," \
#               "enemy_attack_power integer," \
#               "my_attack_power integer," \
#               "time_attacked text)"
#         cursor.execute(sql)
#
#         sql = "INSERT INTO attack_results  SELECT id_attack, attacked_user, weu_stolen, weu_in_total,
#         enemy_attack_power,my_attack_power, time_attacked FROM t1_backup"
#         cursor.execute(sql)
#
#         sql = "DROP TABLE t1_backup"
#         cursor.execute(sql)

"""
        time_attacked like '2020-06-09%'
"""

# get_money_stolen_today()
# get_money_stolen_all_time()

