import sys
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtGui, QtCore


from sudoky import (make_puzzle,
                    is_conflict,
                    is_win
                    )

from overlay import Overlay

GRID_SIZE = 9
REMOVE_COUNT = 20  # сколько цифр убрать
CELL_SIZE = 50


class SudokuWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sudoku — PyQt5")
        self.puzzle, self.solved = make_puzzle(remove_count=REMOVE_COUNT)
        self.current = [row[:] for row in self.puzzle]
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QHBoxLayout(self)

        self.table = QtWidgets.QTableWidget(9, 9)
        self.table.setFixedSize(CELL_SIZE * GRID_SIZE + 2, CELL_SIZE * GRID_SIZE + 2)
        flags = self.windowFlags()
        flags &= ~Qt.WindowMaximizeButtonHint
        self.setWindowFlags(flags)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.table.cellClicked.connect(self.cell_clicked)

        # Настройка размеров ячеек
        for i in range(9):
            self.table.setColumnWidth(i, CELL_SIZE)
            self.table.setRowHeight(i, CELL_SIZE)

        # Заполним значениями
        for r in range(9):
            for c in range(9):
                item = QtWidgets.QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                font = item.font()
                font.setPointSize(16)
                item.setFont(font)
                if self.puzzle[r][c] != 0:
                    item.setText(str(self.puzzle[r][c]))
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    # стиль подсказки
                    item.setForeground(QtGui.QBrush(QtGui.QColor('black')))
                    item.setBackground(QtGui.QBrush(QtGui.QColor('#e0e0e0')))
                    font.setBold(True)
                    item.setFont(font)
                self.table.setItem(r, c, item)

        layout.addWidget(self.table)

        # Панель кнопок справа
        side = QtWidgets.QVBoxLayout()
        side.setAlignment(QtCore.Qt.AlignTop)

        num_label = QtWidgets.QLabel("Цифры:")
        side.addWidget(num_label)

        btn_grid = QtWidgets.QGridLayout()
        self.num_buttons = []
        for i in range(1, 10):
            b = QtWidgets.QPushButton(str(i))
            b.setFixedSize(40, 40)
            b.clicked.connect(self.make_number_handler(i))
            self.num_buttons.append(b)
            btn_grid.addWidget(b, (i - 1) // 3, (i - 1) % 3)
        side.addLayout(btn_grid)

        erase_btn = QtWidgets.QPushButton("Erase")
        erase_btn.clicked.connect(self.erase_cell)
        side.addWidget(erase_btn)

        side.addSpacing(10)
        new_btn = QtWidgets.QPushButton("Легкий")
        new_btn.clicked.connect(lambda: self.new_game(7))
        side.addWidget(new_btn)

        new_btn1 = QtWidgets.QPushButton("Средний")
        new_btn1.clicked.connect(lambda: self.new_game(23))
        side.addWidget(new_btn1)

        new_btn2 = QtWidgets.QPushButton("Сложный")
        new_btn2.clicked.connect(lambda: self.new_game(33))
        side.addWidget(new_btn2)

        show_btn = QtWidgets.QPushButton("Показать решение")
        show_btn.clicked.connect(self.show_solution)
        side.addWidget(show_btn)

        side.addStretch()
        layout.addLayout(side)

        # Состояние выбранной клетки
        self.selected = None  # (r, c)

        self.update_visuals()

    def update_visuals(self):
        # Обновляет значения в таблице и стиль
        for r in range(9):
            for c in range(9):
                item = self.table.item(r, c)
                if item is None:
                    item = QtWidgets.QTableWidgetItem()
                    self.table.setItem(r, c, item)
                if self.current[r][c] == 0:
                    item.setText('')
                    font = item.font()
                    font.setBold(False)
                    item.setFont(font)
                    if self.puzzle[r][c] == 0:
                        item.setBackground(QtGui.QBrush(QtGui.QColor('white')))
                else:
                    item.setText(str(self.current[r][c]))
                if self.puzzle[r][c] != 0:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    item.setBackground(QtGui.QBrush(QtGui.QColor('#e0e0e0')))
                else:
                    item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.highlight_selection()

    def show_win_screen(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Победа!")
        dialog.setModal(True)
        dialog.setFixedSize(400, 200)

        layout = QtWidgets.QVBoxLayout(dialog)

        label = QtWidgets.QLabel("ВЫ ПОБЕДИЛИ!")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("""
            color: green;
            font-size: 36px;
            font-weight: bold;
        """)

        btn = QtWidgets.QPushButton("OK")
        btn.setFixedHeight(40)
        btn.clicked.connect(dialog.accept)

        layout.addStretch()
        layout.addWidget(label)
        layout.addWidget(btn)
        layout.addStretch()
        dialog.move(
            self.geometry().center() - dialog.rect().center()
        )

        dialog.exec_()

    def check_win(self):
        grid = []
        for r in range(9):
            row = []
            for c in range(9):
                item = self.table.item(r, c)
                val = item.text()
                row.append(int(val) if val.isdigit() else 0)
            grid.append(row)

        if is_win(grid, self.solved):
            print('ds')
            self.show_win_screen()


    def cell_clicked(self, r, c):
        # Выбор клетки мышью
        self.selected = (r, c)
        self.highlight_selection()
        self.check_win()
        

    def highlight_selection(self):
        # Сбросить стилевые подсветки
        for r in range(9):
            for c in range(9):
                item = self.table.item(r, c)
                if self.puzzle[r][c] != 0:
                    item.setBackground(QtGui.QBrush(QtGui.QColor('#e0e0e0')))
                else:
                    item.setBackground(QtGui.QBrush(QtGui.QColor('white')))
                item.setForeground(QtGui.QBrush(QtGui.QColor('black')))

        if self.selected is None:
            return
        sr, sc = self.selected
        # подсветка выбранной клетки
        sel_item = self.table.item(sr, sc)
        sel_item.setBackground(QtGui.QBrush(QtGui.QColor("#f0f8ff")))
        # подсветка
        for i in range(9):
            if i != sc:
                it = self.table.item(sr, i)
                it.setBackground(QtGui.QBrush(QtGui.QColor("#335266")))
            if i != sr:
                it = self.table.item(i, sc)
                it.setBackground(QtGui.QBrush(QtGui.QColor('#335266')))
        br, bc = (sr // 3) * 3, (sc // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if (r, c) != (sr, sc):
                    it = self.table.item(r, c)
                    it.setBackground(QtGui.QBrush(QtGui.QColor("#1e7ed3")))

    def make_number_handler(self, num):
        def handler():
            if self.selected is None:
                return
            r, c = self.selected
            if self.puzzle[r][c] != 0:
                return
            self.current[r][c] = num
            self.update_visuals()
            self.check_win()
            # проверяем конфликт
            if is_conflict(self.current, r, c, num):
                self.flash_conflict_cell(r, c)
        return handler

    def erase_cell(self):
        if self.selected is None:
            return
        r, c = self.selected
        if self.puzzle[r][c] != 0:
            return
        self.current[r][c] = 0
        self.update_visuals()
        self.check_win()

    def flash_conflict_cell(self, r, c):
        item = self.table.item(r, c)
        orig_bg = item.background()
        item.setBackground(QtGui.QBrush(QtGui.QColor('#ff9999')))
        QtCore.QTimer.singleShot(400, lambda: self._restore_bg(r, c, orig_bg))

    def _restore_bg(self, r, c, bgbrush):
        item = self.table.item(r, c)
        item.setBackground(bgbrush)
        self.highlight_selection()

    def new_game(self, remvd = 20):
        self.puzzle, self.solved = make_puzzle(remove_count=remvd)
        self.current = [row[:] for row in self.puzzle]
        self.selected = None
        # обновляем таблицу текста и стили
        for r in range(9):
            for c in range(9):
                item = self.table.item(r, c)
                item.setText('')
                font = item.font()
                font.setBold(False)
                item.setFont(font)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.update_visuals()

    def show_solution(self):
        # Заполнить оставшиеся клетки решением
        for r in range(9):
            for c in range(9):
                if self.puzzle[r][c] == 0:
                    self.current[r][c] = self.solved[r][c]
        self.update_visuals()
    






def main():
    app = QtWidgets.QApplication(sys.argv)
    w = SudokuWidget()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
