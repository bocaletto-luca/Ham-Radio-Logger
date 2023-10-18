# Nome Software: Ham Radio Logger
# Autore: Bocaletto Luca
# Sito Web: https://www.elektronoide.it
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
        # Imposta il titolo della finestra
        self.setWindowTitle('Logger Radioamatoriale')
        # Imposta le dimensioni della finestra
        self.setGeometry(100, 100, 800, 600)

        # Crea un widget centrale
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Crea un layout verticale per organizzare i widget
        self.layout = QVBoxLayout()

        # Add the title label and set its font size
        self.title_label = QLabel('Ham Radio Logger')
        font = QFont()
        font.setPointSize(20)  # Set font size to 20
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Crea etichette e campi di input per i dati
        self.call_label = QLabel('Indicativo di chiamata:')
        self.call_input = QLineEdit()
        self.call_input.setPlaceholderText('Es. IZ4XYZ')
        self.freq_label = QLabel('Frequenza:')
        self.freq_input = QLineEdit()
        self.freq_input.setPlaceholderText('Es. 144.800 MHz')
        self.date_label = QLabel('Data:')
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText('Es. 2023-01-15')
        self.time_label = QLabel('Ora:')
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText('Es. 14:30')
        self.power_label = QLabel('Potenza del segnale:')
        self.power_input = QLineEdit()
        self.power_input.setPlaceholderText('Es. 50 Watts')

        # Crea bottoni
        self.add_button = QPushButton('Aggiungi')
        self.update_button = QPushButton('Modifica')
        self.delete_button = QPushButton('Elimina')
        self.export_button = QPushButton('Esporta in CSV')

        # Crea una tabella per visualizzare i dati
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', 'Indicativo di chiamata', 'Frequenza', 'Data', 'Ora', 'Potenza del segnale'])
        self.table.horizontalHeader().setStretchLastSection(True)

        # Aggiungi i widget al layout
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

        # Imposta il layout del widget centrale
        self.central_widget.setLayout(self.layout)

        # Collega i bottoni alle funzioni corrispondenti
        self.add_button.clicked.connect(self.add_entry)
        self.update_button.clicked.connect(self.update_entry)
        self.delete_button.clicked.connect(self.delete_entry)
        self.export_button.clicked.connect(self.export_to_csv)

        # Connetti al database e crea la tabella 'log'
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

        # Carica i dati nella tabella
        self.update_entry_list()

    def update_entry_list(self):
        # Esegue una query per ottenere tutti i dati dalla tabella 'log'
        self.cursor.execute('SELECT * FROM log')
        data = self.cursor.fetchall()
        # Imposta il numero di righe nella tabella
        self.table.setRowCount(len(data))
        # Popola la tabella con i dati
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(item)))

    def add_entry(self):
        # Ottiene i dati dai campi di input
        call = self.call_input.text()
        freq = self.freq_input.text()
        date = self.date_input.text()
        time = self.time_input.text()
        power = self.power_input.text()
        # Esegue una query per inserire i dati nella tabella
        self.cursor.execute('INSERT INTO log (call_sign, frequency, date, time, signal_power) VALUES (?, ?, ?, ?, ?)', (call, freq, date, time, power))
        self.conn.commit()
        # Aggiorna la tabella e cancella i campi di input
        self.update_entry_list()
        self.clear_inputs()

    def update_entry(self):
        # Ottiene la riga selezionata nella tabella
        current_row = self.table.currentRow()
        if current_row == -1:
            return
        # Ottiene i dati dai campi di input
        call = self.call_input.text()
        freq = self.freq_input.text()
        date = self.date_input.text()
        time = self.time_input.text()
        power = self.power_input.text()
        # Ottiene l'ID dell'elemento selezionato
        entry_id = self.table.item(current_row, 0).text()
        # Esegue una query per aggiornare i dati
        self.cursor.execute('UPDATE log SET call_sign=?, frequency=?, date=?, time=?, signal_power=? WHERE id=?', (call, freq, date, time, power, entry_id))
        self.conn.commit()
        # Aggiorna la tabella e cancella i campi di input
        self.update_entry_list()
        self.clear_inputs()

    def delete_entry(self):
        # Ottiene la riga selezionata nella tabella
        current_row = self.table.currentRow()
        if current_row == -1:
            return
        # Ottiene l'ID dell'elemento selezionato
        entry_id = self.table.item(current_row, 0).text()
        # Esegue una query per eliminare l'elemento
        self.cursor.execute('DELETE FROM log WHERE id=?', (entry_id,))
        self.conn.commit()
        # Aggiorna la tabella
        self.update_entry_list()
        # Cancella i campi di input
        self.clear_inputs()

    def export_to_csv(self):
        # Apre un file CSV e scrive i dati dal database
        with open('radio_logger.csv', 'w') as f:
            self.cursor.execute('SELECT * FROM log')
            data = self.cursor.fetchall()
            headers = [description[0] for description in self.cursor.description]
            f.write(','.join(headers) + '\n')
            for row in data:
                f.write(','.join(map(str, row)) + '\n')

    def clear_inputs(self):
        # Cancella i campi di input
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
