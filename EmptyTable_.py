""" import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QTableWidget(10, 6)
    window.setWindowTitle('My PyQt5 App')
    window.setGeometry(100, 100, 640, 480)

''' # Add some data to the table
    for i in range(10):
        for j in range(6):
            item = QTableWidgetItem(f'Row {i}, Column {j}')
            window.setItem(i, j, item)'''

window.show()
sys.exit(app.exec_()) """


import sys
from PyQt5.QtWidgets import QApplication, QWidget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('My PyQt5 App')
    window.setGeometry(100, 100, 640, 480)
    window.show()
    sys.exit(app.exec_())
