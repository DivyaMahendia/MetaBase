import pyodbc
from PyQt5.QtWidgets import QApplication, QDialog, QFormLayout, QCalendarWidget, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QColor, QDesktopServices, QFont, QFontDatabase, QPalette
from PyQt5 import QtCore, QtSql, QtWidgets

# Define a global variable to store the username
logged_in_user = None

class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):   #initializes the GUI widgets
        super().__init__(parent)

        self.edit = QtWidgets.QLineEdit()
        self.combo = QtWidgets.QComboBox()
        self.table = QtWidgets.QTableWidget()
        self.button = QtWidgets.QPushButton("Delete")
        self.insert_button = QPushButton("Insert")
        self.calendar = QCalendarWidget()
        self.calendar.setWindowFlags(QtCore.Qt.Popup)
        self.calendar.setMaximumSize(400, 400)
        self.calendar.selectionChanged.connect(self.update_search_bar)

        grid = QtWidgets.QGridLayout(self)
        grid.addWidget(self.edit, 0, 0)
        grid.addWidget(self.combo, 0, 1)
        grid.addWidget(self.table, 1, 0, 1, 4)
        grid.addWidget(self.button, 0, 3)
        grid.addWidget(self.insert_button, 0, 2)

        self.connection = pyodbc.connect(
            "DRIVER={SQL Server Native Client 11.0};SERVER=DESKTOP-58LJL7D\SQLEXPRESS;DATABASE=app_db;Trusted_Connection=no;UID=Admin;PWD=Password#1234;"
        )
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM app_db.dbo.docs")
        data = cursor.fetchall()

        # Set the username of the logged-in user
        self.username = logged_in_user  


        grouped_data = {}
        for row in data:
            if row[2] not in grouped_data:
               grouped_data[row[2]] = []
            grouped_data[row[2]].append(row)
        for key in grouped_data:
            grouped_data[key] = sorted(grouped_data[key], key=lambda x: x[3])

        
        self.table.setColumnCount(len(data[0]))
        self.table.setRowCount(len(data))
        headers = [description[0] for description in cursor.description]
        self.table.setHorizontalHeaderLabels(headers)
        self.combo.clear()
        for i in range(self.table.columnCount()):
            self.combo.addItem(headers[i])


        row = 0
        for key in grouped_data:
            for row_data in grouped_data[key]:
                for col, cell in enumerate(row_data):
                    item = QTableWidgetItem(str(cell))
                    if col == 5:
                       item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                       item.setForeground(Qt.blue)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, item)
                row += 1

        # Handle link clicks
        self.table.cellDoubleClicked.connect(lambda row, col: QDesktopServices.openUrl(QUrl.fromLocalFile(self.table.item(row, col).text())))
        self.edit.textChanged.connect(self.filter_table)
        self.table.cellChanged.connect(self.update_database)
        self.button.clicked.connect(self.delete_rows)
        self.insert_button.clicked.connect(self.show_insert_dialog)
        self.edit.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.edit and event.type() == QtCore.QEvent.MouseButtonPress:
            if self.combo.currentText() == "date_time":
                combo_box_rect = self.combo.geometry()
                calendar_rect = self.calendar.geometry()
                calendar_rect.moveTopRight(combo_box_rect.bottomLeft())
                self.calendar.setGeometry(calendar_rect)
                self.calendar.show()
                return True
        return super().eventFilter(obj, event)
    
    def update_search_bar(self):
        date = self.calendar.selectedDate().toString("dd-MM-yyyy")
        self.edit.setText(date)
        self.filter_table(date)


    def filter_table(self, text):
        if text:
           filter_column = self.combo.currentIndex()

           for i in range(self.table.rowCount()):
               item = self.table.item(i, filter_column)
               if self.filter_row(item, text.lower()):
                   self.table.showRow(i)
               else:
                   self.table.hideRow(i)
        else:
            for i in range(self.table.rowCount()):
                self.table.showRow(i)

    def filter_row(self, item, text):
        return text.lower() in item.text().lower() or text in item.text()
    
    def update_database(self, row, column):
        # Get the new value of the cell
        new_value = self.table.item(row, column).text()

        # Get the primary key of the row
        primary_key = self.table.item(row, 0).text()

        # Get the name of the column that was edited
        column_name = self.table.horizontalHeaderItem(column).text()

        # Update the corresponding row in the database
        cursor = self.connection.cursor()
        cursor.execute(
            f"UPDATE dbo.docs SET {column_name} = ? WHERE id = ?",
            new_value,
            primary_key
        )
        self.connection.commit()

        # Log the change in the log table
        global logged_in_user
        username = logged_in_user
        action = f"Updated {column_name} to {new_value}"
        cursor.execute(f"INSERT INTO app_db.dbo.logs (username, row_id, action) VALUES (?, ?, ?)", username, primary_key, action)
        self.connection.commit()

        
           
    def delete_rows(self):
        selected_rows = []
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).isSelected():
                selected_rows.append(row)
        if selected_rows:
            id = [str(self.table.item(row, 0).text()) for row in selected_rows]
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Question)
            message_box.setText("Are you sure you want to delete these entries?")
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.setDefaultButton(QMessageBox.No)
            response = message_box.exec_()    
            if response == QMessageBox.Yes:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM app_db.dbo.docs WHERE id IN ({})".format(','.join(id)))
                for row in selected_rows[::-1]:
                    self.table.removeRow(row)
                self.connection.commit() 

                # Log the change in the log table
                global logged_in_user
                username = logged_in_user
                action = f"Deleted rows with ID {', '.join(id)}"
                cursor.execute(f"INSERT INTO app_db.dbo.logs (username,row_id, action) VALUES (?, NULL, ?)", username, action)
                self.connection.commit()

    def show_insert_dialog(self):
        dialog = InsertDialog(self)
        dialog.exec_()


class SignupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up the UI
        self.username_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.hint_label = QLabel("Hint:")
        self.hint_edit = QLineEdit()
        self.signup_button = QPushButton("Sign Up")

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow(self.username_label, self.username_edit)
        form_layout.addRow(self.password_label, self.password_edit)
        form_layout.addRow(self.hint_label, self.hint_edit)
        layout.addLayout(form_layout)
        layout.addWidget(self.signup_button)

        # Connect the button to the signup method
        self.signup_button.clicked.connect(self.signup)

        # Connect to the database
        self.connection = pyodbc.connect(
            "DRIVER={SQL Server Native Client 11.0};SERVER=DESKTOP-58LJL7D\SQLEXPRESS;DATABASE=app_db;Trusted_Connection=no;UID=Admin;PWD=Password#1234;"
        )

        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(255, 255, 255))
        self.setPalette(palette)

        # Set the font and color of the signup button
        font = QFont()
        font.setFamily("Cambria")
        font.setPointSize(10)
        self.username_label.setFont(font)
        self.username_edit.setFont(font)
        self.password_label.setFont(font)
        self.password_edit.setFont(font)
        self.hint_label.setFont(font)
        self.hint_edit.setFont(font)
        self.signup_button.setFont(font)
        self.signup_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px;")

    
    def signup(self):
        # Get the values from the fields
        username = self.username_edit.text()
        password = self.password_edit.text()
        hint = self.hint_edit.text()

        # Validate the input
        if not username or not password or not hint:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return

        # Check if the username already exists
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM app_db.dbo.userr WHERE username = ?", username)
        data = cursor.fetchone()
        if data is not None:
            QMessageBox.warning(self, "Error", "Username already exists")
            return

        # Create a new user in the user-level authentication table
        cursor.execute("INSERT INTO app_db.dbo.userr (username, password, hint) VALUES (?, ?, ?)", username, password, hint)
        self.connection.commit()

        QMessageBox.information(self, "Success", "User created successfully")

        # Close the dialog
        self.accept()



