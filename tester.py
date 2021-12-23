from tkinter import *
import tkinter.font as tkFont
import os
import pandas as pd
import random
import tester_window
import editor_window
from globals import cn

# ----------------------------------------------------------------------------------------------------------------------
# Основное окно
class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("TESTER")

        # Размер экране
        cn.W = self.winfo_screenwidth()
        cn.H = self.winfo_screenheight()

        size_window = (400, 600)
        # Положение окна по центру
        self.geometry(f'{size_window[0]}x{size_window[1]}+{(cn.W-size_window[0])//2}+{(cn.H-size_window[1])//2}')

        self.words = StringVar() # Переменная для поля ввода

        # Элементы управления
        sf = tkFont.Font(family='Helvetica', size=16, weight='bold')
        self.dict_list = Listbox(self, height=20, width=40, font=sf, selectmode='multiple',exportselection=0)
        self.word = Entry(self, width=5, font="Helvetica 14", textvariable=self.words)
        lab = Label(text="СЛУЧАЙНЫХ СЛОВ", font="Helvetica 14")
        self.editor_btn = Button(self, text='Редактор', command=self.edit, font="Helvetica 14", width=15)
        self.start_btn = Button(self, text='Тест', command=self.start, font="Helvetica 14", width=15)

        self.dict_list.place(x=0, y=0)
        self.word.place(x=60, y=520)
        lab.place(x=130, y=520)
        self.editor_btn.place(x=13, y=555)
        self.start_btn.place(x=213, y=555)

        # Клик по ListBox
        self.dict_list.bind('<<ListboxSelect>>', self.clickEvent)

        self.files = os.listdir(cn.PATH)
        for i in self.files:
            if i.endswith('.xlsx'):
                self.dict_list.insert(END, i[0:-5])
        self.dict_list.select_set(0)

    # Редактировать словари
    def edit(self):
        word_all = self.create_cast() # Создаем список тестов из выбранных словарей
        if not word_all:
            return
        editor = editor_window.EditorWindow(self, word_all)
        editor.grab_set()

    # Начать тест
    def start(self):
        word_all = self.create_cast() # Создаем список тестов из выбранных словарей
        if not word_all:
            return
        # Если указано какое-то количество случайных слов, то готовим список
        # выбирая нужное количество случайных слов (с повторами)
        if self.words.get().isdigit():
            word_cast = [word_all[random.randint(0, len(word_all) - 1)] for i in range(0, int(self.words.get()))]

            # Выбор случайных позиций из всего списка (не повторяющихся)
            # word_cast = []
            # while len(word_cast) < int(words.get()):
            #     word_cast += [word_all[random.randint(0, len(word_all))]]
        else:
            # Случайные слова выбирать не надо, берем список слов целиком
            word_cast = word_all
            random.shuffle(word_cast) # Перемешиваем список заданий

        tester = tester_window.TesterWindow(self, word_cast)
        tester.grab_set()

    # Подготовка списка одинаковая часть для редактора (без сортировки) и тестера
    def create_cast(self):
        # Готовим список имен выбранных файлов
        selected_files = [self.dict_list.get(i) for i in self.dict_list.curselection()]
        if not len(selected_files):
            return
        # Готовим список слов из выбранных словарей
        word_all = []
        for i in selected_files:
            file = cn.PATH + f'\{i}.xlsx'  # Путь к очередному файлу
            excel_df = pd.read_excel(file, 'Sheet0')  # Читаем файл в DataFrame
            word_all += [(b[0], b[1]) for a, b in excel_df.iterrows()]  # Перенос ataFrame в список кортежей
        return word_all

    # Клик по ListBox для очистки поля ввода количества случайных слов
    def clickEvent(self, n):
        self.words.set('')



if __name__ == "__main__":

    app = App()
    app.mainloop()
