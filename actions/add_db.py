# добавление баз данных user - список поадрков, user - выбранный подарок
import os
import sqlite3
import pymorphy2
import re

morph = pymorphy2.MorphAnalyzer()


def parse_str(mes):
    pattern = r'@\w+'
    words = re.findall(pattern, mes)
    return words

def parse_gif(mes):
    pattern = r'на \w+'
    words = re.findall(pattern, mes)
    return words

def change_gif(mes):
    ans = ""
    for i in range(5, len(mes) - 2):
        ans = ans + mes[i]
    return ans

def change_str(mes):
    ans = ""
    for i in range(2, len(mes) - 3):
        ans = ans + mes[i]
    return ans

def change_str2(mes):
    ans = ""
    for i in range(3, len(mes) - 4):
        ans = ans + mes[i]
    return ans

def create_tables(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS Wishlists (count_id INT AUTO_INCREMENT,id INT, user_name VARCHAR(100),
    gift_name VARCHAR(100), price INT,  taken VARCHAR(100))''')
    cursor.execute("CREATE TABLE IF NOT EXISTS User (user_id integer, user2_name VARCHAR(100), gift_name VARCHAR("
                   "100))")



def write():
    relative = os.path.join(os.curdir, "gift.txt")
    absolute_path = os.path.abspath(relative)
    with open(absolute_path, "r", encoding='UTF-8') as elements, sqlite3.connect("gifts.db") as conn:
        cursor = conn.cursor()

        create_tables(cursor)
        conn.commit()

        print()


if __name__ == "__main__":
    write()
