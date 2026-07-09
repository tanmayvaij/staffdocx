import os
import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QTextEdit, QPushButton, QListWidget, QFormLayout, 
    QMessageBox, QFileDialog, QSplitter, QDateEdit, QGraphicsDropShadowEffect,
    QFrame, QScrollArea, QCheckBox, QComboBox, QGridLayout
)
from PySide6.QtCore import Qt, QDate, QUrl
from PySide6.QtGui import QFont, QIcon, QDesktopServices, QColor, QPixmap

from services.csv_service import CSVService
from services.pdf_service import PDFService
from utils.validator import Validator
from utils.settings import get_setting, set_setting

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StaffDocx - Confidential Report")
        self.icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "app_icon.png")
        if os.path.exists(self.icon_path):
            self.setWindowIcon(QIcon(self.icon_path))
        self.resize(1000, 800)
        self.csv_service = None
        self.pdf_service = PDFService()
        self.selected_employee_data = None
        
        self.init_ui()
        self.apply_styles()
        self.load_initial_data()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header Frame
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 15, 30, 15)
        
        # Software App Icon
        logo_label = QLabel()
        if os.path.exists(self.icon_path):
            pixmap = QPixmap(self.icon_path).scaled(42, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("🎓")
            logo_label.setFont(QFont("Arial", 28))
        
        title_label = QLabel("StaffDocx")
        title_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title_label.setStyleSheet("color: #1e293b;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        settings_btn = QPushButton("Change CSV")
        settings_btn.setObjectName("secondaryBtn")
        settings_btn.clicked.connect(self.prompt_for_csv)
        header_layout.addWidget(settings_btn)
        
        main_layout.addWidget(header_frame, 0)

        # Add shadow to header
        shadow_header = QGraphicsDropShadowEffect()
        shadow_header.setBlurRadius(15)
        shadow_header.setColor(QColor(0, 0, 0, 15))
        shadow_header.setOffset(0, 2)
        header_frame.setGraphicsEffect(shadow_header)

        # Main Content Area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter for left (search) and right (details) panels
        splitter = QSplitter(Qt.Horizontal)
        content_layout.addWidget(splitter)
        main_layout.addWidget(content_widget, 1)

        # Left Panel (Search & List)
        left_panel = QWidget()
        left_panel.setObjectName("cardPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 24, 20, 24)
        left_layout.setSpacing(15)
        
        search_label = QLabel("Search Employee")
        search_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type name to search...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        
        self.employee_list = QListWidget()
        self.employee_list.itemSelectionChanged.connect(self.on_employee_selected)
        
        left_layout.addWidget(search_label)
        left_layout.addWidget(self.search_input)
        left_layout.addWidget(self.employee_list)
        
        splitter.addWidget(left_panel)

        # Right Panel (Details)
        right_panel = QWidget()
        right_panel.setObjectName("cardPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll Area for Right Panel content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(30, 30, 30, 10)
        scroll_layout.setSpacing(20)

        # Read-only Employee Details
        emp_details_group = QWidget()
        emp_layout = QFormLayout(emp_details_group)
        emp_layout.setVerticalSpacing(10)
        emp_layout.setLabelAlignment(Qt.AlignLeft)
        emp_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        emp_title = QLabel("Employee Details")
        emp_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        scroll_layout.addWidget(emp_title)

        self.emp_fields = {}
        csv_cols = ["Full Name", "Designation", "Date of Joining", "Basic Qualification", "Professional Qualification ", "Exp.in SVIS"]
        for field in csv_cols:
            le = QLineEdit()
            le.setReadOnly(True)
            self.emp_fields[field] = le
            emp_layout.addRow(QLabel(field.strip() + ":"), le)
            
        scroll_layout.addWidget(emp_details_group)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #e2e8f0;")
        scroll_layout.addWidget(sep)

        # Editable Document Details
        doc_details_group = QWidget()
        doc_layout = QVBoxLayout(doc_details_group)
        doc_layout.setSpacing(15)
        
        doc_title = QLabel("Confidential Report Details")
        doc_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        doc_layout.addWidget(doc_title)
        
        # 1. How long known
        how_long_layout = QHBoxLayout()
        how_long_layout.addWidget(QLabel("How long have you known the applicant?"))
        self.how_long_input = QLineEdit()
        how_long_layout.addWidget(self.how_long_input)
        doc_layout.addLayout(how_long_layout)

        # 2. Activities
        doc_layout.addWidget(QLabel("School activities where applicant is happiest/most successful:"))
        self.activities_grid = QGridLayout()
        self.activities_cb = {}
        activities_list = ["Academic", "Reading", "Sports", "Music", "Concerts", "Outdoors", "Community service"]
        for i, act in enumerate(activities_list):
            cb = QCheckBox(act)
            self.activities_cb[act] = cb
            self.activities_grid.addWidget(cb, i // 4, i % 4)
        doc_layout.addLayout(self.activities_grid)
        
        # 3. Academic Factors
        doc_layout.addWidget(QLabel("Factors for academic achievements:"))
        self.factors_grid = QGridLayout()
        self.factors_cb = {}
        factors_list = ["Retentive memory", "Hard, conscientious work", "Above average intelligence"]
        for i, fact in enumerate(factors_list):
            cb = QCheckBox(fact)
            self.factors_cb[fact] = cb
            self.factors_grid.addWidget(cb, i // 3, i % 3)
        doc_layout.addLayout(self.factors_grid)

        # 4. Ratings (1 to 5)
        doc_layout.addWidget(QLabel("Ratings (1 to 5): 1=Poor, 5=Excellent"))
        self.ratings_layout = QGridLayout()
        self.ratings_cb = {}
        ratings_list = [
            "Integrity", "Responsibility", "Initiative", "Leadership", 
            "Personality", "Response to challenges", "Attitude to work", 
            "Handling pressure", "Communication/ personal relations", "Punctuality"
        ]
        for i, rating in enumerate(ratings_list):
            self.ratings_layout.addWidget(QLabel(f"{i+1}. {rating}:"), i // 2, (i % 2) * 2)
            cb = QComboBox()
            cb.addItems(["1", "2", "3", "4", "5"])
            cb.setCurrentIndex(4) # Default to 5
            self.ratings_cb[rating] = cb
            self.ratings_layout.addWidget(cb, i // 2, (i % 2) * 2 + 1)
        doc_layout.addLayout(self.ratings_layout)

        # 5. Text Areas
        doc_layout.addWidget(QLabel("Any other comments:"))
        self.comments_input = QTextEdit()
        self.comments_input.setMaximumHeight(80)
        doc_layout.addWidget(self.comments_input)
        
        doc_layout.addWidget(QLabel("Special achievements:"))
        self.achievements_input = QTextEdit()
        self.achievements_input.setMaximumHeight(80)
        doc_layout.addWidget(self.achievements_input)

        scroll_layout.addWidget(doc_details_group)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        right_layout.addWidget(scroll_area)

        # Generate Button right-aligned
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(30, 10, 30, 30)
        button_layout.addStretch()
        self.generate_btn = QPushButton("Generate PDF")
        self.generate_btn.setMinimumHeight(45)
        self.generate_btn.setMinimumWidth(200)
        self.generate_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.generate_btn.clicked.connect(self.generate_pdf)
        button_layout.addWidget(self.generate_btn)
        
        right_layout.addLayout(button_layout)

        splitter.addWidget(right_panel)
        splitter.setSizes([350, 650])

    def apply_styles(self):
        style_sheet = """
        * {
            font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
        }
        QMainWindow {
            background-color: #f0f4f8;
        }
        QLabel {
            color: #334155;
        }
        QCheckBox {
            color: #334155;
            font-size: 13px;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid #cbd5e1;
            background-color: #f8fafc;
        }
        QCheckBox::indicator:hover {
            border: 1px solid #2563eb;
        }
        QCheckBox::indicator:checked {
            background-color: #2563eb;
            border: 1px solid #2563eb;
        }
        QFrame#headerFrame {
            background-color: #ffffff;
            border-bottom: 1px solid #e2e8f0;
        }
        #cardPanel {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-top: none;
            border-bottom: none;
        }
        QSplitter::handle {
            background: transparent;
            width: 24px;
        }
        QScrollBar:vertical {
            border: none;
            background: #f8fafc;
            width: 8px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background: #cbd5e1;
            border-radius: 4px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            border: none;
            background: #f8fafc;
            height: 8px;
            border-radius: 4px;
        }
        QScrollBar::handle:horizontal {
            background: #cbd5e1;
            border-radius: 4px;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QLineEdit, QTextEdit, QDateEdit, QComboBox {
            background-color: #f8fafc;
            color: #1e293b;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
        }
        QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QComboBox:focus {
            border: 1.5px solid #2563eb;
            background-color: #ffffff;
        }
        QLineEdit[readOnly="true"] {
            background-color: transparent;
            color: #475569;
            border: none;
            font-weight: 500;
            padding-left: 0px;
        }
        QListWidget {
            background-color: transparent;
            border: none;
            outline: none;
            color: #334155;
            font-size: 14px;
        }
        QListWidget::item {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 4px;
        }
        QListWidget::item:hover {
            background-color: #f1f5f9;
        }
        QListWidget::item:selected {
            background-color: #eff6ff;
            color: #2563eb;
            font-weight: bold;
        }
        QPushButton {
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #1d4ed8;
        }
        QPushButton:pressed {
            background-color: #1e40af;
        }
        QPushButton#secondaryBtn {
            background-color: #f1f5f9;
            color: #475569;
            border: 1px solid #cbd5e1;
        }
        QPushButton#secondaryBtn:hover {
            background-color: #e2e8f0;
            color: #1e293b;
        }
        """
        self.setStyleSheet(style_sheet)

    def load_initial_data(self):
        csv_path = get_setting("csv_path")
        if csv_path and os.path.exists(csv_path):
            self.load_csv(csv_path)

    def prompt_for_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Employees CSV", "", "CSV Files (*.csv)"
        )
        if file_path:
            set_setting("csv_path", file_path)
            self.load_csv(file_path)

    def load_csv(self, file_path):
        try:
            self.csv_service = CSVService(file_path)
            self.refresh_employee_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CSV:\n{e}")

    def refresh_employee_list(self, query=""):
        self.employee_list.clear()
        if not self.csv_service:
            return
            
        employees = self.csv_service.search_employees(query)
        for emp in employees:
            name = emp.get("Full Name", "Unknown")
            desig = emp.get("Designation", "")
            display_text = f"{name} ({desig})" if desig else name
            self.employee_list.addItem(display_text)
            
        self._current_employee_list = employees

    def on_search_text_changed(self, text):
        self.refresh_employee_list(text)

    def on_employee_selected(self):
        selected_items = self.employee_list.selectedIndexes()
        if not selected_items:
            self.selected_employee_data = None
            self.clear_employee_details()
            return
            
        index = selected_items[0].row()
        if index < len(self._current_employee_list):
            self.clear_employee_details()
            emp = self._current_employee_list[index]
            self.selected_employee_data = emp
            self.populate_employee_details(emp)

    def populate_employee_details(self, emp_data):
        for field, le in self.emp_fields.items():
            le.setText(emp_data.get(field, ""))
        
        # Pre-fill 'how long' using Exp.in SVIS if available
        exp = emp_data.get("Exp.in SVIS", "").strip()
        if exp and exp.isdigit():
            self.how_long_input.setText(f"{exp} years")
        else:
            self.how_long_input.setText(exp)

    def clear_employee_details(self):
        for le in self.emp_fields.values():
            le.clear()
        self.how_long_input.clear()
        self.comments_input.clear()
        self.achievements_input.clear()
        for cb in self.activities_cb.values():
            cb.setChecked(False)
        for cb in self.factors_cb.values():
            cb.setChecked(False)
        for cb in self.ratings_cb.values():
            cb.setCurrentIndex(4)

    def generate_pdf(self):
        if not self.selected_employee_data:
            QMessageBox.warning(self, "Validation Error", "Please select an employee first.")
            return
        
        emp_name = self.selected_employee_data.get("Full Name", "Employee").replace(" ", "_")
        gen_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_filename = f"{emp_name}_{gen_datetime}_CR.pdf"
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Confidential Report", default_filename, "PDF Files (*.pdf)"
        )
        if not save_path:
            return
        
        doc_data = {
            "How Long": self.how_long_input.text(),
            "Activities": [act for act, cb in self.activities_cb.items() if cb.isChecked()],
            "Factors": [fact for fact, cb in self.factors_cb.items() if cb.isChecked()],
            "Ratings": {rating: cb.currentText() for rating, cb in self.ratings_cb.items()},
            "Comments": self.comments_input.toPlainText(),
            "Achievements": self.achievements_input.toPlainText(),
            "Generated_DateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            # Assuming logo is in assets/logo.png if it exists
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
            pdf_path = self.pdf_service.generate_pdf(self.selected_employee_data, doc_data, logo_path, save_path)
            self.show_success_dialog(pdf_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF:\n{e}")

    def show_success_dialog(self, pdf_path):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Success")
        msg_box.setText("PDF generated successfully.")
        msg_box.setIcon(QMessageBox.Information)

        open_pdf_btn = msg_box.addButton("Open PDF", QMessageBox.ActionRole)
        open_folder_btn = msg_box.addButton("Open Output Folder", QMessageBox.ActionRole)
        close_btn = msg_box.addButton("Close", QMessageBox.RejectRole)

        msg_box.exec()

        if msg_box.clickedButton() == open_pdf_btn:
            QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path))
        elif msg_box.clickedButton() == open_folder_btn:
            folder_path = os.path.dirname(pdf_path)
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
