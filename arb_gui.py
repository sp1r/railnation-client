#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Scary gui formatting
"""

import Tkinter as Tk

__author__ = 'spir'

from modules_config import bot_names

root = Tk.Tk()

row_1 = Tk.Frame(root)
row_2 = Tk.Frame(root)



gui_fields = {
    'user_name': Tk.StringVar(),
    'user_corp': Tk.StringVar(),
    'time': Tk.StringVar(),

    'judge_state': Tk.StringVar(),
    'inspector_state': Tk.StringVar(),
    'engineer_state': Tk.StringVar(),
    'mechanic_state': Tk.StringVar(),
    'bidder_state': Tk.StringVar(),

    'inspector_collected': Tk.StringVar(),
    'inspector_missed': Tk.StringVar(),
    'inspector_overflows': Tk.StringVar(),
    'inspector_tickets': Tk.StringVar(),
    'inspector_next': Tk.StringVar(),
    'scientist_state': Tk.StringVar(),

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

    'scientist_queue0': Tk.StringVar(),
    'scientist_queue1': Tk.StringVar(),
    'scientist_queue2': Tk.StringVar(),
    'scientist_queue3': Tk.StringVar(),

    'mechanic_floor': Tk.StringVar(),
    
    'bidder_wanted0': Tk.StringVar(),
    'bidder_wanted1': Tk.StringVar(),
    'bidder_wanted2': Tk.StringVar(),
    'bidder_wanted3': Tk.StringVar(),
    'bidder_next': Tk.StringVar(),
}

# default
gui_fields['user_name'].set('?')
gui_fields['user_corp'].set('?')
gui_fields['time'].set('-')

gui_fields['judge_state'].set('RUN')
gui_fields['inspector_state'].set('?')
gui_fields['engineer_state'].set('?')
gui_fields['scientist_state'].set('?')
gui_fields['mechanic_state'].set('?')
gui_fields['bidder_state'].set('?')

gui_fields['inspector_collected'].set('0')
gui_fields['inspector_missed'].set('0')
gui_fields['inspector_overflows'].set('0')
gui_fields['inspector_tickets'].set('0')
gui_fields['inspector_next'].set('-')

gui_fields['engineer_now1'].set('-')
gui_fields['engineer_ready1'].set('-')
gui_fields['engineer_now2'].set('-')
gui_fields['engineer_ready2'].set('-')
gui_fields['engineer_queue0'].set('-')
gui_fields['engineer_queue1'].set('-')
gui_fields['engineer_queue2'].set('-')
gui_fields['engineer_queue3'].set('-')
gui_fields['engineer_queue4'].set('-')
gui_fields['engineer_queue5'].set('-')

gui_fields['scientist_queue0'].set('-')
gui_fields['scientist_queue1'].set('-')
gui_fields['scientist_queue2'].set('-')
gui_fields['scientist_queue3'].set('-')

gui_fields['mechanic_floor'].set('-')

gui_fields['bidder_wanted0'].set('-')
gui_fields['bidder_wanted1'].set('-')
gui_fields['bidder_wanted2'].set('-')
gui_fields['bidder_wanted3'].set('-')
gui_fields['bidder_next'].set('-')

title = Tk.Label(control_block, text="Look at my Bot! My Bot is amazing!!!")
title.grid(row=0, column=0, columnspan=12)

user_name_l = Tk.Label(control_block, text="Имя игрока : ", anchor=Tk.E)
user_name_l.grid(row=1, column=1, columnspan=2)
user_name_v = Tk.Label(control_block, textvariable=gui_fields['user_name'],
                       anchor=Tk.W)
user_name_v.grid(row=1, column=3, columnspan=2)
user_corp_l = Tk.Label(control_block, text="Корпорация : ", anchor=Tk.E)
user_corp_l.grid(row=2, column=1, columnspan=2)
user_corp_v = Tk.Label(control_block, textvariable=gui_fields['user_corp'],
                       anchor=Tk.W)
user_corp_v.grid(row=2, column=3, columnspan=2)

time_v = Tk.Label(control_block, textvariable=gui_fields['time'])
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

###############################################################################

# Inspector (collecting)

ins_title = Tk.Label(inspector_block, text='Жадный Хомяк',
                     height=1, width=28)
ins_title.grid(row=0, column=0, columnspan=4)

ins_collected_l = Tk.Label(inspector_block, text='собрано бонусов :',
                           height=1, width=21, anchor=Tk.E)
ins_collected_l.grid(row=1, column=0, columnspan=3)
ins_collected_v = Tk.Label(inspector_block,
                           textvariable=gui_fields['inspector_collected'],
                           height=1, width=7, relief=Tk.SUNKEN)
ins_collected_v.grid(row=1, column=3)
ins_missed_l = Tk.Label(inspector_block, text='упущено бонусов :',
                        height=1, width=21, anchor=Tk.E)
ins_missed_l.grid(row=2, column=0, columnspan=3)
ins_missed_v = Tk.Label(inspector_block,
                        textvariable=gui_fields['inspector_missed'],
                        height=1, width=7, relief=Tk.SUNKEN)
ins_missed_v.grid(row=2, column=3)
ins_overflows_l = Tk.Label(inspector_block, text='лопнувшие банки :',
                           height=1, width=21, anchor=Tk.E)
ins_overflows_l.grid(row=3, column=0, columnspan=3)
ins_overflows_v = Tk.Label(inspector_block,
                           textvariable=gui_fields['inspector_overflows'],
                           height=1, width=7, relief=Tk.SUNKEN)
ins_overflows_v.grid(row=3, column=3)
ins_tickets_l = Tk.Label(inspector_block, text='получено билетов :',
                         height=1, width=21, anchor=Tk.E)
ins_tickets_l.grid(row=4, column=0, columnspan=3)
ins_tickets_v = Tk.Label(inspector_block,
                         textvariable=gui_fields['inspector_tickets'],
                         height=1, width=7, relief=Tk.SUNKEN)
ins_tickets_v.grid(row=4, column=3)
ins_next_l = Tk.Label(inspector_block, text="следующий :",
                      height=1, width=14)
ins_next_l.grid(row=5, column=0, columnspan=2)
ins_next_v = Tk.Label(inspector_block,
                      textvariable=gui_fields['inspector_next'],
                      height=1, width=14, relief=Tk.SUNKEN)
ins_next_v.grid(row=5, column=2, columnspan=2)


###############################################################################

# Engineer (builder)

eng_title = Tk.Label(engineer_block, text='Неутомимый Джамшут',
                     height=1, width=56)
eng_title.grid(row=0, column=4, columnspan=8)

eng_subtitle1 = Tk.Label(engineer_block, text='строится сейчас',
                         height=1, width=35)
eng_subtitle1.grid(row=1, column=4, columnspan=5)

eng_subtitle2 = Tk.Label(engineer_block, text='очередь строительства',
                         height=1, width=21)
eng_subtitle2.grid(row=1, column=9, columnspan=3)

eng_subtitle3 = Tk.Label(engineer_block, text='управление Джамшутом',
                         height=1, width=35)
eng_subtitle3.grid(row=5, column=4, columnspan=5)

eng_now1_v = Tk.Label(engineer_block,
                      textvariable=gui_fields['engineer_now1'],
                      height=1, width=21, relief=Tk.SUNKEN)
eng_now1_v.grid(row=2, column=4, columnspan=3)

eng_ready1_v = Tk.Label(engineer_block,
                        textvariable=gui_fields['engineer_ready1'],
                        height=1, width=14, relief=Tk.SUNKEN)
eng_ready1_v.grid(row=2, column=7, columnspan=2)

eng_now2_v = Tk.Label(engineer_block,
                      textvariable=gui_fields['engineer_now2'],
                      height=1, width=21, relief=Tk.SUNKEN)
eng_now2_v.grid(row=3, column=4, columnspan=3)

eng_ready2_v = Tk.Label(engineer_block,
                        textvariable=gui_fields['engineer_ready2'],
                        height=1, width=14, relief=Tk.SUNKEN)
eng_ready2_v.grid(row=3, column=7, columnspan=2)

eng_queue0_v = Tk.Label(engineer_block,
                        textvariable=gui_fields['engineer_queue0'],
                        height=1, width=21, relief=Tk.SUNKEN)
eng_queue0_v.grid(row=2, column=9, columnspan=3)

eng_queue1_v = Tk.Label(engineer_block,
                        textvariable=gui_fields['engineer_queue1'],
                        height=1, width=21, relief=Tk.SUNKEN)
eng_queue1_v.grid(row=3, column=9, columnspan=3)

eng_queue2_v = Tk.Label(engineer_block,
                        textvariable=gui_fields['engineer_queue2'],
                        height=1, width=21, relief=Tk.SUNKEN)
eng_queue2_v.grid(row=4, column=9, columnspan=3)

eng_queue3_v = Tk.Label(engineer_block,
                        textvariable=gui_fields['engineer_queue3'],
                        height=1, width=21, relief=Tk.SUNKEN)
eng_queue3_v.grid(row=5, column=9, columnspan=3)

eng_queue4_v = Tk.Label(engineer_block,
                        textvariable=gui_fields['engineer_queue4'],
                        height=1, width=21, relief=Tk.SUNKEN)
eng_queue4_v.grid(row=6, column=9, columnspan=3)

eng_queue5_v = Tk.Label(engineer_block,
                        textvariable=gui_fields['engineer_queue5'],
                        height=1, width=21, relief=Tk.SUNKEN)
eng_queue5_v.grid(row=7, column=9, columnspan=3)

eng_new_e = Tk.Entry(engineer_block, width=7)
eng_new_e.grid(row=6, column=4)

###############################################################################

# Scientist

sci_title = Tk.Label(scientist_block, text='Мудрый Саладин',
                     height=1, width=21)
sci_title.grid(row=0, column=0, columnspan=3)

sci_queue0_v = Tk.Label(scientist_block, 
                        textvariable=gui_fields['scientist_queue0'],
                        height=1, width=21, relief=Tk.SUNKEN)
sci_queue0_v.grid(row=1, column=0, columnspan=3)
sci_queue1_v = Tk.Label(scientist_block, 
                        textvariable=gui_fields['scientist_queue1'],
                        height=1, width=21, relief=Tk.SUNKEN)
sci_queue1_v.grid(row=2, column=0, columnspan=3)
sci_queue2_v = Tk.Label(scientist_block, 
                        textvariable=gui_fields['scientist_queue2'],
                        height=1, width=21, relief=Tk.SUNKEN)
sci_queue2_v.grid(row=3, column=0, columnspan=3)
sci_queue3_v = Tk.Label(scientist_block, 
                        textvariable=gui_fields['scientist_queue3'],
                        height=1, width=21, relief=Tk.SUNKEN)
sci_queue3_v.grid(row=4, column=0, columnspan=3)
sci_subtitle1 = Tk.Label(scientist_block, text='управление Саладином',
                         height=1, width=35)
sci_subtitle1.grid(row=5, column=0, columnspan=3)
sci_new_e = Tk.Entry(scientist_block, width=7)
sci_new_e.grid(row=6, column=0)

###############################################################################

# Mechanic

mec_title = Tk.Label(mechanic_block, text='Шпунтик и Винтик',
                     height=1, width=28)
mec_title.grid(row=0, column=0, columnspan=4)

mec_floor_l = Tk.Label(mechanic_block, text='порог починки :',
                       height=1, width=21)
mec_floor_l.grid(row=1, column=0, columnspan=3)
mec_floor_v = Tk.Label(mechanic_block, textvariable=gui_fields['mechanic_floor'],
                       height=1, width=7, relief=Tk.SUNKEN)
mec_floor_v.grid(row=1, column=3)

mec_subtitle1 = Tk.Label(mechanic_block, text='управление механиками',
                         height=1, width=28)
mec_subtitle1.grid(row=2, column=0, columnspan=4)
mec_floor_e = Tk.Entry(mechanic_block, width=7)
mec_floor_e.grid(row=3, column=0)

###############################################################################

# Bidder

bid_title = Tk.Label(bidder_block, text='Ушлый Брокер',
                     height=1, width=21)
bid_title.grid(row=0, column=0, columnspan=3)

bid_wanted0_v = Tk.Label(bidder_block,
                         textvariable=gui_fields['bidder_wanted0'],
                         height=1, width=21, relief=Tk.SUNKEN)
bid_wanted0_v.grid(row=1, column=0, columnspan=3)
bid_wanted1_v = Tk.Label(bidder_block,
                         textvariable=gui_fields['bidder_wanted1'],
                         height=1, width=21, relief=Tk.SUNKEN)
bid_wanted1_v.grid(row=2, column=0, columnspan=3)
bid_wanted2_v = Tk.Label(bidder_block,
                         textvariable=gui_fields['bidder_wanted2'],
                         height=1, width=21, relief=Tk.SUNKEN)
bid_wanted2_v.grid(row=3, column=0, columnspan=3)
bid_wanted3_v = Tk.Label(bidder_block,
                         textvariable=gui_fields['bidder_wanted3'],
                         height=1, width=21, relief=Tk.SUNKEN)
bid_wanted3_v.grid(row=4, column=0, columnspan=3)
bid_subtitle1 = Tk.Label(bidder_block, text='управление Брокером',
                         height=1, width=35)
bid_subtitle1.grid(row=5, column=0, columnspan=3)
bid_new_e = Tk.Entry(bidder_block, width=7)
bid_new_e.grid(row=6, column=0)
bid_next_l = Tk.Label(bidder_block, text="следующий :",
                      height=1, width=14)
bid_next_l.grid(row=7, column=0, columnspan=2)
bid_next_v = Tk.Label(bidder_block,
                      textvariable=gui_fields['bidder_next'],
                      height=1, width=14, relief=Tk.SUNKEN)
bid_next_v.grid(row=7, column=2, columnspan=2)

if __name__ == '__main__':
    control_block.pack()
    row_1.pack()
    row_2.pack()
    inspector_block.pack(side=Tk.LEFT)
    engineer_block.pack(side=Tk.LEFT)
    scientist_block.pack(side=Tk.LEFT)
    mechanic_block.pack(side=Tk.LEFT)
    bidder_block.pack(side=Tk.LEFT)

    root.mainloop()
    root.destroy()