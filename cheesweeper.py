#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Библиотека графического интерфейса Tk
import tkinter, tkinter.messagebox

# Генератор псевдослучайных чисел
from random import randrange


##### КЛАСС CELL #####

class Cell(object):
    """Представляет ячейку игрового поля"""

    def __init__(self, field, x, y):
        # Игровое поле
        self.__field = field

        # Количество флагов вокруг ячейки
        self.__flag_count = 0

        # Помечена ли ячейка флагом
        self.__is_flagged = False

        # Находится ли в ячейке мина
        self.__is_mine = False

        # Открыта ли ячейка
        self.__is_opened = False

        # Количество мин вокруг ячейки
        self.__mine_count = 0

        # Координаты ячейки в игровом поле
        self.__x = x
        self.__y = y

        # Соседствующие с данной ячейки
        self.__sides = [
            (
                # ...
                # ?X.
                # ...
                self.x > 0,
                (self.x - 1, self.y)
            ),
            (
                # ?..
                # .X.
                # ...
                self.x > 0 and self.y > 0,
                (self.x - 1, self.y - 1)
            ),
            (
                # .?.
                # .X.
                # ...
                self.y > 0,
                (self.x, self.y - 1)
            ),
            (
                # ..?
                # .X.
                # ...
                self.x < self.__field.x - 1 and self.y > 0,
                (self.x + 1, self.y - 1)
            ),
            (
                # ...
                # .X?
                # ...
                self.x < self.__field.x - 1,
                (self.x + 1, self.y)
            ),
            (
                # ...
                # .X.
                # ..?
                self.x < self.__field.x - 1 and self.y < self.__field.y - 1,
                (self.x + 1, self.y + 1)
            ),
            (
                # ...
                # .X.
                # .?.
                self.y < self.__field.y - 1,
                (self.x, self.y + 1)
            ),
            (
                # ...
                # .X.
                # ?..
                self.x > 0 and self.y < self.__field.y - 1,
                (self.x - 1, self.y + 1)
            )
        ]


    @property
    def flag_count(self):
        """Количество флагов вокруг данной ячейки"""
        return self.__flag_count


    @flag_count.setter
    def flag_count(self, value):
        """Количество флагов вокруг данной ячейки"""
        has_changed = (value != self.flag_count)
        if not has_changed: return

        self.__flag_count = value


    @property
    def is_flagged(self):
        """Помечена ли ячейка флагом"""
        return self.__is_flagged


    @is_flagged.setter
    def is_flagged(self, value):
        """Помечена ли ячейка флагом"""
        has_changed = (value != self.is_flagged)
        if not has_changed or self.is_opened:
            return

        self.__is_flagged = value

        if value:
            delta = 1
        else:
            delta = -1

        self.__execute_around(Cell.__is_flagged_lambda, delta)

        for callback in self.__field.change_callbacks:
            callback(self)


    @staticmethod
    def __is_flagged_lambda(cell, delta):
        """Обновляет количество флагов для указанной ячейки"""
        cell.flag_count += delta


    @property
    def is_mine(self):
        """Находится ли в ячейке мина"""
        return self.__is_mine

    @is_mine.setter
    def is_mine(self, value):
        """Находится ли в ячейке мина"""
        has_changed = (value != self.is_mine)
        if not has_changed: return

        self.__is_mine = value

        if value:
            delta = 1
        else:
            delta = -1

        self.__execute_around(Cell.__is_mine_lambda, delta)


    @staticmethod
    def __is_mine_lambda(cell, delta):
        """Обновляет количество флагов для указанной ячейки"""
        cell.mine_count += delta


    @property
    def is_opened(self):
        """Открыта ли ячейка"""
        return self.__is_opened


    @is_opened.setter
    def is_opened(self, value):
        """Открыта ли ячейка"""
        has_changed = (value != self.__is_opened)
        if not has_changed: return

        self.__is_opened = value

        if value:
            delta = 1
        else:
            delta = -1

        self.__field.opened_count += delta

        for callback in self.__field.change_callbacks:
            callback(self)


    @property
    def mine_count(self):
        """Количество мин вокруг данной ячейки"""
        return self.__mine_count


    @mine_count.setter
    def mine_count(self, value):
        """Количество мин вокруг данной ячейки"""

        has_changed = (value != self.mine_count)
        if not has_changed or self.is_mine:
            return

        self.__mine_count = value

        if self.is_opened:
            for callback in self.__field.change_callbacks:
                callback(self)


    @property
    def x(self):
        """Координата ячейки по оси X (начиная с 0)"""
        return self.__x


    @property
    def y(self):
        """Координата ячейки по оси Y (начиная с 0)"""
        return self.__y


    def open(self, is_chain = False):
        """Открывает эту ячейку и те, что вокруг неё с учётом флагов"""

        if (self.is_flagged) or (is_chain and self.is_opened):
            return True

        self.is_opened = True

        if self.is_mine:
            if self.__field.explosion is None:
                self.__field.explosion = (self.x, self.y)

            return False

        if self.flag_count >= self.mine_count:
            return self.__execute_around(
                lambda cell, arg: cell.open(arg),
                True,
                acc_fun = lambda a, b: a & b,
                acc_def = True
            )

        return True


    def __execute_around(self, func, arg, acc_fun = None, acc_def = None):
        """Выполняет функцию для каждой ячейки вокруг данной"""

        output = acc_def

        for side in self.__sides:
            has_cell, coords = side

            if not has_cell:
                continue

            result = func(self.__field.cells[coords[1]][coords[0]], arg)

            if acc_fun is not None:
                output = acc_fun(result, output)

        return output


    def __repr__(self):
        """Возвращает текстовое представление ячейки"""

        if self.is_mine:
            return '*'
        elif self.mine_count == 0:
            return '.'
        else:
            return str(self.mine_count)


