from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QGridLayout, QLineEdit, QApplication,
                             QMainWindow, QToolBar, QTextEdit, QDialog, QTabWidget, QScrollArea, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont, QIcon
from databases import DatabaseManager
import sys, winsound


def get_entry_list(db: DatabaseManager):
    raw_entries = db.fetch_entries()
    entry_list = []
    for entry in raw_entries:
        entry_list.append(entry[0])

    return entry_list


def get_max_index(db: DatabaseManager):
    max_index = len(get_entry_list(db))
    return max_index


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(600, 600)
        self.setWindowTitle('Cade Data Entry')
        icon = QIcon(r"C:\Users\jrod4\PycharmProjects\DataEntryProgram\images\app icon.png")
        self.setWindowIcon(icon)
# --------- TABS ------------------------------- #
        tabs = QTabWidget()
        tabs.addTab(TaskTab(), "Tasks")
        tabs.addTab(GratitudeTab(), "Gratitude")

        self.setCentralWidget(tabs)


class TemplateTab(QWidget):
    def __init__(self):
        super().__init__()
        main_style_sheet =   '''
            font-size: 24pt;
            font-style: Times New Roman
            '''

        layout = QGridLayout()

        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setWordWrap(True)
        self.display_label.setStyleSheet(main_style_sheet)

        self.enter_button = QPushButton("Enter")
        self.clear_button = QPushButton("Clear All Entries")
        self.select_clear_button = QPushButton("Clear Entry")
        self.entry_box = QLineEdit()

        scroll = QScrollArea()
        scroll.setWidget(self.display_label)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(200)


        layout.addWidget(self.enter_button, 1, 0)
        layout.addWidget(self.clear_button,1, 2)
        layout.addWidget(self.select_clear_button, 2, 0)
        layout.addWidget(self.entry_box, 1,1)
        layout.addWidget(scroll, 0, 1)

        self.setLayout(layout)

# ----------- FUNCTIONS ------------------------------------------------------------------ #
    def insert_entry(self, db: DatabaseManager):
        text = self.entry_box.text()

        if text.strip():
            db.insert_entry(text)
            self.entry_box.clear()
            self.display_label.setText(self.get_display_text(db))

    def get_display_text(self, db: DatabaseManager):
        entries = db.fetch_entries()
        entry_list = []
        count = 1
        for entry in entries:
            entry_list.append(f'{db.db_name} #{count}: ' + entry[0])
            count+=1
        display_text = ' \n '.join(entry_list)
        if not display_text:
            return f'No {db.db_name} set yet'
        return display_text

    def clear_entries(self, db: DatabaseManager):
        popup = PopupWindow()
        result = popup.exec()

        if result:
            db.clear_entries()
            self.display_label.setText(self.get_display_text(db))

    def single_entry_clear(self, db: DatabaseManager):
        popup = DeleteEntryWindow(db)
        result = popup.exec()
        if result:
            self.display_label.setText(self.get_display_text(db))


class TaskTab(TemplateTab):
    def __init__(self):
        super().__init__()

        self.task_db = DatabaseManager('Task')
        self.display_label.setText(self.get_display_text(self.task_db))

        self.entry_box.returnPressed.connect(lambda: self.insert_entry(self.task_db))
        self.enter_button.clicked.connect(lambda: self.insert_entry(self.task_db))
        self.select_clear_button.clicked.connect(lambda: self.single_entry_clear(self.task_db))

        self.clear_button.clicked.connect(lambda: self.clear_entries(self.task_db))


class GratitudeTab(TemplateTab):
    def __init__(self):
        super().__init__()

        self.gratitude_db = DatabaseManager('Gratitude')
        self.display_label.setText(self.get_display_text(self.gratitude_db))

        self.entry_box.returnPressed.connect(lambda: self.insert_entry(self.gratitude_db))
        self.enter_button.clicked.connect(lambda: self.insert_entry(self.gratitude_db))
        self.select_clear_button.clicked.connect(lambda: self.single_entry_clear(self.gratitude_db))

        self.clear_button.clicked.connect(lambda: self.clear_entries(self.gratitude_db))


class PopupWindow(QDialog):
    def __init__(self):
        super().__init__()

        main_style_sheet = '''
                    font-size: 24pt;
                    font-style: Times New Roman;
                    '''

        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        yes_button = QPushButton('Yes')
        no_button = QPushButton('No')
        self.prompt_label = QLabel("Are you sure you'd like to delete all entries?")
        self.setWindowTitle('Are You Sure?')

        self.prompt_label.setStyleSheet(main_style_sheet)

        layout = QGridLayout()
        layout.addWidget(yes_button, 1, 0)
        layout.addWidget(no_button, 1, 2)
        layout.addWidget(self.prompt_label, 0, 1)

        self.setLayout(layout)
        yes_button.clicked.connect(self.accept)
        no_button.clicked.connect(self.reject)

        print('no')


class DeleteEntryWindow(QDialog):
    def __init__(self, db: DatabaseManager):
        super().__init__()

        main_style_sheet = '''
                            font-size: 14pt;
                            font-style: Times New Roman;
                            '''
        self.resize(300, 200)
        welcome_label = QLabel("Please enter number of the entry you'd\nlike to delete:")
        self.entry_box = QSpinBox()
        enter_button = QPushButton("Enter")

        welcome_label.setStyleSheet(main_style_sheet)
        self.entry_box.setMaximum(get_max_index(db))

        layout = QGridLayout()
        layout.addWidget(welcome_label, 0, 1)
        layout.addWidget(self.entry_box, 1,0)
        layout.addWidget(enter_button, 1,2)

        self.setLayout(layout)

        enter_button.clicked.connect(lambda: self.single_entry_clear(db))

    def single_entry_clear(self, db: DatabaseManager):
        entry_id = self.entry_box.text()
        entry_list = get_entry_list(db)
        try:
            entry_id = int(entry_id)
        except ValueError:
            popup = ErrorPopUp()
            popup.exec()
            return
        popup = DeleteEntryPopUp(entry_id, db)
        result = popup.exec()
        entry_id-=1
        if entry_id < 0:
            print('too low')
            return
        target = entry_list[entry_id]
        sql_id = db.id_from_text(target)
        if result:
            db.delete_entry(sql_id[0])
            self.accept()

    def test_method(self):
        print('This is a test')


class DeleteEntryPopUp(PopupWindow):
    def __init__(self, id: int, db: DatabaseManager):
        super().__init__()

        self.prompt_label.setText(f'Are you sure you want to delete {db.db_name} #{id}?')

        yes_button = QPushButton('Yes')
        no_button = QPushButton('No')

        yes_button.clicked.connect(self.accept)
        no_button.clicked.connect(self.reject)


class ErrorPopUp(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(100,100)
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        error_message= QLabel('ERROR: INVALID INPUT.\nPLEASE ENTER A NUMBER')
        error_message.setAlignment(Qt.AlignmentFlag.AlignCenter)


        layout = QGridLayout()
        layout.addWidget(error_message, 0,0)

        self.setLayout(layout)

