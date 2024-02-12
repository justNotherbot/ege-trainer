import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import sys


class QTManager:

    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window = QtWidgets.QMainWindow()
        self.main_widget = QtWidgets.QWidget(self.main_window)
        self.main_window.setCentralWidget(self.main_widget)
        self.main_layout = QtWidgets.QVBoxLayout(self.main_widget)


class RODelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return


class TableView(QtWidgets.QTableWidget):
    def __init__(self, *args):
        super(QtWidgets.QTableWidget, self).__init__(*args)

        #self.setData()

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().sectionResized.connect(self.resizeRowsToContents)
        self.verticalHeader().setVisible(False)

        delegate = RODelegate(self)
        self.setItemDelegate(delegate)
 
    def set_data(self, headers, data):
        for n, key in enumerate(headers):
            for m, item in enumerate(data[key]):
                new_item = QtWidgets.QTableWidgetItem(item)
                self.setItem(m, n, new_item)
        self.setHorizontalHeaderLabels(headers)
 

class Table:

    def __init__(self, headers, n_rows, default_el=""):
        self.content = {}
        self.headers = headers
        self.size = [n_rows, len(headers)]

        for i in headers:
            self.content[i] = [default_el] * n_rows

    def add_row(self, row):
        self.size[0] += 1

        for i in range(len(self.headers)):
            self.content[self.headers[i]].append(row[i])

    def set_row(self, row):
        for i in range(len(self.headers)):
            self.content[self.headers[i]] = row[i]

    def show(self, qt_manager):
        gui_table = TableView(self.size[0], self.size[1], qt_manager.main_widget)
        gui_table.set_data(self.headers, self.content)
        qt_manager.main_layout.addWidget(gui_table)

        qt_manager.main_window.show()
        if qt_manager.app.exec() == 0:
            qt_manager.main_layout.removeWidget(gui_table)
            return


if __name__=="__main__":
    qt_mngr = QTManager()

    table = Table(["col1", "col2", "col3"], 0)
    table.add_row(['1','2','3'])
    table.add_row(['4','5','6'])
    table.add_row(['7','8','9'])
    print("start")
    table.show(qt_mngr)
    print("finnish")
