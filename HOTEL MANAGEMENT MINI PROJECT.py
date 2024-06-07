import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QComboBox, QGridLayout, QTableWidgetItem, QTableWidget
from PyQt5.QtCore import Qt

class HotelManagementApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hotel Management System")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Database connection
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="@Vicky2005",
            database="vicky"
        )
        self.cursor = self.db.cursor()

        # User details form
        self.name_label = QLabel("Name:")
        self.name_entry = QLineEdit()
        self.email_label = QLabel("Email:")
        self.email_entry = QLineEdit()
        self.phone_label = QLabel("Phone:")
        self.phone_entry = QLineEdit()

        # Room form
        self.room_id_label = QLabel("Room ID:")
        self.room_id_combo = QComboBox()  # Combo box for room IDs
        self.room_id_combo.currentIndexChanged.connect(self.display_room_details)  # Add event listener
        self.room_type_label = QLabel("Room Type:")
        self.room_type_display = QLabel()
        self.room_price_label = QLabel("Room Price:")
        self.room_price_display = QLabel()

        # Add guest button
        self.add_guest_button = QPushButton("Add Guest")
        self.add_guest_button.clicked.connect(self.add_guest)
        self.add_guest_button.setStyleSheet("background-color: #4CAF50; color: black; font-weight: bold;")

        # Rooms list
        self.rooms_table = QTableWidget()
        self.rooms_table.setColumnCount(4)
        self.rooms_table.setHorizontalHeaderLabels(["Room ID", "Room Type", "Price", "Current Occupant"])
        self.rooms_table.setStyleSheet("background-color: white;")

        # Layout setup
        user_form_layout = QGridLayout()
        user_form_layout.addWidget(self.name_label, 0, 0)
        user_form_layout.addWidget(self.name_entry, 0, 1)
        user_form_layout.addWidget(self.email_label, 1, 0)
        user_form_layout.addWidget(self.email_entry, 1, 1)
        user_form_layout.addWidget(self.phone_label, 2, 0)
        user_form_layout.addWidget(self.phone_entry, 2, 1)

        room_form_layout = QVBoxLayout()
        room_form_layout.addWidget(self.room_id_label)
        room_form_layout.addWidget(self.room_id_combo)
        room_form_layout.addWidget(self.room_type_label)
        room_form_layout.addWidget(self.room_type_display)
        room_form_layout.addWidget(self.room_price_label)
        room_form_layout.addWidget(self.room_price_display)

        main_layout = QVBoxLayout()
        main_layout.addLayout(user_form_layout)
        main_layout.addLayout(room_form_layout)
        main_layout.addWidget(self.add_guest_button)
        main_layout.addWidget(self.rooms_table)

        self.setLayout(main_layout)

        # Load data
        self.load_room_ids()
        self.load_rooms_data()

    def display_room_details(self):
        room_id = self.room_id_combo.currentText()
        if room_id:
            try:
                # Fetch room details from the database
                sql = "SELECT room_type, price FROM rooms WHERE room_id = %s"
                self.cursor.execute(sql, (room_id,))
                result = self.cursor.fetchone()
                if result:
                    room_type, price = result
                    self.room_type_display.setText(room_type)
                    self.room_price_display.setText(f"${price:.2f}")
                else:
                    self.room_type_display.setText("")
                    self.room_price_display.setText("")
            except mysql.connector.Error as err:
                QMessageBox.warning(self, "Error", f"Error loading room details: {err}")

    def add_guest(self):
        room_id = self.room_id_combo.currentText()
        name = self.name_entry.text()
        email = self.email_entry.text()
        phone = self.phone_entry.text()

        try:
            # Add guest to the database
            sql_guest = "INSERT INTO guests (name, email, phone) VALUES (%s, %s, %s)"
            val_guest = (name, email, phone)
            self.cursor.execute(sql_guest, val_guest)
            self.db.commit()

            # Update room with guest details
            sql_update_room = "UPDATE rooms SET current_occupant = %s, availability_status = FALSE WHERE room_id = %s"
            val_update_room = (name, room_id)
            self.cursor.execute(sql_update_room, val_update_room)
            self.db.commit()

            QMessageBox.information(self, "Success", "Guest added successfully!")
            self.load_room_ids()  # Refresh room IDs after updating availability
            self.load_rooms_data()  # Refresh rooms table data
        except mysql.connector.Error as err:
            QMessageBox.warning(self, "Error", f"Error adding guest: {err}")

    def load_room_ids(self):
        self.room_id_combo.clear()
        try:
            self.cursor.execute("SELECT room_id FROM rooms WHERE availability_status = TRUE")
            rooms = self.cursor.fetchall()
            for room in rooms:
                self.room_id_combo.addItem(str(room[0]))
        except mysql.connector.Error as err:
            QMessageBox.warning(self, "Error", f"Error loading room IDs: {err}")

    def load_rooms_data(self):
        self.rooms_table.setRowCount(0)
        try:
            self.cursor.execute("SELECT room_id, room_type, price, current_occupant FROM rooms")
            rooms_data = self.cursor.fetchall()
            for row_index, room_data in enumerate(rooms_data):
                self.rooms_table.insertRow(row_index)
                for column_index, data in enumerate(room_data):
                    item = QTableWidgetItem(str(data))
                    self.rooms_table.setItem(row_index, column_index, item)
        except mysql.connector.Error as err:
            QMessageBox.warning(self, "Error", f"Error loading rooms data: {err}")

    def closeEvent(self, event):
        self.cursor.close()
        self.db.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HotelManagementApp()
    window.show()
    sys.exit(app.exec_())
