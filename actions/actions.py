# создание своего вишлиста, просмотр чужого и выбор подарка, рекомендации подарков
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import sqlite3
from rasa_sdk import Action, Tracker
from add_db import write, morph, parse_str, change_str, parse_gif, change_gif, change_str2

# 903347596 - my id
# rasa run -m models -p 5005 --connector telegram --credentials credentials.yml --debug
write()


class ActionCreateList(Action):
    def name(self):
        return "action_create_list"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        user_id = tracker.sender_id

        gif = next(tracker.get_latest_entity_values("gift"), None)
        gif = str(gif)
        gif = morph.parse(gif)[0].normal_form
        pr = next(tracker.get_latest_entity_values("price"), None)
        pr = int(pr)
        mes = tracker.latest_message.get("text")
        un = parse_str(mes)
        un = str(un)

        file = open('gift.txt', 'r')  # 'r' stands for read mode
        count_id = file.read()
        file.close()

        count_id=int(count_id)
        if gif and pr and un != '[]':
            with sqlite3.connect('gifts.db') as conn:
                curs = conn.cursor()

                curs.execute("INSERT INTO Wishlists (count_id, id, user_name, gift_name , price, taken) VALUES "
                         "(?,?,?,?,?,?)", (count_id,user_id, un, gif, pr, "свободен"))
                dispatcher.utter_message("Создан")
                count_id += 1
        else:
            dispatcher.utter_message("Введите корректное сообщение")
        file = open('gift.txt', 'w')  # 'w' stands for write mode
        content = str(count_id)
        file.write(content)
        file.close()
        return []


class ActionShowList(Action):
    def name(self):
        return "action_show_list"

    def run(self, dispatcher, tracker, domain):
        user_id = tracker.sender_id
        mes = tracker.latest_message.get("text")
        un = parse_str(mes)
        un = str(un)
        if un != '[]':
            with sqlite3.connect('gifts.db') as conn:
                curs = conn.cursor()
                curs.execute(
                    "SELECT gift_name,price,taken FROM Wishlists WHERE user_name = ? ORDER BY gift_name",
                    (un,)
                )
                (history) = curs.fetchall()
                if history:
                    for el in history:
                        ans = ', '.join(map(str, el))
                        dispatcher.utter_message(str(ans))
                else:
                    dispatcher.utter_message("Вишлиста не существует")
        else:
            dispatcher.utter_message("Введите корректное сообщение")
        return []


class ActionChoose(Action):

    def name(self):
        return "action_choose"

    def run(self, dispatcher, tracker, domain):
        user_id = tracker.sender_id
        gif = tracker.get_latest_entity_values("gift")
        gif = str(next(gif))
        gif = morph.parse(gif)[0].normal_form
        mes = tracker.latest_message.get("text")
        un = parse_str(mes)
        un = str(un)
        if gif and un != '[]':
            with sqlite3.connect('gifts.db') as conn:
                curs = conn.cursor()
                curs.execute("SELECT taken FROM Wishlists WHERE user_name=? and gift_name=?", (un, gif))
                res = curs.fetchall()
                if res:
                    curs.execute("UPDATE Wishlists SET taken= 'занято' WHERE user_name=? and gift_name=?", (un, gif))

                    curs.execute("INSERT INTO User (user_id, user2_name, gift_name) VALUES "
                             "(?,?,?)", (user_id, un, gif))
                    dispatcher.utter_message("Подарок записан")
                else:
                    dispatcher.utter_message("Такого подарка не существует")
        else:
            dispatcher.utter_message("Введите корректное сообщение")
        return []


class ActionRec(Action):

    def name(self):
        return "action_rec"

    def run(self, dispatcher, tracker, domain):
        user_id = tracker.sender_id
        pr = next(tracker.get_latest_entity_values("price"), None)
        pr = int(pr)

        mes = tracker.latest_message.get("text")
        un = parse_str(mes)
        un = str(un)
        if pr and un != '[]':
            with sqlite3.connect('gifts.db') as conn:
                curs = conn.cursor()
                curs.execute("SELECT gift_name, price FROM Wishlists WHERE price<=? AND user_name=? AND taken='свободен'"
                         , (pr, un))
                ans = curs.fetchall()

                if ans:
                    for el in ans:
                        res = ', '.join(map(str, el))
                        dispatcher.utter_message(str(res))
                else:
                    dispatcher.utter_message("Не удалось подобрать, измените параметры")
        else:
            dispatcher.utter_message("Введите корректное сообщение")
        return []


