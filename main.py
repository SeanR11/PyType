import json
import time
import random
import threading
from ui_manager import UIManager
from PyQt5.Qt import Qt, QFont,QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLabel


class Core(QMainWindow):
    def __init__(self, title, size):
        super().__init__()
        # Set window properties
        self.setFixedSize(*size)
        self.setWindowTitle(title)
        self.setMouseTracking(True)
        self.setWindowIcon(QIcon('assets/icon.png'))
        # Initialize UIManager for managing UI components
        self.ui = UIManager()
        # Initialize variables
        self.main_layout = None
        self.right_layout = None
        self.left_layout = None
        self.test_text_field = None
        self.example_test_field = None
        # Load tests data from JSON file
        self.tests = self.load_tests()
        self.example_test = None
        self.test_length = '1 minute'
        self.test_language = 'en'
        self.test_timer_thread = None
        self.test_timer_event = threading.Event()
        self.test_timer = 0
        self.test_timer_limit = 0
        self.test_timer_label = None
        self.result_grid_objects = [[0 for _ in range(3)] for _ in range(3)]
        # Load UI components
        self.load_ui()

    def load_tests(self):
        # Load tests data from JSON file
        with open('tests.json','r',encoding='utf-8') as test_file:
            return json.load(test_file)

    def load_ui(self):
        # Set up main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(self.main_layout)
        # Set up left layout
        self.left_layout = self.ui.create_layout(self.main_layout, 'v')
        self.load_left_layout(self.left_layout)
        # Set up right layout
        self.right_layout = self.ui.create_layout(self.main_layout, 'v')
        self.load_right_layout(self.right_layout)

    def load_left_layout(self,layout):
        # Load UI components for the left layout
        self.test_text_field = self.ui.create_textfield(layout,'Test text', 'Enter text', (20, 20, 20, 20))
        self.example_test_field = self.ui.create_textfield(layout, 'Modal text', 'Test text', (20, 20, 20, 20),
                                                           True)

    def load_right_layout(self,layout):
        # Load UI components for the right layout
        settings_layout = self.ui.create_layout(layout, 'v', stretch=5)
        self.ui.create_label(settings_layout, 'Test settings', align=Qt.AlignCenter, stretch=2)
        self.ui.create_radio_selection(settings_layout, ['1 minute', '3 minute', '5 minute'],
                                       button_action=self.set_test_length, layout_direction='h', layout_stretch=2)
        self.ui.create_radio_selection(settings_layout, ['en', 'he'], is_icon=True,
                                       button_action=self.set_test_language, layout_direction='h', layout_stretch=2)

        buttons_layout = self.ui.create_layout(settings_layout, 'h', stretch=1)
        buttons_layout.setContentsMargins(0, 30, 0, 50)
        self.ui.create_button(buttons_layout, 'start test', action=self.start_timer)
        self.ui.create_button(buttons_layout, 'reset test', action=self.reset_timer)

        self.test_timer_label = self.ui.create_label(layout, '00:00', size=24, align=Qt.AlignHCenter)
        self.ui.create_label(layout, 'Test results', align=Qt.AlignCenter)
        result_layout = self.ui.create_layout(layout, 'g', stretch=3)
        result_layout.setContentsMargins(0, 0, 50, 0)
        result_params = ['GW', 'GWPM', 'GWPS', 'NW', 'NWPM', 'NWPS', 'AP']
        result_params_tooltip = ['<h2>Gross Words</h2>This is the total number of words typed by the candidate',
                                 '<h2>Gross Words Per Min</h2>The total number of words typed in one minute.',
                                 '<h2>Gross Words Per Second</h2>The total number of words typed per second.',
                                 '<h2>Net Words</h2>The number of correct words typed.',
                                 '<h2>Net words Per Min</h2>The total number of Net Words typed in one minutes',
                                 '<h2>Net words Per Second</h2>The total number of Net Words typed per second.',
                                 '<h2>Accurate Percentage</h2>The percentage of correct words entered.']
        for row in range(3):
            for col in range(3):
                idx = row * 3 + col
                result_title = QLabel(result_params[idx] + ':', font=QFont('Arial', 12))
                result_title.setToolTip(result_params_tooltip[idx])

                self.result_grid_objects[row][col] = QLabel('0.000')
                self.result_grid_objects[row][col].setFont(QFont('Arial', 12))
                if idx == 6:
                    self.result_grid_objects[row][col].setText('0%')
                    result_layout.addWidget(result_title, row, col, 1, 3, alignment=Qt.AlignCenter)
                    result_layout.addWidget(self.result_grid_objects[row][col], row, col, 1, 2, alignment=Qt.AlignRight)
                    break
                else:
                    result_layout.addWidget(result_title, row, col, alignment=Qt.AlignCenter)
                    result_layout.addWidget(self.result_grid_objects[row][col], row, col, alignment=Qt.AlignRight)

    def set_test_length(self):
        # Set test length based on selected radio button
        self.test_length = self.sender().text()

    def set_test_language(self):
        # Set test language based on selected radio button
        self.test_language = self.sender().toolTip()

    def start_timer(self):
        # Start typing test
        if not self.test_timer_thread:
            if self.test_timer_event.is_set():
                # If test is reset, clear previous results and text
                self.test_timer_event.clear()
                self.test_text_field.setReadOnly(False)
                for row in range(3):
                    for col in range(3):
                        if 6 == row * 3 + col:
                            self.result_grid_objects[row][col].setText('0%')
                            break
                        self.result_grid_objects[row][col].setText('0.000')
            # Choose a random example test from loaded tests
            self.example_test = random.choice(self.tests[self.test_language][self.test_length])
            self.example_test_field.setText(self.example_test)
            self.test_text_field.setText('')
            # Start the test timer thread
            self.test_timer_thread = threading.Thread(target=self.timer_cycle)
            self.test_timer_limit = 60 * int(self.test_length.split(' ')[0])
            self.test_timer_thread.start()

    def reset_timer(self):
        # Reset the timer and test
        self.test_timer_event.set()
        self.test_timer_thread = None
        self.test_timer = 0
        self.test_timer_label.setText('00:00')

    def timer_cycle(self):
        # Timer cycle function to update timer label
        while not self.test_timer_event.is_set():
            time_left = self.test_timer_limit - self.test_timer
            time_gmt = time.gmtime(time_left)
            time_formatted = time.strftime('%M:%S', time_gmt)
            self.test_timer_label.setText(time_formatted)
            if time_left == 0:
                # If time is up, calculate typing speed and reset timer
                self.calculate_type_speed()
                self.reset_timer()
                break
            self.test_timer += 1
            time.sleep(1)

    def calculate_type_speed(self):
        # Calculate typing speed and display results
        test = self.test_text_field.toPlainText()
        example_test = self.example_test_field.toPlainText()
        test_time = int(self.test_length.split(' ')[0])
        gross_words = len(test.split(' '))
        gross_per_minute = gross_words / test_time
        gross_per_second = gross_words / test_time / 60
        net_words = sum(1 for idx, word in enumerate(test.split(' ')) if word == example_test.split(' ')[idx])
        net_per_minute = net_words / test_time
        net_per_second = net_words / test_time / 60
        accurate_percentage = net_per_minute*100/gross_per_minute if gross_per_minute != 0 else 0
        results = [gross_words,gross_per_minute,gross_per_second,net_words,net_per_minute,net_per_second,accurate_percentage]
        for idx, value in enumerate(results):
            if idx == 6:
                self.result_grid_objects[2][0].setText(f'{value:.0f} %')
            else:
                self.result_grid_objects[idx // 3][idx % 3].setText(f'{value:.3f}')
        self.test_text_field.setReadOnly(True)


if __name__ == '__main__':
    app = QApplication([])
    core = Core('PyType', (1000, 600))
    core.show()
    app.exec_()