##### КЛАСС FIELD #####

class Field(object):
    """Представляет игровое поле"""

    def __init__(self, x, y, mines):
        self.__cell_count = x * y
        self.__explosion = None
        self.__is_initialized = False
        self.__mines = mines
        self.__need_opened = (x * y) - mines
        self.__opened_count = 0
        self.__x = x
        self.__y = y

        self.cells = [
            [Cell(self, xi, yi) for xi in range(self.x)]
            for yi in range(self.y)
        ]

        # Функции, вызываемые при изменении состояния ячейки
        self.change_callbacks = []


    @property
    def explosion(self):
        """Определяет ячейку, в которой произошёл первый взрыв"""
        return self.__explosion

    @explosion.setter
    def explosion(self, value):
        """Определяет ячейку, в которой произошёл первый взрыв"""

        has_changed = (value != self.explosion)
        if not has_changed:
            return

        self.__explosion = value

        for callback in self.change_callbacks:
            callback(self.cells[value[1]][value[0]])


    @property
    def has_won(self):
        """Определяет, выиграл ли игрок"""
        return self.opened_count == self.__need_opened


    @property
    def is_initialized(self):
        """Определяет, было ли инициализировано игровое поле"""
        return self.__is_initialized


    @property
    def opened_count(self):
        """Количество открытых ячеек поля"""
        return self.__opened_count


    @opened_count.setter
    def opened_count(self, value):
        """Количество открытых ячеек поля"""
        self.__opened_count = value


    @property
    def x(self):
        """Размер поля по оси X"""
        return self.__x


    @property
    def y(self):
        """Размер поля по оси Y"""
        return self.__y


    def initialize(self):
        """Расставляет мины по полю в соответствии с указанным количеством"""
        if self.is_initialized:
            return

        cell_list = []

        for yi in range(self.y):
            for xi in range(self.x):
                if self.cells[yi][xi].is_opened:
                    continue
                cell_list.append((xi, yi))

        for _ in range(self.__mines):
            index = randrange(len(cell_list))
            coord = cell_list[index]
            self.cells[coord[1]][coord[0]].is_mine = True
            cell_list.pop(index)

        self.__is_initialized = True


    def open_all(self):
        """Открывает все ячейки игрового поля"""
        for yi in range(self.y):
            for xi in range(self.x):
                self.cells[yi][xi].is_opened = True


    def __repr__(self):
        """Возвращает строковое представление игрового поля"""

        output = ''

        for yi in range(self.y):
            for xi in range(self.x):
                output += str(self.cells[yi][xi])
            output += '\n'

        return output


##### КЛАСС GAMETK #####

