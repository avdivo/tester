from tkinter import *
from globals import cn
import tkinter.font as tkFont
import pandas as pd
import random


# Окно Редактирования словарей
# Не умеет подстраиваться под размеры экрана, рассчитывалось для 1366х768
class EditorWindow(Toplevel):
    def __init__(self, parent, word_cast):
        super().__init__(parent)
        self.attributes("-fullscreen", True)
        self.focus_set()
        self.bind("<Escape>", self.close_w)
        # self.bind("<space>", self.space)
        # self.bind('<Key>', lambda e, ok=1: self.keypress(e, ok))
        my_font = tkFont.Font(family="Lucida Console", size=20)  # Must come after the previous line

        frame = Frame(self)
        frame.pack()
        scrollbar = Scrollbar(frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.lb = Listbox(frame, yscrollcommand=scrollbar.set, width=89, height=25, font=my_font,
                          selectmode='multiple',exportselection=0)
        self.lb.pack()

        scrollbar.config(command=self.lb.yview)

        self.lb.bind('<<ListboxSelect>>', self.onselect_lb)

        self.word_cast = sorted(list(set(word_cast)), key=lambda x: x[0].casefold(), reverse=False)
        for one, two in reversed(self.word_cast):
            self.lb.insert(0, "{:40}{:}".format(one, two))

        self.file_name = StringVar()  # Переменная для поля ввода (имя файла)
        self.sel_n_words = StringVar()  # Переменная для количества слов которые надо выделить
        self.select_rnd = BooleanVar() # Переменная флажка, случайно или нет выбирать слова
        self.select_rnd.set(1)

        label1 = Label(self, text='Всего слов', font=f'Helvetica 14')
        label2 = Label(self, text='Выделено', font=f'Helvetica 14')
        self.all_words_lab = Label(self, text=len(self.word_cast), font=f'Helvetica 14')
        self.select_words_lab = Label(self, text=len(self.lb.curselection()), font=f'Helvetica 14')
        select_all_btn = Button(self, text='Выделить все', command=self.select_all, font="Helvetica 13", width=14)
        sel_words_btn = Button(self, text='Выбрать', command=self.sel_words, font="Helvetica 13", width=12)
        sel_words_entry = Entry(self, width=4, font="Helvetica 14", textvariable=self.sel_n_words)
        check_rnd = Checkbutton(self, text="Случайных", variable=self.select_rnd, onvalue=1, offvalue=0, font="Helvetica 13")
        unselect_all_btn = Button(self, text='Снять выделение', command=self.unselect_all, font="Helvetica 13", width=15)
        del_btn = Button(self, text='Удалить', command=self.del_sel, font="Helvetica 13", width=14)
        file_name_entry = Entry(self, width=15, font="Helvetica 14", textvariable=self.file_name)
        save_btn = Button(self, text='Сохранить', command=self.save_file, font="Helvetica 13", width=14)

        label1.place(x=10, y=708)
        self.all_words_lab.place(x=120, y=708)
        label2.place(x=10, y=735)
        self.select_words_lab.place(x=120, y=735)
        select_all_btn.place(x=180, y=718)
        sel_words_btn.place(x=335, y=718)
        sel_words_entry.place(x=458, y=720)
        check_rnd.place(x=510, y=714)
        unselect_all_btn.place(x=660, y=718)
        del_btn.place(x=850, y=718)
        file_name_entry.place(x=1030, y=720)
        save_btn.place(x=1200, y=718)

    # listBox
    def onselect_lb(self, n):
        self.select_words_lab['text'] = len(self.lb.curselection())

    # Закрытие окна тестирования
    def close_w(self, n):
        self.destroy()

    # Выбрать все
    def select_all(self):
        self.lb.select_set(0, "end")
        self.select_words_lab['text'] = len(self.lb.curselection())

    # Снять выделение
    def unselect_all(self):
        self.lb.select_clear(0, "end")
        self.select_words_lab['text'] = len(self.lb.curselection())

    # Удалить выбранные
    def del_sel(self):
        items = list(map(int, self.lb.curselection()))
        for item in reversed(items):
            self.lb.delete(item) # Удаляем из ListBox
            del(self.word_cast[item]) # Удаляем из списка
        self.select_words_lab['text'] = len(self.lb.curselection())
        self.all_words_lab['text'] = len(self.word_cast)

    # Выбрать слова
    def sel_words(self):
        count_words = len(self.word_cast)
        select_words = int(self.sel_n_words.get())
        if not select_words or count_words < select_words:
            return
        if self.select_rnd.get():
            c = list(range(0, count_words))
            for i in random.sample(c, select_words):
                self.lb.selection_set(i)
        else:
            # Выбираем последовательно слова сначала
            self.lb.select_set(0, select_words-1)
        self.select_words_lab['text'] = len(self.lb.curselection())

    # Сохранить выделенные
    def save_file(self):
        items = list(map(int, self.lb.curselection()))
        if not self.file_name.get() or not len(items):
            return

        df = dict()
        for i in items:
            if '1' in df:
                df['1'] += [self.word_cast[i][0]]
                df['2'] += [self.word_cast[i][1]]
            else:
                df['1'] = [self.word_cast[i][0]]
                df['2'] = [self.word_cast[i][1]]

        df = pd.DataFrame(df)
        file = cn.PATH + f'\{self.file_name.get()}.xlsx'  # Путь к файлу
        df.to_excel(file, sheet_name='Sheet0', index=False, header=False)
