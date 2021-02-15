import sqlite3
import os
from card import Card

class CardRepository:
	def __init__(self, db_filename: str = "cards_db.db"):
		self.__db_filename = db_filename
		if not os.path.isfile(db_filename):
			self.__create_db()

	def get_all(self) -> list(Card):
		connection = self.__create_connection()
		cursor = connection.cursor()
		cursor.row_factory = self.__dict_factory
		sql = 'SELECT * FROM Cards'
		cursor.execute(sql)
		result = cursor.fetchall()
		connection.close()
		cards = [Card.from_dict(x) for x in result]
		return cards

	def get_by_tag(self, tag: str) -> list(Card):
		connection = self.__create_connection()
		cursor = connection.cursor()
		cursor.row_factory = self.__dict_factory
		sql = 'SELECT * FROM Cards WHERE Tag=:Tag'
		cursor.execute(sql, {"Tag": tag})
		result = cursor.fetchall()
		connection.close()
		cards = [Card.from_dict(x) for x in result]
		return cards

	def add(self, card: Card) -> int:
		connection = self.__create_connection()
		cursor = connection.cursor()
		sql = "insert into Cards (Tag, Author, Text, Country) values (:tag, :author, :text, :country)"
		card_dict = vars(card)
		cursor.execute(sql, card_dict)
		id = cursor.lastrowid
		connection.commit()
		connection.close()
		return id

	def __create_connection(self):
		connection = None
		try:
			connection = sqlite3.connect(self.__db_filename)
		except sqlite3.DatabaseError as e:
			# TODO: переделать на логгер
			print(e)
			return None
		# finally:
		# 	connection.close()

		return connection

	def __create_db(self):
		connection = self.__create_connection()
		cursor = connection.cursor()
		sql = '''CREATE TABLE "Cards" (
					"ID"	INTEGER NOT NULL UNIQUE,
					"Tag"	TEXT,
					"Text"	TEXT NOT NULL,
					"Author"	TEXT,
					"Country"	TEXT,
					PRIMARY KEY("ID" AUTOINCREMENT)
				);'''
		cursor.execute(sql)
		connection.commit()
		connection.close()

		# вставляем дефолтные карточки
		self.__insert_default_cards()

	def __insert_default_cards(self):
		default_cards = [
			{"tag": "Политика", "author": "Б. Андерсон", "text": "Быть нацией по сути самая универсальная легитимная ценность в политической жизни нашего времени", "country": "" },
			{"tag": "Политика", "author": "Кольбе", "text": "Мы должны завоевать народы нашей промышленностью и победить их нашим вкусом", "country": "Франция" },
			{"tag": "Экономика", "author": "М.  Фридман", "text": "Роль правительства в свободном обществе делать то, что рынок не может делать для себя сам, а именно определять, устанавливать и поддерживать правила игры", "country": "" },
			{"tag": "Экономика", "author": "Г. Форд", "text": "Не работодатель выдает зарплату, работодатель только распределяет деньги. Зарплату выдает клиент.", "country": "" },
			{"tag": "Культура", "author": "Н. Арутюнян", "text": "Все носят невидимые очки, стекла которых сварены из услышанных или прочитанных слов, идей и мнений. Никто не свободен от очков.", "country": "" }
		]
		for	card in default_cards:
			self.add(card)

	@staticmethod
	def __dict_factory(cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			name = col[0]
			lower_name = name.lower()
			d[lower_name] = row[idx]
		return d
