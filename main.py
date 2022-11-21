import sys
import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.con = sqlite3.connect('coffee.sqlite')
        self.load_table()

    def load_table(self):
        cur = self.con.cursor()
        res = cur.execute("""SELECT ID,
(SELECT name FROM Sort WHERE id=sort_id), step_obj, (SELECT value FROM Type WHERE id=type_id),
vkus, price, obyom FROM data""").fetchall()
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                if j == 5:
                    elem = str(elem) + ' руб.'
                elif j == 6:
                    elem = str(elem) + ' мл.'
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