class ActionChange(Action):

    def name(self):
        return "action_change"

    def run(self, dispatcher, tracker, domain):
        user_id = tracker.sender_id
        gif = next(tracker.get_latest_entity_values("gift"), None)
        gif = str(gif)
        gif = morph.parse(gif)[0].normal_form

        pr = next(tracker.get_latest_entity_values("price"), None)
        pr = int(pr)

        mes = tracker.latest_message.get("text")
        un = parse_str(mes)
        un = str(un)

        gif2 = parse_gif(str(mes))
        gif2 = str(gif2)
        gif2 = change_gif(gif2)
        gif2 = morph.parse(gif2)[0].normal_form

        if gif and pr and un != '[]' and gif2:
            with sqlite3.connect('gifts.db') as conn:
                curs = conn.cursor()
                curs.execute("SELECT id FROM Wishlists WHERE user_name = ? and gift_name=?", (un,gif))
                rec = curs.fetchall()

                rec = change_str2(str(rec))
                dispatcher.utter_message(str(rec))
                if str(rec) == str(user_id):
                    curs.execute("SELECT taken FROM Wishlists WHERE user_name = ? and gift_name=?", (un, gif))
                    ans = curs.fetchall()
                    ans = change_str2(str(ans))

                    if ans == "занято":
                        curs.execute("UPDATE User SET gift_name='изменен' WHERE user2_name = ? and gift_name=?", (un, gif2))
                    curs.execute("UPDATE Wishlists SET gift_name= ?, price=?, taken='свободен' WHERE id=? and gift_name=?",
                             (gif2, pr, user_id, gif))
                    dispatcher.utter_message("Подарок изменен")
                else:
                    dispatcher.utter_message("Вы не можете редактировать чужой подарок или данного подарка не существует")
        else:
            dispatcher.utter_message("Введите корректное сообщение")
        return []


class ActionDel(Action):

    def name(self):
        return "action_del"

    def run(self, dispatcher, tracker, domain):
        user_id = tracker.sender_id
        gif = tracker.get_latest_entity_values("gift")
        gif = str(next(gif))
        gif = morph.parse(gif)[0].normal_form
        mes = tracker.latest_message.get("text")
        un = parse_str(mes)
        un = str(un)
        if gif and un != '[]':
            with sqlite3.connect('gifts.db') as conn:
                curs = conn.cursor()
                curs.execute("SELECT id FROM Wishlists WHERE user_name = ? and gift_name=?", (un,gif))
                rec = curs.fetchall()
                rec = change_str(str(rec))

                if str(rec) == str(user_id):
                    curs.execute("SELECT taken FROM Wishlists WHERE user_name = ? and gift_name=?", (un, gif))
                    ans = curs.fetchall()

                    ans = change_str2(str(ans))

                    if ans == "занято":
                        curs.execute("UPDATE User SET gift_name='удалено' WHERE user2_name = ? and gift_name=?", (un, gif))
                    curs.execute(
                        "DELETE FROM Wishlists WHERE id=? and gift_name=?",
                        (user_id, gif))

                    dispatcher.utter_message("Подарок удален")
                else:
                    dispatcher.utter_message("Вы не можете удалить чужой подарок или данного подарка не существует")
        else:
            dispatcher.utter_message("Введите корректное сообщение")
        return []


class ActionRemind(Action):

    def name(self):
        return "action_remind"

    def run(self, dispatcher, tracker, domain):
        user_id = tracker.sender_id
        mes = tracker.latest_message.get("text")
        un = parse_str(mes)
        un = str(un)
        if un != '[]':
            with sqlite3.connect('gifts.db') as conn:
                curs = conn.cursor()
                curs.execute("SELECT gift_name FROM User WHERE user_id = ? and user2_name = ? ORDER BY gift_name",
                         (user_id, un))
                reco = curs.fetchall()
                if reco:
                    for el in reco:
                        res = ', '.join(map(str, el))
                        dispatcher.utter_message(str(res))
                else:
                    dispatcher.utter_message("Подарок еще не выбран")
        else:
            dispatcher.utter_message("Введите корректное сообщение")
        return []
