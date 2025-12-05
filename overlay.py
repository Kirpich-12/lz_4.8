class Overlay(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.resize(parent.size())

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtGui.QColor("black"))
        pen.setWidth(4)
        painter.setPen(pen)
        cell_size = CELL_SIZE

        # Вертикальные линии
        for i in (0, 3, 6, 9):
            x = i * cell_size
            painter.drawLine(x, 0, x, 9 * cell_size)
        # Горизонтальные линии
        for i in (0, 3, 6, 9):
            y = i * cell_size
            painter.drawLine(0, y, 9 * cell_size, y)