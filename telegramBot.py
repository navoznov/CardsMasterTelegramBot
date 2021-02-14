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
from cardProvider import CardProvider


class TelegramBot:

    def __init__(self, token: str, card_provider: CardProvider):
        self.__token = token
        self.__card_provider = card_provider


    def go(self) -> None:
        # TODO: длинный метод
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        logger = logging.getLogger(__name__)

        # Create the Updater and pass it your bot's token.
        updater = Updater(self.__token)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        MAIN_MENU_STATE, SHOW_CARD_STATE, SELECT_TAG_STATE = range(3)
        # текст кнопки "выбрать все колоды"
        ALL_TAGS_TAG = "! Все !"

        def main_menu_state_handler(update: Update, context: CallbackContext) -> int:
            logger.info("Главное меню")
            text = 'Привет. Я карточных дел мастер. Выбери, что мы с тобой будем делать'
            reply_keyboard = [['Вытянуть карточку'], ['Добавить карточку'], ['Список всех карточек']]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text(text, reply_markup=markup)
            return MAIN_MENU_STATE

        def select_tag_state_handler(update: Update, context: CallbackContext) -> int:
            text = 'Выбери колоду или "Все", если хочешь смешать все колоды',
            logger.info("Выбрать колоду")
            tags = self.__card_provider.get_all_tags()
            tags = [ALL_TAGS_TAG] + tags
            reply_keyboard = [[tag] for tag in tags]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text(text, reply_markup=markup)
            return SELECT_TAG_STATE

        def show_card_state_handler(update: Update, context: CallbackContext) -> int:
            user_data = context.user_data
            selected_tag = update.message.text
            logger.info('Выбрана колода "%s"', selected_tag)
            card_tag = None if selected_tag == ALL_TAGS_TAG else selected_tag
            card = self.__card_provider.get_random(card_tag)
            card_text = card["text"]
            reply_keyboard = [["Вытащить еще одну карту"], ["Выбрать колоду"], ["Вернуться в главное меню"]]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text(card_text, reply_markup=markup)
            logger.info('Показана цитата "%s"', card_text)
            return SHOW_CARD_STATE

        def cancel(update: Update, context: CallbackContext) -> int:
            logger.info("Отмена")
            text = 'Bye! I hope we can talk again some day.'
            update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', main_menu_state_handler)],
            states={
                MAIN_MENU_STATE: [
                    MessageHandler(Filters.regex('^.*Вытянуть карточку.*$'), select_tag_state_handler),
                    # MessageHandler(Filters.regex('^.*Добавить карточку.*$'), add_card_state_handler),
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
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        dispatcher.add_handler(conv_handler)

        def inlinequery(update: Update, context: CallbackContext) -> None:
            """Handle the inline query."""
            query = update.inline_query.query
            logger.info('Inline query "%s"', query)

            all_tags = self.__card_provider.get_all_tags() + [None]

            def get_inline_query_result_for_tag(tag):
                card = self.__card_provider.get_random(tag)
                text = card["text"]
                title = ALL_TAGS_TAG if tag == None else tag
                return InlineQueryResultArticle(id=uuid4(), title=title, input_message_content=InputTextMessageContent(text))

            results = [get_inline_query_result_for_tag(tag) for tag in all_tags]
            update.inline_query.answer(results)

        dispatcher.add_handler(InlineQueryHandler(inlinequery))
        # запускаем бота
        updater.start_polling()
        # бесконечная работа бота
        updater.idle()
