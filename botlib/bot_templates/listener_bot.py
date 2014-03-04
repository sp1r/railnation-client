#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'spir'

from bot import Bot


class ListenerBot(Bot):
    """
    Этот тип бота сидит на своем пайпе, слушает сообщения от других ботов
    и реагирует на них.
    И все.
    """
    def __init__(self, name, pipe):
        Bot.__init__(self, name, pipe)

    def bot_logic(self):
        self.wait_for_message()