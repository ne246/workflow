from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QFrame, QTabWidget, QVBoxLayout, QLabel, QComboBox, 
                             QLineEdit, QPushButton, QMessageBox, QTextEdit,
                             QGridLayout, QTimeEdit, QCheckBox, QScrollArea)
from PyQt5.QtCore import Qt, QTime
from twilio.rest import Client  
import requests
from datetime import datetime, date, timezone  
import calendar
import sys
import json
import os

class Task:
    def __init__(self, description, time, is_permanent=False, completed=False):
        self.description = description
        self.time = time
        self.is_permanent = is_permanent
        self.completed = completed
        self.day_task_layout = None
        self.day_task_widget = None
        self.tasks = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
     

    def to_dict(self):
        return {
            'description': self.description,
            'time': self.time,
            'is_permanent': self.is_permanent,
            'completed': self.completed
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            description=data['description'],
            time=data['time'],
            is_permanent=data['is_permanent'],
            completed=data['completed']
        )

class CustomTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.day_task_layout = None
        self.day_task_widget = None
        self.tasks = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}

        today = date.today()
        date_numeric = today.strftime("%m/%d/%Y")
        date_spelled = today.strftime("%B %d, %Y")
        self.date_label = QLabel(f"{date_numeric} ({date_spelled})")
        self.date_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 10pt;
                padding: 8px 20px;
            }
        """)
        self.setCornerWidget(self.date_label, Qt.TopRightCorner)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.day_task_layout = None
        self.day_task_widget = None
        self.tasks = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
        self.load_tasks()
        self.setWindowTitle("WorkFlow")
        self.tabs = CustomTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Initialize task storage
        self.tasks = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
        self.load_tasks()

        self.setStyleSheet("""
            QMainWindow {
                background-color: black;
            }
            QTabWidget::pane {
                border: 1px solid white;
                background-color: black;
            }
            QTabWidget::tab-bar {
                left: 0px;
            }
            QTabBar::tab {
                background-color: #333333;
                color: white;
                padding: 8px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #90d5ff;
                border: 1px solid white;
            }
        """)
        self.setMinimumSize(2560, 872)

        self.create_tabs()

    def create_tabs(self):
        self.edit_tab = QWidget()
        self.week_tab = QWidget()
        self.day_tab = QWidget()

        self.tabs.addTab(self.edit_tab, "Edit")
        self.tabs.addTab(self.week_tab, "Week")
        self.tabs.addTab(self.day_tab, "Day")
        self.tabs.setCurrentIndex(1)

        self.add_content_to_edit_tab()
        self.add_content_to_week_tab()
        self.add_content_to_day_tab()

    def add_content_to_edit_tab(self):
        layout = QHBoxLayout(self.edit_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Task Input Container
        input_container = QWidget()
        input_container.setStyleSheet("background-color: white; border: 2px solid black;")
        input_container.setMinimumWidth(1280)
        input_layout = QVBoxLayout(input_container)

        # Header
        header = QLabel("Add, Edit, Remove Tasks")
        header.setStyleSheet("""
            QLabel {
                color: black;
                background-color: white;
                padding: 5px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 10pt;  /* Changed from 12pt to 10pt */
                font-weight: bold;
            }
        """)
        input_layout.addWidget(header)

        # Task input fields
        input_grid = QGridLayout()
        
        # Day selection
        self.day_combo = QComboBox()
        self.day_combo.addItems(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        self.day_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid black;
                background: white;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
        """)
        input_grid.addWidget(QLabel("Day:"), 0, 0)
        input_grid.addWidget(self.day_combo, 0, 1)

        # Time input
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setDisplayFormat("h:mm AP")  # Changed to 12-hour format with AM/PM
        self.time_edit.setStyleSheet("""
            QTimeEdit {
                padding: 5px;
                border: 1px solid black;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
        """)
        input_grid.addWidget(QLabel("Time:"), 1, 0)
        input_grid.addWidget(self.time_edit, 1, 1)

        # Task description
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter task description")
        self.task_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid black;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
        """)
        input_grid.addWidget(QLabel("Task:"), 2, 0)
        input_grid.addWidget(self.task_input, 2, 1)

        # Permanent checkbox
        self.permanent_check = QCheckBox("Permanent Task")
        self.permanent_check.setStyleSheet("""
            QCheckBox {
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
        """)
        input_grid.addWidget(self.permanent_check, 3, 0, 1, 2)

        input_layout.addLayout(input_grid)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Task")
        self.edit_button = QPushButton("Edit")
        self.remove_button = QPushButton("Remove Selected")
        self.clear_button = QPushButton("Clear Completed")

        for button in [self.add_button, self.edit_button, self.remove_button, self.clear_button]:
            button.setStyleSheet("""
                QPushButton {
                    padding: 8px 20px;
                    background-color: #333333;
                    color: white;
                    border: none;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                }
                QPushButton:hover {
                    background-color: #90d5ff;
                }
            """)
            button_layout.addWidget(button)

        input_layout.addLayout(button_layout)

        # Task List Container
        list_container = QWidget()
        list_container.setStyleSheet("background-color: white; border: 2px solid black;")
        list_container.setMinimumWidth(1280)
        list_layout = QVBoxLayout(list_container)

        # Tasks header
        tasks_header = QLabel("Current Tasks")
        tasks_header.setStyleSheet("""
            QLabel {
                color: black;
                background-color: white;
                padding: 5px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 12pt;
                font-weight: bold;
            }
        """)
        list_layout.addWidget(tasks_header)

        # Create scroll area for tasks
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: white; border: none;")
        
        self.task_list_widget = QWidget()
        self.task_list_layout = QVBoxLayout(self.task_list_widget)
        scroll.setWidget(self.task_list_widget)
        list_layout.addWidget(scroll)

        # Add containers to main layout
        layout.addWidget(input_container)
        layout.addWidget(list_container)

        # Connect buttons
        self.add_button.clicked.connect(self.add_task)
        self.edit_button.clicked.connect(self.edit_task)
        self.remove_button.clicked.connect(self.remove_task)
        self.clear_button.clicked.connect(self.clear_completed_tasks)
        self.day_combo.currentTextChanged.connect(self.update_task_display)

        # Initial update
        self.update_task_display()

    def add_task(self):
        day = self.day_combo.currentText()
        time = self.time_edit.time().toString("hh:mm AP")  # Changed to 12-hour format
        description = self.task_input.text().strip()
        is_permanent = self.permanent_check.isChecked()

        if description:
            new_task = Task(description, time, is_permanent)
            self.tasks[day].append(new_task)
            self.save_tasks()
            self.update_task_display()
            self.update_week_view()
            self.update_todays_tasks()  # Update today's tasks
            self.task_input.clear()
            self.log_activity(f"Added task to {day}: {description}")
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a task description.")

    def edit_task(self):
        day = self.day_combo.currentText()
        selected_task = self.get_selected_task()

        if selected_task:
            # Load the selected task's details into the input fields
            time_obj = datetime.strptime(selected_task.time, "%I:%M %p")
            self.time_edit.setTime(QTime(time_obj.hour, time_obj.minute))
            self.task_input.setText(selected_task.description)
            self.permanent_check.setChecked(selected_task.is_permanent)

            # Remove the old task and allow the user to re-add or update it
            self.tasks[day].remove(selected_task)
            self.update_task_display()
            self.update_todays_tasks()
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a task to edit.")


    def remove_task(self):
        day = self.day_combo.currentText()
        selected_task = self.get_selected_task()
        if selected_task:
            self.tasks[day].remove(selected_task)
            self.save_tasks()
            self.update_task_display()
            self.update_week_view()
            self.update_todays_tasks()  # Update today's tasks
            self.log_activity(f"Removed task from {day}: {selected_task.description}")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a task to remove.")

    def clear_completed_tasks(self):
        for day in self.tasks:
            self.tasks[day] = [task for task in self.tasks[day] if not task.completed]
        self.save_tasks()
        self.update_task_display()
        self.update_week_view()
        self.log_activity("Cleared completed tasks")

    def get_selected_task(self):
        day = self.day_combo.currentText()
        for i in range(self.task_list_layout.count()):
            widget = self.task_list_layout.itemAt(i).widget()
            if widget:
                checkbox = widget.layout().itemAt(0).widget()
                if checkbox.isChecked():
                    return self.tasks[day][i]
        return None

    def update_task_display(self):
        while self.task_list_layout.count():
            widget = self.task_list_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        selected_day = self.day_combo.currentText()
        for task in self.tasks[selected_day]:
            task_widget = QWidget()
            task_layout = QHBoxLayout(task_widget)
            
            checkbox = QCheckBox()
            checkbox.setChecked(task.completed)
            checkbox.stateChanged.connect(lambda state, t=task: self.toggle_task_completion(t, state))
            
            label = QLabel(f"{task.time} - {task.description}")
            label.setStyleSheet("""
                QLabel {
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    %s
                }
            """ % ("color: #800080;" if task.is_permanent else ""))  # Changed to purple (#800080)
            
            task_layout.addWidget(checkbox)
            task_layout.addWidget(label)
            self.task_list_layout.addWidget(task_widget)


    def toggle_task_completion(self, task, state):
        task.completed = bool(state)
        self.save_tasks()
        self.update_week_view()

    def add_content_to_week_tab(self):
        layout = QHBoxLayout(self.week_tab)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        days = ['Saturday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Sunday']
        self.day_layouts = {}  # Store layouts for later updates

        for day in days:
            container = QWidget()
            container.setStyleSheet("background-color: white; ")
            container.setFixedSize(360, 872)  # Set fixed size for all day boxes

            box_layout = QVBoxLayout(container)
            box_layout.setSpacing(5)
            box_layout.setContentsMargins(5, 5, 5, 5)

            # Day label
            day_label = QLabel(day)
            day_label.setAlignment(Qt.AlignCenter)
        
            
            my_date = date.today()
            if day != calendar.day_name[my_date.weekday()]:
                day_label.setStyleSheet("""
                    QLabel {
                        color: black;
                        background-color: white;
                        padding: 5px;
                        font-family: 'Segoe UI', 'Arial', sans-serif;
                        font-size: 12pt;
                        font-weight: bold;
                    }
                """)
            else:
                day_label.setStyleSheet("""
                    QLabel {
                        color: #90d5ff;
                        background-color: white;
                        padding: 5px;
                        font-family: 'Segoe UI', 'Arial', sans-serif;
                        font-size: 12pt;
                        font-weight: bold;
                        text-decoration: underline;
                    }
                """)
            box_layout.addWidget(day_label)

            # Create scroll area for tasks
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("background-color: white; border: none;")
            
            task_widget = QWidget()
            task_layout = QVBoxLayout(task_widget)
            scroll.setWidget(task_widget)
            
            self.day_layouts[day] = task_layout
            box_layout.addWidget(scroll)
            
            layout.addWidget(container)

        self.update_week_view()

    def update_week_view(self):
         for day, layout in self.day_layouts.items():
            while layout.count():
                widget = layout.takeAt(0).widget()
                if widget:
                    widget.deleteLater()

            for task in sorted(self.tasks[day], key=lambda x: datetime.strptime(x.time, "%I:%M %p")):
                task_label = QLabel(f"{task.time}: {task.description}")
                task_label.setStyleSheet(f"""
                    QLabel {{
                        font-family: 'Segoe UI', 'Arial', sans-serif;
                        padding: 2px;
                        {
                            'text-decoration: line-through;' if task.completed else 
                            'color: #800080;' if task.is_permanent else ''  # Changed to purple
                        }
                    }}
                """)
                layout.addWidget(task_label)
                task_label.setTextInteractionFlags(Qt.TextSelectableByMouse)


            layout.addStretch()

    def add_content_to_day_tab(self):
        layout = QHBoxLayout(self.day_tab)

        # First container: Weather info and today's tasks
        container1 = QWidget()
        container1.setStyleSheet("background-color: white; border: 2px solid black;")
        container1.setMinimumWidth(640)
        container1_layout = QVBoxLayout(container1)

        # Weather info
        weather_title = QLabel("Current Weather in Anaheim")
        weather_title.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                padding: 5px;
            }
        """)

        container1_layout.addWidget(weather_title)

        current_temp_label = QLabel("Fetching weather data...")
        container1_layout.addWidget(current_temp_label)

        # Update the weather information
        self.update_weather_info(current_temp_label)

        # Task section
        task_section_label = QLabel("Today's Tasks:")
        task_section_label.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                font-weight: bold;
                padding: 5px;
            }
        """)
        container1_layout.addWidget(task_section_label)

        # Scrollable area for today's tasks
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.day_task_widget = QWidget()
        self.day_task_layout = QVBoxLayout(self.day_task_widget)
        scroll.setWidget(self.day_task_widget)
        container1_layout.addWidget(scroll)

        # Update today's tasks initially
        self.update_todays_tasks()

        layout.addWidget(container1)

        # Second container: Send message section
        container2 = QWidget()
        container2.setStyleSheet("background-color: white; border: 2px solid black;")
        container2.setMinimumWidth(640)
        container2_layout = QVBoxLayout(container2)

        label = QLabel("Send a Message to Your Phone")
        label.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                font-weight: bold;
                padding: 5px;
            }
        """)
        container2_layout.addWidget(label)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter your message here")
        container2_layout.addWidget(self.message_input)

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        container2_layout.addWidget(send_button)

        layout.addWidget(container2)

    def update_weather_info(self, label):
        try:
            city = ''
            api_key = ''
            base_url = 'https://api.openweathermap.org/data/2.5/weather'
            response = requests.get(f"{base_url}?q={city}&appid={api_key}").json()

            # Extract main temperature details
            temp_kelvin = response['main']['temp']
            temp_fahrenheit = (temp_kelvin - 273.15) * 9/5 + 32

            temp_max_kelvin = response['main']['temp_max']
            temp_max_fahrenheit = (temp_max_kelvin - 273.15) * 9/5 + 32

            temp_min_kelvin = response['main']['temp_min']
            temp_min_fahrenheit = (temp_min_kelvin - 273.15) * 9/5 + 32

            # Extract weather description
            description = response['weather'][0]['description']

            # Extract wind speed
            wind_speed = response['wind']['speed']

            # Extract sunrise and sunset times
            sunrise_timestamp = response['sys']['sunrise']
            sunset_timestamp = response['sys']['sunset']

            # Convert timestamps to readable times
            sunrise_time = datetime.fromtimestamp(sunrise_timestamp).strftime('%I:%M %p')
            sunset_time = datetime.fromtimestamp(sunset_timestamp).strftime('%I:%M %p')

            # Update the label text with the additional information
            label.setText(
                f"Current Temperature: {temp_fahrenheit:.1f}°F ({description.capitalize()})\n"
                f"High: {temp_max_fahrenheit:.1f}°F | Low: {temp_min_fahrenheit:.1f}°F\n"
                f"Wind Speed: {wind_speed} m/s\n"
                f"Sunrise: {sunrise_time} | Sunset: {sunset_time}"
            )
        except Exception:
            label.setText("Unable to fetch weather data.")
            


    def update_todays_tasks(self):
        # Clear the current tasks in the Day Tab
        while self.day_task_layout.count():
            widget = self.day_task_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        today = calendar.day_name[date.today().weekday()]
        for task in self.tasks[today]:
            task_label = QLabel(f"{task.time} - {task.description}")
            task_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.day_task_layout.addWidget(task_label)

        self.day_task_layout.addStretch()

    def send_message(self):
        message = self.message_input.toPlainText().strip()
        if message:
            try:
                account_sid = ''
                auth_token = ''
                client = Client(account_sid, auth_token)
                client.messages.create(
                    body=message,
                    from_='',
                    to=''
                )
                QMessageBox.information(self, "Message Sent", "Your message has been sent successfully!")
                self.message_input.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to send message: {e}")
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a message before sending.")

    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as file:
                tasks_dict = json.load(file)
                self.tasks = {day: [Task.from_dict(data) for data in tasks] for day, tasks in tasks_dict.items()}
        except FileNotFoundError:
            pass

    def save_tasks(self):
        tasks_dict = {day: [task.to_dict() for task in tasks] for day, tasks in self.tasks.items()}
        with open('tasks.json', 'w') as file:
            json.dump(tasks_dict, file)
    
    def log_activity(self, activity):
        with open('activity_log.txt', 'a') as file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"[{timestamp}] {activity}\n")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())