from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QDate
from PySide6.QtUiTools import QUiLoader
from datetime import date
import sys


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = QUiLoader().load("main.ui")

        today = QDate.fromString(date.today().strftime('%d/%m/%Y'),
                                 'dd/MM/yyyy')
        self.ui.endDate.setDate(today)

        self.ui.show()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec()


if __name__ == '__main__':
    main()