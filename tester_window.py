import time
import tkinter.ttk as ttk
import threading
import winsound
from tkinter import *
from globals import cn

# Окно тестирования
class TesterWindow(Toplevel):
    def __init__(self, parent, word_cast):
        super().__init__(parent)
        self.attributes("-fullscreen", True)
        self.focus_set()
        self.bind("<Escape>", self.close_w)
        self.bind("<space>", self.space)
        self.bind('<Key>', lambda e, ok=1: self.keypress(e, ok))
        self.sound = [6000, 100] # Звук для winsound.Beep(3000, 50)
        self.player1 = 0 # Очки игроков
        self.player2 = 0
        self.next_task = self.task(word_cast) # Создаем генератор заданий
        self.stop_timer = 0 # Сообщяет таймеру в поток, что он остановлен
        self.current_task = '' # Текущая пара ворос - ответ в кортеже
        self.counter = len(word_cast) # Количесьтво вопросов
        self.first = 0 # Кто остановил таймер 1, 2 игроки или 0 - если никто (вышли по Пробелу или таймеру)
        self.stage = 0 # Этап игры. Повторяются по кругу для каждого вопроса:
        # 0 - Ожидается Пробел или "z", "/", которые работают если first не 0, т.е. был ответ
        # Если нужно, зачисляются очки и выводится следующий вопрос
        # и запускается таймер на 5 секунд, а этап становится 1
        # Если вопросы кончились выводися прощание и этап меняется на 4
        # 1 - Ворос на экране, запущен и идет таймер.
        # Ожидается "z", "/"  для перехода к этапу 2
        # Пробел или окончание таймера (нет ответа). Переход к этапу 0
        # 2 - Вопрос остается. Запускается таймер 3 сек. для ответа игрока остановившего таймер,
        # его очки подсвечены. По истечении таймера звучит сигнал и переход на этап 3
        # 3 - Подсвечиваются очки 2 игрока, запускается таймер 3 секунды,
        # после истечения которых или при нажатии Пробела выводится ответ и переходит к этапу 0
        # 4 - Выйти как и в любой момент можно по ESC, только с этапом 4 не нужно подтверждать

        self.frame1 = LabelFrame(self, width=cn.W//3, height=100)
        self.frame2 = LabelFrame(self, width=cn.W//3, height=100)
        self.prog1 = ttk.Progressbar(self, length=99, orient='vertical', mode="determinate", maximum=100, value=0)
        self.prog2 = ttk.Progressbar(self, length=99, orient='vertical', mode="determinate", maximum=100, value=0)
        self.score_lab1 = Label(self, text=0, font=f'Helvetica {int(cn.W//22.76)}', width=7)
        self.score_lab2 = Label(self, text=0, font=f'Helvetica {int(cn.W // 22.76)}', width=7)
        self.words_lab = Label(self, text=self.counter, font=f'Helvetica {int(cn.W // 22.76)}', width=7)
        self.question_lab = Text(self, width=30, height=3, font=f'Helvetica {int(cn.W // 22.76)}', bg=self["bg"], bd=1)
        self.question_lab.tag_configure("center", justify='center')
        self.question_lab.insert("1.0", 'Hello! Начнем?')
        self.question_lab.tag_add("center", "1.0", "end")
        self.question_lab.configure(state='disabled')

        self.answer_lab = Text(self, width=30, height=3, font=f'Helvetica {int(cn.W // 22.76)}', bg=self["bg"], bd=1)
        self.answer_lab.tag_configure("center", justify='center')
        self.answer_lab.insert("1.0", '')
        self.answer_lab.tag_add("center", "1.0", "end")
        self.answer_lab.configure(state='disabled')

        size_label_score = (self.score_lab1.winfo_reqwidth(), self.score_lab1.winfo_reqheight())
        size_label_question = (self.question_lab.winfo_reqwidth(), self.question_lab.winfo_reqheight())

        self.frame1.place(x=0, y=0)
        self.frame2.place(x=cn.W-cn.W//3, y=0)
        self.prog1.place(x=cn.W//3-22, y=0)
        self.prog2.place(x=cn.W-cn.W//3, y=0)
        self.score_lab1.place(x=(cn.W//3-size_label_score[0])//2, y=(100-size_label_score[1])//2)
        self.score_lab2.place(x=(cn.W-cn.W//3) + (cn.W//3-size_label_score[0])//2, y=(100 - size_label_score[1]) // 2)
        self.words_lab.place(x=(cn.W//3) + (cn.W//3-size_label_score[0])//2, y=(100 - size_label_score[1]) // 2)
        self.question_lab.place(x=(cn.W-size_label_question[0])//2, y=200)
        self.answer_lab.place(x=(cn.W-size_label_question[0])//2, y=(cn.H-200)//2+200)

    # Изменение вопроса
    def change_question_lab(self, text):
        self.question_lab.configure(state='normal')
        if text == '':
            self.question_lab.delete('1.0', 'end')
        else:
            self.question_lab.insert('1.0', text)
            self.question_lab.tag_add("center", "1.0", "end")
        self.question_lab.configure(state='disabled')

    # Изменение ответа
    def change_answer_lab(self, text):
        self.answer_lab.configure(state='normal')
        if text == '':
            self.answer_lab.delete('1.0', 'end')
        else:
            self.answer_lab.insert('1.0', text)
            self.answer_lab.tag_add("center", "1.0", "end")
        self.answer_lab.configure(state='disabled')

    # Закрытие окна тестирования
    def close_w(self, n):
        self.destroy()

    # Реакция на клавишу Пробел
    # Выход из функции таймера так же иммитирует нажатие пробела, обработка выходов обрабатывается тут
    def space(self, n):
        self.bind('<Key>', lambda e, ok=1: self.keypress(e, ok)) # Разрешаем кнопки 'z' и '/'
        if self.stage == 0:
            winsound.Beep(self.sound[0], self.sound[1])
            # Программа ожидает нажатие пробела для показа нового задания
            # Но прежде, если ожидался ответ, self.first показывает от какого игрока, он получает -1 - не ответил
            if self.first != 0 :
                if self.first == 1:
                    self.player1 -= 1
                else:
                    self.player2 -= 1
                self.score_lab1['text'] = self.player1
                self.score_lab2['text'] = self.player2
                self.first = 0

            self.change_question_lab('')
            self.change_answer_lab('')
            try:
                # Если задания не кончились, вывести новое и запустить таймер
                self.current_task = next(self.next_task) # Читаем задание
                self.counter -= 1
                self.words_lab['text'] = self.counter # Меняем счетчик
                self.change_question_lab(self.current_task[0]) # Печать вопроса
                self.stage = 1 # Меняем этап на показа задания и ожидаем окончание таймера, отмену или ответ
                thread = threading.Thread(target=self.run_timer, args=(5,))
                thread.start()
            except StopIteration:
                self.change_question_lab('THE END - КОНЕЦ')
                self.stage = 4
        elif self.stage == 1:
            # Нажатие пробела на этапе 1 означает окончание времени или пропуск вопроса пользователями
            # значит выводим ответ и переходим к этапу 0
            self.stop_timer = 1 # Если нажал пользователь, нужно остановить таймер (убить процесс)
            self.change_answer_lab(self.current_task[1]) # Выводим ответ
            self.stage = 0
        elif self.stage == 2:
            # Нажатие пробела на этапе 2 означает что либо кончился таймер 1 игрока, либо нажат пробел
            # Если таймер кончился сам то stop_timer будет 2
            if self.stop_timer == 2:
                # Время первого игрока на ответ вышло, пошло время второго
                winsound.Beep(self.sound[0], self.sound[1])
                thread = threading.Thread(target=self.run_timer, args=(3, 1 if self.first == 2 else 2))
                self.stage = 3 # Пошло время второго игрока
                thread.start()
            else:
                # Таймер не кончился, но игроки нажали Пробел. Выводим ответ, останавливаем таймер. Переход к этапу 0
                winsound.Beep(self.sound[0], self.sound[1])
                self.stop_timer = 1  # Остановить таймер (убить процесс)
                self.change_answer_lab(self.current_task[1]) # Выводим ответ
                self.stage = 0
        elif self.stage == 3:
            # Нажатие пробела на этапе 3 означает что либо кончился таймер 2 игрока, либо нажат пробел
            # В любом случае: выводим ответ, останавливаем таймер. Переход к этапу 0
            winsound.Beep(self.sound[0], self.sound[1])
            self.stop_timer = 1  # Остановить таймер (убить процесс)
            self.change_answer_lab(self.current_task[1]) # Выводим ответ
            self.stage = 0


    # Нажатие других клавиш
    # Принимает event и разрешение на работу функции ок=1 (событие меняется чтоб предотвратить повторное нажатие)
    def keypress(self, key, ok):
        if not ok:
            return
        # Может быть нажата клавиша первого ('z') или второго ('/') игрока, определяем нажавшего
        # Если не эти клавиши - покидеем функцию
        if key.keycode == 90:
            player = 1
        elif key.keycode == 191:
            player = 2
        else:
            return
        # Кто то нажал. Дальнейшая реакция зависит от этапа
        # На этапе 1 определяется какой игрок отвечает первым, какой вторым, запускается таймер он сам выберет для кого
        if self.stage == 1:
            winsound.Beep(self.sound[0], self.sound[1])
            self.stop_timer = 1  # Остановить таймер (убить процесс)
            self.bind('<Key>', lambda e, ok=0: self.keypress(e, ok)) # Запрещаем кнопки 'z' и '/'
            while self.stop_timer:
                # Ждем остановки таймера
                self.update()
            self.first = player

            thread = threading.Thread(target=self.run_timer, args=(3, player)) # Таймер для того кто остановил
            self.stage = 2
            thread.start()
        if self.stage == 0:
            # Если клавиши нажаты на этапе 0, зачисляем очки, если self.first не 0 (т.е. кто-то хотел ответить)
            # Ответивший получает 1 очко, а остановивший, но не ответивший -1
            if self.first != 0:
                if player == 1:
                    self.player1 += 1
                else:
                    self.player2 += 1
                if player != self.first:
                    if self.first == 1:
                        self.player1 -= 1
                    else:
                        self.player2 -= 1
            self.score_lab1['text'] = self.player1
            self.score_lab2['text'] = self.player2
            self.first = 0

    # Генератор заданий
    def task(self, word_cast):
        for i in word_cast:
            yield i

    # Таймер в потоке обрабатывает прогресс бары и сообщяет когда завершится
    # Если аргумент player не передан, то работают оба прогресс бара
    def run_timer(self, second, player=0):
        self.stop_timer = 0 # Таймер идет
        if player == 0 or player == 1:
            self.prog1['value'] = 100
        if player == 0 or player == 2:
            self.prog2['value'] = 100
        progress = 100
        section = 100 / (second * 5)
        while progress > 0:
            if self.stop_timer:
                # Принудительная остановка таймера
                self.prog1['value'] = 0
                self.prog2['value'] = 0
                self.stop_timer = 0
                return
            time.sleep(0.2)
            progress -= section # Каждые 0.2 секунды снимает 2 риски с прогрессбара, пока он не опустеет
            if player == 0 or player == 1:
                self.prog1['value'] = progress if progress >= 0 else 0
            if player == 0 or player == 2:
                self.prog2['value'] = progress if progress >= 0 else 0
        self.stop_timer = 2 # Таймер завершился сам
        self.event_generate('<space>') # Генерируем событие нажатия пробела
        return
