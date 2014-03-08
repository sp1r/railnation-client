#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'spir'

import Tkinter as Tk

from core.templates import Bot


bot_names = ['judge', 'game', 'log', 'stranger', 'builder',
             'mechanic', 'scientist']


class Monitor(Bot):
    """
    Адов гуй.

    Сервисы:
       Порт 514.
          На входе ожидаются следующие сообщения:
          msg = {'variable':string, 'value':xxx, 'add':xxx, 'sub':xxx}
    """
    def __init__(self, name, pipe):
        Bot.__init__(self, name, pipe)
        self.root = Tk.Tk()

        self.gui_fields = {
            'user_name': Tk.StringVar(),
            'user_corp': Tk.StringVar(),
            'time': Tk.StringVar(),
            
            'judge_state': Tk.StringVar(),
            'game_state': Tk.StringVar(),
            'log_state': Tk.StringVar(),
            'stranger_state': Tk.StringVar(),
            'builder_state': Tk.StringVar(),
            'mechanic_state': Tk.StringVar(),
            'scientist_state': Tk.StringVar(),
        
            'inspector_collected': Tk.StringVar(),
            'inspector_missed': Tk.StringVar(),
            'inspector_overflows': Tk.StringVar(),
            'inspector_tickets': Tk.StringVar(),
            'inspector_next': Tk.StringVar(),
            'inspector_min': Tk.StringVar(),
            'inspector_max': Tk.StringVar(),
        
            'engineer_now1': Tk.StringVar(),
            'engineer_ready1': Tk.StringVar(),
            'engineer_now2': Tk.StringVar(),
            'engineer_ready2': Tk.StringVar(),
            'engineer_queue0': Tk.StringVar(),
            'engineer_queue1': Tk.StringVar(),
            'engineer_queue2': Tk.StringVar(),
            'engineer_queue3': Tk.StringVar(),
            'engineer_queue4': Tk.StringVar(),
            'engineer_queue5': Tk.StringVar(),
            'engineer_queue6': Tk.StringVar(),
            'engineer_queue7': Tk.StringVar(),
            'engineer_queue8': Tk.StringVar(),
            'engineer_queue9': Tk.StringVar(),
        
            'scientist_queue0': Tk.StringVar(),
            'scientist_queue1': Tk.StringVar(),
            'scientist_queue2': Tk.StringVar(),
            'scientist_queue3': Tk.StringVar(),
            'scientist_queue4': Tk.StringVar(),
            'scientist_queue5': Tk.StringVar(),
            'scientist_queue6': Tk.StringVar(),
            'scientist_queue7': Tk.StringVar(),
            'scientist_queue8': Tk.StringVar(),
            'scientist_queue9': Tk.StringVar(),
        
            'mechanic_floor': Tk.StringVar(),
        }

    def configure(self):

        row_1 = Tk.Frame(self.root)
        row_2 = Tk.Frame(self.root)

        control_block = Tk.Frame(self.root)
        inspector_block = Tk.Frame(row_1)
        engineer_block = Tk.Frame(row_1)
        scientist_block = Tk.Frame(row_2)
        mechanic_block = Tk.Frame(row_2)
        bidder_block = Tk.Frame(row_2)

        self.gui_fields['user_name'].set('?')
        self.gui_fields['user_corp'].set('?')
        self.gui_fields['time'].set('-')

        self.gui_fields['judge_state'].set('?')
        self.gui_fields['game_state'].set('?')
        self.gui_fields['logger_state'].set('?')
        self.gui_fields['stranger_state'].set('?')
        self.gui_fields['builder_state'].set('?')
        self.gui_fields['mechanic_state'].set('?')
        self.gui_fields['scientist_state'].set('?')

        self.gui_fields['inspector_collected'].set('0')
        self.gui_fields['inspector_missed'].set('0')
        self.gui_fields['inspector_overflows'].set('0')
        self.gui_fields['inspector_tickets'].set('0')
        self.gui_fields['inspector_next'].set('-')
        self.gui_fields['inspector_min'].set('?')
        self.gui_fields['inspector_max'].set('?')

        self.gui_fields['engineer_now1'].set('-')
        self.gui_fields['engineer_ready1'].set('-')
        self.gui_fields['engineer_now2'].set('-')
        self.gui_fields['engineer_ready2'].set('-')
        self.gui_fields['engineer_queue0'].set('-')
        self.gui_fields['engineer_queue1'].set('-')
        self.gui_fields['engineer_queue2'].set('-')
        self.gui_fields['engineer_queue3'].set('-')
        self.gui_fields['engineer_queue4'].set('-')
        self.gui_fields['engineer_queue5'].set('-')
        self.gui_fields['engineer_queue6'].set('-')
        self.gui_fields['engineer_queue7'].set('-')
        self.gui_fields['engineer_queue8'].set('-')
        self.gui_fields['engineer_queue9'].set('-')

        self.gui_fields['scientist_queue0'].set('-')
        self.gui_fields['scientist_queue1'].set('-')
        self.gui_fields['scientist_queue2'].set('-')
        self.gui_fields['scientist_queue3'].set('-')
        self.gui_fields['scientist_queue4'].set('-')
        self.gui_fields['scientist_queue5'].set('-')
        self.gui_fields['scientist_queue6'].set('-')
        self.gui_fields['scientist_queue7'].set('-')
        self.gui_fields['scientist_queue8'].set('-')
        self.gui_fields['scientist_queue9'].set('-')

        self.gui_fields['mechanic_floor'].set('-')

        title = Tk.Label(control_block,
                         text="Look at my Bot! My Bot is amazing!!!")
        title.grid(row=0, column=0, columnspan=12)

        user_name_l = Tk.Label(control_block, text="Имя игрока : ", anchor=Tk.E)
        user_name_l.grid(row=1, column=1, columnspan=2)
        user_name_v = Tk.Label(control_block,
                               textvariable=self.gui_fields['user_name'],
                               anchor=Tk.W)
        user_name_v.grid(row=1, column=3, columnspan=2)
        user_corp_l = Tk.Label(control_block, text="Корпорация : ", anchor=Tk.E)
        user_corp_l.grid(row=2, column=1, columnspan=2)
        user_corp_v = Tk.Label(control_block,
                               textvariable=self.gui_fields['user_corp'],
                               anchor=Tk.W)
        user_corp_v.grid(row=2, column=3, columnspan=2)

        time_v = Tk.Label(control_block, textvariable=self.gui_fields['time'])
        time_v.grid(row=1, column=7, columnspan=4)

        bots = {}
        for x in range(12):
            if bot_names[x]:
                name_field = '{0:}_name'.format(bot_names[x])
                bots[name_field] = Tk.Label(control_block, text=bot_names[x],
                                            height=1, width=7, relief=Tk.GROOVE)
                bots[name_field].grid(row=3, column=x)
            else:
                name_field = '{0:d}_name_stub'.format(x)
                bots[name_field] = Tk.Label(control_block, text="",
                                            height=1, width=7, relief=Tk.GROOVE)
                bots[name_field].grid(row=3, column=x)

        control_block.pack()
        row_1.pack()
        row_2.pack()
        inspector_block.pack(side=Tk.LEFT)
        engineer_block.pack(side=Tk.LEFT)
        scientist_block.pack(side=Tk.LEFT)
        mechanic_block.pack(side=Tk.LEFT)
        bidder_block.pack(side=Tk.LEFT)

        self.root.mainloop()
        self.root.destroy()
