# Software Name: Ham Radio Logger
# Author: Bocaletto Luca
# Web Site: https://www.elektronoide.it
import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class HamRadioLogger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set the window title
        self.setWindowTitle('Ham Radio Logger')
        # Set the window dimensions
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a vertical layout to organize the widgets
        self.layout = QVBoxLayout()

        # Add the title label and set its font size
        self.title_label = QLabel('Ham Radio Logger')
        font = QFont()
        font.setPointSize(20)  # Set font size to 20
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Create labels and input fields for data
        self.call_label = QLabel('Call Sign:')
        self.call_input = QLineEdit()
        self.call_input.setPlaceholderText('E.g., IZ4XYZ')
        self.freq_label = QLabel('Frequency:')
        self.freq_input = QLineEdit()
        self.freq_input.setPlaceholderText('E.g., 144.800 MHz')
        self.date_label = QLabel('Date:')
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText('E.g., 2023-01-15')
        self.time_label = QLabel('Time:')
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText('E.g., 14:30')
        self.power_label = QLabel('Signal Power:')
        self.power_input = QLineEdit()
        self.power_input.setPlaceholderText('E.g., 50 Watts')

        # Create buttons
        self.add_button = QPushButton('Add')
        self.update_button = QPushButton('Update')
        self.delete_button = QPushButton('Delete')
        self.export_button = QPushButton('Export to CSV')

        # Create a table to display the data
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', 'Call Sign', 'Frequency', 'Date', 'Time', 'Signal Power'])
        self.table.horizontalHeader().setStretchLastSection(True)

        # Add the widgets to the layout
        self.layout.addWidget(self.call_label)
        self.layout.addWidget(self.call_input)
        self.layout.addWidget(self.freq_label)
        self.layout.addWidget(self.freq_input)
        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.date_input)
        self.layout.addWidget(self.time_label)
        self.layout.addWidget(self.time_input)
        self.layout.addWidget(self.power_label)
        self.layout.addWidget(self.power_input)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.update_button)
        self.layout.addWidget(self.delete_button)
        self.layout.addWidget(self.export_button)
        self.layout.addWidget(self.table)

        # Set the layout of the central widget
        self.central_widget.setLayout(self.layout)

        # Connect buttons to their respective functions
        self.add_button.clicked.connect(self.add_entry)
        self.update_button.clicked.connect(self.update_entry)
        self.delete_button.clicked.connect(self.delete_entry)
        self.export_button.clicked.connect(self.export_to_csv)

        # Connect to the database and create the 'log' table
        self.conn = sqlite3.connect('radio_logger.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS log (
                            id INTEGER PRIMARY KEY,
                            call_sign TEXT,
                            frequency TEXT,
                            date TEXT,
                            time TEXT,
                            signal_power TEXT)''')
        self.conn.commit()

        # Load data into the table
        self.update_entry_list()

    def update_entry_list(self):
        # Execute a query to retrieve all data from the 'log' table
        self.cursor.execute('SELECT * FROM log')
        data = self.cursor.fetchall()
        # Set the number of rows in the table
        self.table.setRowCount(len(data))
        # Populate the table with data
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(item)))

    def add_entry(self):
        # Get data from the input fields
        call = self.call_input.text()
        freq = self.freq_input.text()
        date = self.date_input.text()
        time = self.time_input.text()
        power = self.power_input.text()
        # Execute a query to insert data into the table
        self.cursor.execute('INSERT INTO log (call_sign, frequency, date, time, signal_power) VALUES (?, ?, ?, ?, ?)', (call, freq, date, time, power))
        self.conn.commit()
        # Update the table and clear the input fields
        self.update_entry_list()
        self.clear_inputs()

    def update_entry(self):
        # Get the selected row in the table
        current_row = self.table.currentRow()
        if current_row == -1:
            return
        # Get data from the input fields
        call = self.call_input.text()
        freq = self.freq_input.text()
        date = self.date_input.text()
        time = self.time_input.text()
        power = self.power_input.text()
        # Get the ID of the selected item
        entry_id = self.table.item(current_row, 0).text()
        # Execute a query to update the data
        self.cursor.execute('UPDATE log SET call_sign=?, frequency=?, date=?, time=?, signal_power=? WHERE id=?', (call, freq, date, time, power, entry_id))
        self.conn.commit()
        # Update the table and clear the input fields
        self.update_entry_list()
        self.clear_inputs()

    def delete_entry(self):
        # Get the selected row in the table
        current_row = self.table.currentRow()
        if current_row == -1:
            return
        # Get the ID of the selected item
        entry_id = self.table.item(current_row, 0).text()
        # Execute a query to delete the item
        self.cursor.execute('DELETE FROM log WHERE id=?', (entry_id,))
        self.conn.commit()
        # Update the table
        self.update_entry_list()
        # Clear the input fields
        self.clear_inputs()

    def export_to_csv(self):
        # Open a CSV file and write data from the database
        with open('radio_logger.csv', 'w') as f:
            self.cursor.execute('SELECT * FROM log')
            data = self.cursor.fetchall()
            headers = [description[0] for description in self.cursor.description]
            f.write(','.join(headers) + '\n')
            for row in data:
                f.write(','.join(map(str, row)) + '\n')

    def clear_inputs(self):
        # Clear the input fields
        self.call_input.clear()
        self.freq_input.clear()
        self.date_input.clear()
        self.time_input.clear()
        self.power_input.clear()

def main():
    app = QApplication(sys.argv)
    ex = HamRadioLogger()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
