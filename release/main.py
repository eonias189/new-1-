import sys
import sqlite3

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem, QMessageBox

from addEditCoffeeForm import Ui_Form
from mainUi import Ui_MainWindow


class AddEditForm(QWidget, Ui_Form):
    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self.setupUi(self)

    def closeEvent(self, event):
        if self.mw:
            self.mw.is_creating = False


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect('data/coffee.sqlite')
        self.is_creating = False
        self.load_table()
        self.add.clicked.connect(self.add_value)
        self.redact.clicked.connect(self.redact_value)

    def load_table(self):
        cur = self.con.cursor()
        res = cur.execute("""SELECT ID, sort, step_obj, (SELECT value FROM Type WHERE id=type_id),
vkus, price, obyom FROM data""").fetchall()
        for i, row in enumerate(res):
            if self.tableWidget.rowCount() < len(res):
                self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                if j == 5:
                    elem = str(elem) + ' руб.'
                elif j == 6:
                    elem = str(elem) + ' мл.'
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

    def add_value(self):
        self.is_creating = True
        cur = self.con.cursor()
        new_id = max([i[0] for i in cur.execute('SELECT ID FROM data').fetchall()]) + 1
        self.cur_id = new_id
        self.redact_value()

    def redact_value(self):
        if not self.is_creating:
            self.cur_id = int(self.tableWidget.item(int(self.tableWidget.currentRow()), 0).text())
            cur = self.con.cursor()
            sort, step_obj, type_c, vkus, price, obyom = cur.execute(f"""SELECT sort, step_obj,
(SELECT value FROM Type WHERE id=type_id), vkus, price, obyom FROM data WHERE ID={self.cur_id}""").fetchall()[0]
        self.widget = AddEditForm(self)
        if not self.is_creating:
            self.widget.sort.setText(sort)
            self.widget.step_obj.setText(step_obj)
            self.widget.type.setCurrentText(type_c)
            self.widget.vkus.setText(vkus)
            self.widget.price.setText(str(price))
            self.widget.obyom.setText(str(obyom))
        self.widget.show()
        self.widget.ok.clicked.connect(self.redact_value_1)

    def redact_value_1(self):
        sort, step_obj, type_c, vkus, price, obyom = self.widget.sort.text(), self.widget.step_obj.text(), \
                                                     self.widget.type.currentText(), self.widget.vkus.text(), \
                                                     self.widget.price.text(), self.widget.obyom.text()
        if not all([sort, step_obj, vkus, price, obyom]):
            ms = QMessageBox.about(self.widget, 'Ошибка', 'не должно быть пустых строк для ввода')
        elif not price.isdigit():
            ms = QMessageBox.about(self.widget, 'Ошибка', 'цена должна быть целым положительным числом')
        elif not obyom.isdigit():
            ms = QMessageBox.about(self.widget, 'Ошибка', 'объём должен быть целым положительным числом')
        else:
            cur = self.con.cursor()
            if self.is_creating:
                cur.execute(f"INSERT INTO data VALUES ({self.cur_id}, '', '', 0, '', 0, 0)")
            cur.execute(f"""UPDATE data SET
sort='{sort}', step_obj='{step_obj}', type_id=(SELECT id FROM Type WHERE value='{type_c}'),
vkus='{vkus}', price={price}, obyom={obyom} WHERE ID={self.cur_id}""")
            self.con.commit()
            self.widget.close()
            self.load_table()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