class GameTk(object):
    """Описывает игру в рамках графического интерфейса Tk"""

    def __init__(self, x, y, mines):
        self.__x = x
        self.__y = y
        self.__mines = mines
        self.__field = Field(x, y, mines)

        self.__field.change_callbacks.append(self.cell_update_callback)

        self.__window = tkinter.Tk()
        self.__window.resizable(0,0)
        self.__window.title('Сапёр')

        frame = tkinter.Frame(self.__window)
        frame.pack()

        self.__cell_img = {
            'closed': tkinter.PhotoImage(file = 'img/cell_closed.gif'),
            'explosion': tkinter.PhotoImage(file = 'img/cell_explosion.gif'),
            'flag': tkinter.PhotoImage(file = 'img/cell_flag.gif'),
            'mine': tkinter.PhotoImage(file = 'img/cell_mine.gif'),
            'mineflag': tkinter.PhotoImage(file = 'img/cell_mineflag.gif')
        }
        for i in range(9):
            self.__cell_img[i] = tkinter.PhotoImage(file = 'img/cell_{}.gif'.format(i))

        self.__buttons = []

        for yi in range(y):
            row = []

            for xi in range(x):
                button = tkinter.Button(
                    frame,
                    image = self.__cell_img['closed']
                )

                button.coords = (xi, yi)
                button.bind('<Button-1>', self.__button_leftclick)
                button.bind('<Button-2>', self.__button_rightclick)
                button.bind('<Button-3>', self.__button_rightclick)
                button.grid(row = yi, column = xi)

                row.append(button)

            self.__buttons.append(row)

        caption = tkinter.Label(
            frame,
            text = 'Автор: Фостер Сноухилл, гр. 7-АиСн-4, Московский политех'
        )
        caption.grid(row = y, column = 0, columnspan = x)

        self.center()
        self.__window.focus()
        self.__window.mainloop()


    def __button_leftclick(self, event):
        """Обрабатывает щелчок левой кнопки мыши по ячейке"""

        (x, y) = event.widget.coords
        cell = self.__field.cells[y][x]

        if not self.__field.is_initialized:
            cell.is_opened = True
            self.__field.initialize()
            print(self.__field)

        result = cell.open()

        self.__window.update_idletasks()

        if not result:
            self.__field.open_all()
            coords = self.__field.explosion
            cell = self.__field.cells[coords[1]][coords[0]]
            self.cell_update_callback(cell)
            self.__window.update_idletasks()
            tkinter.messagebox.showinfo('Сапёр', 'Игра окончена. Вы проиграли :(')
            self.__window.quit()
        elif self.__field.has_won:
            self.__field.open_all()
            self.__window.update_idletasks()
            tkinter.messagebox.showinfo('Сапёр', 'Игра окончена. Вы выиграли! :D')
            self.__window.quit()


    def __button_rightclick(self, event):
        """Обрабатывает щелчок правой кнопки мыши"""

        if not self.__field.is_initialized:
            return

        (x, y) = event.widget.coords
        cell = self.__field.cells[y][x]

        if cell.is_opened:
            return

        cell.is_flagged = not cell.is_flagged


    def cell_update_callback(self, cell):
        """Обновляет визуальное состояние ячейки"""

        button = self.__buttons[cell.y][cell.x]

        if cell.is_opened:
            if self.__field.explosion == (cell.x, cell.y):
                button.config(image = self.__cell_img['explosion'])
            elif cell.is_mine:
                if cell.is_flagged:
                    button.config(image = self.__cell_img['mineflag'])
                else:
                    button.config(image = self.__cell_img['mine'])
            else:
                button.config(image = self.__cell_img[cell.mine_count])
        else:
            if cell.is_flagged:
                button.config(image = self.__cell_img['flag'])
            else:
                button.config(image = self.__cell_img['closed'])


    def center(self):
        """Выравнивает окно по центру экрана"""

        self.__window.update_idletasks()

        w = self.__window.winfo_screenwidth()
        h = self.__window.winfo_screenheight()

        size = tuple(int(_) for _ in self.__window.geometry().split('+')[0].split('x'))

        x = w / 2 - size[0] / 2
        y = h / 2 - size[1] / 2

        self.__window.geometry("%dx%d+%d+%d" % (size + (x, y)))


if __name__ == '__main__':
    GameTk(16, 16, 32)