class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up the UI
        self.username_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login")
        self.signup_button = QPushButton("Sign Up")
        


        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow(self.username_label, self.username_edit)
        form_layout.addRow(self.password_label, self.password_edit)
        layout.addLayout(form_layout)
        layout.addWidget(self.login_button)
        layout.addWidget(self.signup_button)
        

        # Connect the buttons to their respective methods
        self.signup_button.clicked.connect(self.show_signup_dialog)
        self.login_button.clicked.connect(self.login)

        # Connect to the database
        self.connection = pyodbc.connect(
            "DRIVER={SQL Server Native Client 11.0};SERVER=DESKTOP-58LJL7D\SQLEXPRESS;DATABASE=app_db;Trusted_Connection=no;UID=Admin;PWD=Password#1234;"
        )
        # Set the background color of the dialog
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(255, 255, 255))
        self.setPalette(palette)

        # Set the font and color of the login and signup buttons
        font = QFont()
        font.setFamily("Cambria")
        font.setPointSize(10)
        self.username_label.setFont(font)
        self.username_edit.setFont(font)
        self.password_label.setFont(font)
        self.password_edit.setFont(font)
        self.login_button.setFont(font)
        self.login_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; padding: 5px 10px;")
        self.signup_button.setFont(font)
        self.signup_button.setStyleSheet("background-color: #008CBA; color: white; border-radius: 5px; padding: 5px 10px;")
        
        
        
          
    def show_signup_dialog(self):
        # Create and show the signup dialog
        signup_dialog = SignupDialog(self)
        signup_dialog.exec_()

    def login(self):
        # Get the username and password from the fields
        username = self.username_edit.text()
        password = self.password_edit.text()

        # Check if the username exists in the database
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM app_db.dbo.userr WHERE username = ?", username)
        data = cursor.fetchone()
        if data is None:
            QMessageBox.warning(self, "Error", "Invalid username")
            return

        # Check if the password is correct
        cursor.execute("SELECT * FROM app_db.dbo.userr WHERE username = ? AND password = ?", username, password)
        data = cursor.fetchone()
        if data is None:
            hint = cursor.execute("SELECT hint FROM app_db.dbo.userr WHERE username = ?", username).fetchone()[0]
            QMessageBox.warning(self, "Error", f"Invalid password. Hint: {hint}")
            return

        # If the credentials are valid, set the global variable and close the login window
        global logged_in_user
        logged_in_user = username
        self.accept()


class InsertDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up the UI
        self.country_label = QLabel("Country:")
        self.country_edit = QLineEdit()
        self.sn_label = QLabel("sn:")
        self.sn_edit = QLineEdit()
        self.datetime_label = QLabel("Date/Time:")
        self.datetime_edit = QLineEdit()
        self.docname_label = QLabel("Doc Name:")
        self.docname_edit = QLineEdit()
        self.link_label = QLabel("Link:")
        self.link_edit = QLineEdit()
        self.add_button = QPushButton("Add")
        self.cancel_button = QPushButton("Cancel")
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow(self.country_label, self.country_edit)
        form_layout.addRow(self.sn_label, self.sn_edit)
        form_layout.addRow(self.datetime_label, self.datetime_edit)
        form_layout.addRow(self.docname_label, self.docname_edit)
        form_layout.addRow(self.link_label, self.link_edit)
        layout.addLayout(form_layout)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Connect the buttons to the add_row and close methods
        self.add_button.clicked.connect(self.add_row)
        self.cancel_button.clicked.connect(self.close)

        # Connect to the database
        self.connection = pyodbc.connect(
            "DRIVER={SQL Server Native Client 11.0};SERVER=DESKTOP-58LJL7D\SQLEXPRESS;DATABASE=app_db;Trusted_Connection=no;UID=Admin;PWD=Password#1234;"
        )

    def add_row(self):
        # Get the values from the line edits
        country = self.country_edit.text()
        sn = self.sn_edit.text()
        datetime = self.datetime_edit.text()
        docname = self.docname_edit.text()
        link = self.link_edit.text()

        # Create a cursor object and execute the INSERT query
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO app_db.dbo.docs (country, sn, date_time, docname, link) VALUES (?, ?, ?, ?, ?)", country, sn, datetime, docname, link)
        self.connection.commit()

        # Clear the line edits and close the dialog
        self.country_edit.clear()
        self.sn_edit.clear()
        self.datetime_edit.clear()
        self.docname_edit.clear()
        self.link_edit.clear()
        self.close()

        global logged_in_user
        username = logged_in_user
        cursor.execute(f"SELECT MAX(id) FROM app_db.dbo.docs")
        primary_key = cursor.fetchone()[0]
        action = f"Inserted row with ID {primary_key}"
        cursor.execute(f"INSERT INTO app_db.dbo.logs (username, row_id, action) VALUES (?, ?, ?)", username, primary_key, action)
        self.connection.commit()

def main():
    import sys

    app = QApplication(sys.argv)

    
    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
 
        ex = Widget()
        ex.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()