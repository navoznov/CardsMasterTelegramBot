#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from uuid import uuid4
from telegram import InlineQueryResult, InlineQueryResultArticle, ParseMode, InputTextMessageContent, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    InlineQueryHandler
)
from telegram.utils.helpers import escape_markdown
from cardService import CardService
from card import Card
import re


class TelegramBot:

    def __init__(self, token: str, card_service: CardService):
        self.__token = token
        self.__card_service = card_service

    def go(self) -> None:
        # TODO: длинный метод
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        logger = logging.getLogger(__name__)

        # Create the Updater and pass it your bot's token.
        updater = Updater(self.__token)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        MAIN_MENU_STATE, SHOW_CARD_STATE, SELECT_TAG_STATE, ADD_CARD_TEXT_STATE, ADD_CARD_TAG_STATE, ADD_CARD_AUTHOR_STATE, ADD_CARD_COUNTRY_STATE, CARD_SAVED_STATE  = range(8)
        # текст кнопки "выбрать все колоды"
        ALL_TAGS_TAG = "! Все !"

        # TODO: избавиться от этих переменных (риски ошибок при нескольких сеансах)
        self.__last_selected_tag = None
        self.__card_text = None
        self.__card_tag = None
        self.__card_author = None
        self.__card_country = None
        self.__last_card = None

        def main_menu_state_handler(update: Update, context: CallbackContext) -> int:
            logger.info("Главное меню")
            text = 'Привет. Я карточных дел мастер. Выбери, что мы с тобой будем делать'
            reply_keyboard = [['Вытянуть карточку'], ['Добавить карточку'], ['Список всех карточек']]
            keyboard_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text(text, reply_markup=keyboard_markup)
            return MAIN_MENU_STATE

        def select_tag_state_handler(update: Update, context: CallbackContext) -> int:
            text = 'Выбери колоду или "Все", если хочешь смешать все колоды'
            logger.info("Выбрать колоду")
            tags = self.__card_service.get_all_tags()
            tags = [ALL_TAGS_TAG] + tags
            reply_keyboard = [[tag] for tag in tags]
            keyboard_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text(text, reply_markup=keyboard_markup, reply_to_message_id=update.message.message_id)
            return SELECT_TAG_STATE

        def show_card_state_handler(update: Update, context: CallbackContext) -> int:
            if self.__last_card != None:
                card = self.__last_card
                self.__last_selected_tag = card.tag
                logger.info('Просмотр последней добавленной карты')
            else:
                user_data = context.user_data
                selected_tag = self.__last_selected_tag if update.message.text == 'Вытащить еще одну карту' else update.message.text
                self.__last_selected_tag = selected_tag
                logger.info('Выбрана колода "%s"', selected_tag)
                tag = None if selected_tag == ALL_TAGS_TAG else selected_tag
                card = self.__card_service.get_random_card(tag)

            def get_markdownV2_card_message_text(card: Card):
                result = ''
                author_text = f'{card.author} ' if card.author else ''
                country_text = f'{card.country} ' if card.country else ''
                title_text = author_text + country_text
                result+= f'* {title_text} *\n\n' if title_text else ''
                # result+= card.text.replace('.', r'\.')
                result+= re.escape(card.text)
                return result

            def get_plaintext_card_message_text(card: Card):
                result = ''
                author_text = f'{card.author} ' if card.author else ''
                country_text = f'{card.country} ' if card.country else ''
                title_text = author_text + country_text
                result+= f'{title_text}\n\n' if title_text else ''
                result+= card.text
                return result

            reply_text = get_plaintext_card_message_text(card)
            reply_keyboard = [["Вытащить еще одну карту"], ["Выбрать колоду"], ["Вернуться в главное меню"]]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text(reply_text, reply_markup=markup, reply_to_message_id=update.message.message_id)
            # update.message.reply_text(reply_text, reply_markup=markup, parse_mode='MarkdownV2', reply_to_message_id=update.message.message_id)
            logger.info('Показана цитата "%s"', card.text)
            return SHOW_CARD_STATE

        def add_card_text_state_handler(update: Update, context: CallbackContext) -> int:
            text = 'Введите текст цитаты (можно несколько строк)'
            logger.info("Ввод цитаты")

            self.__last_card = None

            # update.message.reply_text(text, reply_markup=ReplyKeyboardRemove(), reply_to_message_id=update.message.message_id)
            update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
            return ADD_CARD_TEXT_STATE

        def add_card_tag_state_handler(update: Update, context: CallbackContext) -> int:
            self.__card_text = update.message.text

            text = 'Введите название колоды или выбирите из списка'
            logger.info("Ввод названия колоды")
            tags = self.__card_service.get_all_tags()
            reply_keyboard = [[tag] for tag in tags]
            keyboard_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text(text, reply_markup=keyboard_markup, reply_to_message_id=update.message.message_id)
            return ADD_CARD_TAG_STATE

        def add_card_author_state_handler(update: Update, context: CallbackContext) -> int:
            self.__card_tag = update.message.text

            text = 'Введите автора цитаты'
            logger.info("Ввод автора цитаты")
            update.message.reply_text(text, reply_markup=ReplyKeyboardRemove(), reply_to_message_id=update.message.message_id)
            return ADD_CARD_AUTHOR_STATE

        def add_card_country_state_handler(update: Update, context: CallbackContext) -> int:
            self.__card_author = update.message.text

            text = 'Введите страну (если хотите)'
            logger.info("Ввод страны цитаты")
            reply_keyboard = [['Пропустить этот шаг']]
            keyboard_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text(text, reply_markup=keyboard_markup, reply_to_message_id=update.message.message_id)
            return ADD_CARD_COUNTRY_STATE

        def card_saved_state_handler(update: Update, context: CallbackContext) -> int:
            self.__card_country = '' if update.message.text == "Пропустить этот шаг" else update.message.text
            card = Card(self.__card_text, self.__card_tag, self.__card_author, self.__card_country)
            card_id = self.__card_service.save_new_card(card)
            card.id = card_id
            self.__last_card = card

            self.__card_text, self.__card_tag, self.__card_author, self.__card_country = None, None, None, None

            text = 'Цитата сохранена'
            logger.info("Цитата сохранена")
            reply_keyboard = [['Посмотреть карточку сохраненной цитаты'], ['Вернуться в главное меню']]
            keyboard_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text(text, reply_markup=keyboard_markup)

            # update.message.reply_text(text, reply_markup=markup, reply_to_message_id=update.message.message_id)
            return CARD_SAVED_STATE

        def cancel(update: Update, context: CallbackContext) -> int:
            logger.info("Отмена")
            text = 'Bye! I hope we can talk again some day.'
            update.message.reply_text(text, reply_markup=ReplyKeyboardRemove(), reply_to_message_id=update.message.message_id)
            return ConversationHandler.END

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', main_menu_state_handler)],
            states={
                MAIN_MENU_STATE: [
                    MessageHandler(Filters.regex('^.*Вытянуть карточку.*$'), select_tag_state_handler),
                    MessageHandler(Filters.regex('^.*Добавить карточку.*$'), add_card_text_state_handler),
                    # MessageHandler(Filters.regex('^.*Список всех карточек.*$'), get_all_card_state_handler)
                ],
                SELECT_TAG_STATE: [
                    MessageHandler(Filters.text, show_card_state_handler),
                    CommandHandler('cancel', cancel)
                ],
                SHOW_CARD_STATE: [
                    MessageHandler(Filters.regex('^.*Вытащить еще одну карту.*$'), show_card_state_handler),
                    MessageHandler(Filters.regex('^.*Выбрать колоду.*$'), select_tag_state_handler),
                    MessageHandler(Filters.regex('^.*Вернуться в главное меню.*$'), main_menu_state_handler),
                    CommandHandler('cancel', cancel)
                ],
                ADD_CARD_TEXT_STATE : [
                    MessageHandler(Filters.text, add_card_tag_state_handler),
                    CommandHandler('cancel', cancel)
                ],
                ADD_CARD_TAG_STATE : [
                    MessageHandler(Filters.text, add_card_author_state_handler),
                    CommandHandler('cancel', cancel)
                ],
                ADD_CARD_AUTHOR_STATE : [
                    MessageHandler(Filters.text, add_card_country_state_handler),
                    CommandHandler('cancel', cancel)
                ],
                ADD_CARD_COUNTRY_STATE : [
                    MessageHandler(Filters.text, card_saved_state_handler),
                    CommandHandler('cancel', cancel)
                ],
                CARD_SAVED_STATE : [
                    MessageHandler(Filters.regex('^.*Посмотреть карточку сохраненной цитаты.*$'), show_card_state_handler),
                    MessageHandler(Filters.regex('^.*Вернуться в главное меню.*$'), main_menu_state_handler),
                    MessageHandler(Filters.text, card_saved_state_handler),
                    CommandHandler('cancel', cancel)
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        dispatcher.add_handler(conv_handler)

        def inlinequery(update: Update, context: CallbackContext) -> None:
            """Handle the inline query."""
            query = update.inline_query.query
            logger.info('Inline query "%s"', query)

            all_tags = self.__card_service.get_all_tags() + [None]

            def get_inline_query_result_for_tag(tag):
                card = self.__card_service.get_random_card(tag)
                title = ALL_TAGS_TAG if tag == None else tag
                return InlineQueryResultArticle(id=uuid4(), title=title, input_message_content=InputTextMessageContent(card.text))

            results = [get_inline_query_result_for_tag(tag) for tag in all_tags]
            update.inline_query.answer(results)

        dispatcher.add_handler(InlineQueryHandler(inlinequery))
        # запускаем бота
        updater.start_polling()
        # бесконечная работа бота
        updater.idle()
