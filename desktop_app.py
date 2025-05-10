import sys
import os
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QTabWidget, QScrollArea, QFrame, 
                             QGridLayout, QCheckBox, QSlider, QSplitter,
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QSpacerItem, QSizePolicy, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QPen, QLinearGradient, QFont, QPainterPath, QBrush

from function_utils import parse_function, compute_derivative, compute_integral
import database as db

class GridBackground(QWidget):
    """Animated grid background widget."""
    
    def __init__(self, parent=None):
        super(GridBackground, self).__init__(parent)
        self.setAutoFillBackground(True)
        
        # Grid properties
        self.grid_spacing = 30
        self.line_color = QColor(90, 90, 150, 40)  # Soft blue with transparency
        self.line_width = 1
        
        # Animation settings
        self.offset_x = 0
        self.offset_y = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_offset)
        self.timer.start(50)  # Update every 50ms
        
    def update_offset(self):
        """Update the grid animation offset."""
        self.offset_x = (self.offset_x + 0.5) % self.grid_spacing
        self.offset_y = (self.offset_y + 0.5) % self.grid_spacing
        self.update()
        
    def paintEvent(self, event):
        """Paint the animated grid."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(20, 30, 45))  # Dark blue at top
        gradient.setColorAt(1, QColor(35, 45, 65))  # Slightly lighter at bottom
        painter.fillRect(self.rect(), gradient)
        
        # Draw vertical grid lines
        pen = QPen(self.line_color)
        pen.setWidth(self.line_width)
        painter.setPen(pen)
        
        for x in range(int(self.offset_x), self.width() + self.grid_spacing, self.grid_spacing):
            painter.drawLine(x, 0, x, self.height())
            
        # Draw horizontal grid lines
        for y in range(int(self.offset_y), self.height() + self.grid_spacing, self.grid_spacing):
            painter.drawLine(0, y, self.width(), y)


class MathKeyboardButton(QPushButton):
    """Custom styled button for math keyboard."""
    
    def __init__(self, text, symbol=None, parent=None, is_function=False):
        super(MathKeyboardButton, self).__init__(text, parent)
        self.symbol = symbol if symbol else text
        self.is_function = is_function
        
        # Set fixed size for consistent keyboard layout
        self.setFixedSize(40, 40)
        
        # Apply custom styling
        self.setStyleSheet("""
            QPushButton {
                background-color: #303848;
                color: #FFFFFF;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #404858;
            }
            QPushButton:hover {
                background-color: #404858;
                border: 1px solid #505868;
            }
            QPushButton:pressed {
                background-color: #505868;
            }
        """)


class MathKeyboard(QWidget):
    """Mathematical keyboard widget for easier function input."""
    
    def __init__(self, input_field, parent=None):
        super(MathKeyboard, self).__init__(parent)
        self.input_field = input_field
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the keyboard UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Set up rows
        row1_layout = QHBoxLayout()
        row2_layout = QHBoxLayout()
        row3_layout = QHBoxLayout()
        row4_layout = QHBoxLayout()
        
        # Numbers row
        for i in range(1, 10):
            btn = MathKeyboardButton(str(i))
            btn.clicked.connect(lambda _, s=str(i): self.insert_text(s))
            row1_layout.addWidget(btn)
        
        btn_0 = MathKeyboardButton("0")
        btn_0.clicked.connect(lambda: self.insert_text("0"))
        row1_layout.addWidget(btn_0)
        
        # Basic operators row
        operators = [("+", "+"), ("-", "-"), ("×", "*"), ("÷", "/"), ("(", "("), (")", ")")]
        for display, symbol in operators:
            btn = MathKeyboardButton(display, symbol)
            btn.clicked.connect(lambda _, s=symbol: self.insert_text(s))
            row2_layout.addWidget(btn)
        
        power_btn = MathKeyboardButton("x²", "**2")
        power_btn.clicked.connect(lambda: self.insert_text("**2"))
        row2_layout.addWidget(power_btn)
        
        nth_power_btn = MathKeyboardButton("x^n", "**")
        nth_power_btn.clicked.connect(lambda: self.insert_text("**"))
        row2_layout.addWidget(nth_power_btn)
        
        # Functions row
        functions = [
            ("sin", "sin(x)"), 
            ("cos", "cos(x)"), 
            ("tan", "tan(x)"), 
            ("exp", "exp(x)"), 
            ("log", "log(x)"), 
            ("sqrt", "sqrt(x)")
        ]
        
        for display, symbol in functions:
            btn = MathKeyboardButton(display, symbol, is_function=True)
            btn.clicked.connect(lambda _, s=symbol: self.insert_function(s))
            row3_layout.addWidget(btn)
        
        # Variable and clear row
        x_btn = MathKeyboardButton("x", "x")
        x_btn.clicked.connect(lambda: self.insert_text("x"))
        row4_layout.addWidget(x_btn)
        
        pi_btn = MathKeyboardButton("π", "pi")
        pi_btn.clicked.connect(lambda: self.insert_text("pi"))
        row4_layout.addWidget(pi_btn)
        
        e_btn = MathKeyboardButton("e", "e")
        e_btn.clicked.connect(lambda: self.insert_text("e"))
        row4_layout.addWidget(e_btn)
        
        # Add a spacer to push buttons to the left
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        row4_layout.addItem(spacer)
        
        clear_btn = MathKeyboardButton("Clear")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B2E2E;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #9B3E3E;
            }
            QPushButton:hover {
                background-color: #9B3E3E;
            }
        """)
        clear_btn.setFixedSize(80, 40)
        clear_btn.clicked.connect(self.clear_input)
        row4_layout.addWidget(clear_btn)
        
        # Add rows to main layout
        layout.addLayout(row1_layout)
        layout.addLayout(row2_layout)
        layout.addLayout(row3_layout)
        layout.addLayout(row4_layout)
        
        # Add some padding and styling
        self.setStyleSheet("""
            QWidget {
                background-color: #282C38;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
    def insert_text(self, text):
        """Insert text at the current cursor position."""
        current_text = self.input_field.text()
        cursor_pos = self.input_field.cursorPosition()
        new_text = current_text[:cursor_pos] + text + current_text[cursor_pos:]
        self.input_field.setText(new_text)
        self.input_field.setCursorPosition(cursor_pos + len(text))
        self.input_field.setFocus()
        
    def insert_function(self, function_text):
        """Insert a function template and place cursor appropriately."""
        current_text = self.input_field.text()
        cursor_pos = self.input_field.cursorPosition()
        
        # Replace 'x' with cursor position
        if 'x' in function_text:
            # For functions like sin(x), position cursor where 'x' is
            x_pos = function_text.find('x')
            insert_text = function_text.replace('x', '')
            new_text = current_text[:cursor_pos] + insert_text + current_text[cursor_pos:]
            self.input_field.setText(new_text)
            self.input_field.setCursorPosition(cursor_pos + x_pos)
        else:
            # For other functions, just append and place cursor at end
            new_text = current_text[:cursor_pos] + function_text + current_text[cursor_pos:]
            self.input_field.setText(new_text)
            self.input_field.setCursorPosition(cursor_pos + len(function_text))
            
        self.input_field.setFocus()
        
    def clear_input(self):
        """Clear the input field."""
        self.input_field.clear()
        self.input_field.setFocus()


class HistoryTable(QTableWidget):
    """Table widget to display function history."""
    
    def __init__(self, parent=None):
        super(HistoryTable, self).__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the table UI."""
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Function", "Range", "Properties", "Actions"])
        
        # Style the table
        self.setStyleSheet("""
            QTableWidget {
                background-color: #2D3142;
                alternate-background-color: #363A4F;
                color: #FFFFFF;
                gridline-color: #3D4152;
                border: none;
            }
            QHeaderView::section {
                background-color: #383D52;
                color: #FFFFFF;
                padding: 5px;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        
        # Set column widths
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        # Enable alternating row colors
        self.setAlternatingRowColors(True)
        
    def load_history(self, entries):
        """Load history entries into the table."""
        self.setRowCount(0)  # Clear existing rows
        
        for entry in entries:
            row_position = self.rowCount()
            self.insertRow(row_position)
            
            # Function text
            function_item = QTableWidgetItem(entry.function_text)
            function_item.setData(Qt.UserRole, entry.id)  # Store the entry ID
            self.setItem(row_position, 0, function_item)
            
            # Range
            range_text = f"[{entry.x_min}, {entry.x_max}]"
            range_item = QTableWidgetItem(range_text)
            self.setItem(row_position, 1, range_item)
            
            # Properties
            properties = []
            if entry.show_derivative:
                properties.append(f"Deriv(order={entry.derivative_order})")
            if entry.show_integral:
                properties.append("Integral")
            properties_item = QTableWidgetItem(", ".join(properties))
            self.setItem(row_position, 2, properties_item)
            
            # Actions - add button in cell
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 4, 4, 4)
            
            load_button = QPushButton("Load")
            load_button.setStyleSheet("""
                QPushButton {
                    background-color: #4070A0;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #5080B0;
                }
            """)
            load_button.clicked.connect(lambda _, i=entry.id: self.load_entry(i))
            action_layout.addWidget(load_button)
            
            self.setCellWidget(row_position, 3, action_widget)
    
    def load_entry(self, entry_id):
        """Signal to load the selected entry."""
        self.parent().load_history_entry(entry_id)


class MatplotlibCanvas(FigureCanvas):
    """Canvas for displaying matplotlib plots."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MatplotlibCanvas, self).__init__(self.fig)
        self.setParent(parent)
        
        # Set the matplotlib style for dark theme
        plt.style.use('dark_background')
        
        # Customize figure appearance
        self.fig.patch.set_facecolor('#282C38')
        self.axes.set_facecolor('#1F232F')
        
        # Configure axes appearance
        self.axes.spines['bottom'].set_color('#999999')
        self.axes.spines['top'].set_color('#999999')
        self.axes.spines['left'].set_color('#999999')
        self.axes.spines['right'].set_color('#999999')
        self.axes.tick_params(colors='#999999')
        self.axes.xaxis.label.set_color('#EEEEEE')
        self.axes.yaxis.label.set_color('#EEEEEE')
        self.axes.title.set_color('#EEEEEE')
        
        # Enable matplotlib to adjust to the canvas size
        self.fig.tight_layout()


class CalculusVisualizerApp(QMainWindow):
    """Main application window for the Calculus Visualizer."""
    
    def __init__(self):
        super(CalculusVisualizerApp, self).__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the main UI."""
        self.setWindowTitle("Calculus Visualizer")
        self.setMinimumSize(1200, 800)
        
        # Set dark theme stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #242A38;
                color: #FFFFFF;
            }
            QTabWidget::pane {
                border: 1px solid #3D4152;
                background-color: #282C38;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #2D3142;
                color: #BBBBBB;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid #3D4152;
                border-bottom: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #383D52;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
            }
            QLineEdit, QComboBox {
                background-color: #1F232F;
                color: #FFFFFF;
                border: 1px solid #3D4152;
                border-radius: 4px;
                padding: 5px;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #1F232F;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #5070A0;
                border: none;
                width: 16px;
                height: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QCheckBox {
                color: #FFFFFF;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background-color: #1F232F;
                border: 1px solid #3D4152;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #5070A0;
            }
            QGroupBox {
                border: 1px solid #3D4152;
                border-radius: 4px;
                margin-top: 20px;
                color: #FFFFFF;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #4070A0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5080B0;
            }
            QPushButton:pressed {
                background-color: #6090C0;
            }
        """)
        
        # Create central widget with background
        self.central_widget = GridBackground(self)
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create the header with title
        header_layout = QHBoxLayout()
        title_label = QLabel("Calculus Visualizer")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #FFFFFF;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)
        
        # Create tab widget for visualization and history
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create visualization tab
        self.visualization_tab = QWidget()
        self.tab_widget.addTab(self.visualization_tab, "Visualization")
        
        # Create history tab
        self.history_tab = QWidget()
        self.tab_widget.addTab(self.history_tab, "History")
        
        # Set up visualization tab
        self.setup_visualization_tab()
        
        # Set up history tab
        self.setup_history_tab()
        
        # Set up database connection
        self.load_history()
    
    def setup_visualization_tab(self):
        """Set up the visualization tab UI."""
        viz_layout = QVBoxLayout(self.visualization_tab)
        
        # Create splitter for inputs and visualization
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel for inputs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Function input group
        function_group = QGroupBox("Function Input")
        function_layout = QVBoxLayout(function_group)
        
        # Function input field with nice styling
        self.function_input = QLineEdit("x**2 - 4*x + 4")
        self.function_input.setPlaceholderText("Enter a function of x")
        self.function_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 8px;
                border: 1px solid #3D4152;
                border-radius: 4px;
                background-color: #1F232F;
                color: #FFFFFF;
            }
        """)
        function_layout.addWidget(self.function_input)
        
        # Add math keyboard
        self.math_keyboard = MathKeyboard(self.function_input)
        function_layout.addWidget(self.math_keyboard)
        
        left_layout.addWidget(function_group)
        
        # Plot settings group
        settings_group = QGroupBox("Plot Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Range inputs
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("x min:"))
        self.x_min_input = QLineEdit("-10")
        range_layout.addWidget(self.x_min_input)
        range_layout.addWidget(QLabel("x max:"))
        self.x_max_input = QLineEdit("10")
        range_layout.addWidget(self.x_max_input)
        settings_layout.addLayout(range_layout)
        
        # Derivative options
        deriv_layout = QHBoxLayout()
        self.show_derivative = QCheckBox("Show Derivative")
        self.show_derivative.setChecked(True)
        deriv_layout.addWidget(self.show_derivative)
        
        deriv_layout.addWidget(QLabel("Order:"))
        self.derivative_order = QSlider(Qt.Horizontal)
        self.derivative_order.setMinimum(1)
        self.derivative_order.setMaximum(5)
        self.derivative_order.setValue(1)
        self.derivative_order.setTickPosition(QSlider.TicksBelow)
        self.derivative_order.setTickInterval(1)
        
        # Add a label to show the current value
        self.derivative_value_label = QLabel("1")
        self.derivative_order.valueChanged.connect(
            lambda v: self.derivative_value_label.setText(str(v))
        )
        
        deriv_layout.addWidget(self.derivative_order)
        deriv_layout.addWidget(self.derivative_value_label)
        settings_layout.addLayout(deriv_layout)
        
        # Integral option
        integral_layout = QHBoxLayout()
        self.show_integral = QCheckBox("Show Integral")
        self.show_integral.setChecked(True)
        integral_layout.addWidget(self.show_integral)
        integral_layout.addStretch()
        settings_layout.addLayout(integral_layout)
        
        # Plot type selection
        plot_type_layout = QHBoxLayout()
        plot_type_layout.addWidget(QLabel("Plot Type:"))
        self.plot_type = QComboBox()
        self.plot_type.addItems(["Combined", "Separate"])
        plot_type_layout.addWidget(self.plot_type)
        settings_layout.addLayout(plot_type_layout)
        
        left_layout.addWidget(settings_group)
        
        # Visualization button
        self.visualize_button = QPushButton("Visualize Function")
        self.visualize_button.setStyleSheet("""
            QPushButton {
                background-color: #4070A0;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5080B0;
            }
        """)
        self.visualize_button.clicked.connect(self.visualize_function)
        left_layout.addWidget(self.visualize_button)
        
        # Add spacer at the bottom
        left_layout.addStretch()
        
        # Right panel for visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add matplotlib canvas for visualization
        self.canvas = MatplotlibCanvas(self, width=10, height=8)
        right_layout.addWidget(self.canvas)
        
        # Add LaTeX display for equations
        latex_frame = QFrame()
        latex_frame.setStyleSheet("""
            QFrame {
                background-color: #1F232F;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        latex_layout = QVBoxLayout(latex_frame)
        
        self.function_latex = QLabel("f(x) = x² - 4x + 4")
        self.function_latex.setStyleSheet("font-size: 16px;")
        latex_layout.addWidget(self.function_latex)
        
        self.derivative_latex = QLabel("f'(x) = 2x - 4")
        self.derivative_latex.setStyleSheet("font-size: 16px;")
        latex_layout.addWidget(self.derivative_latex)
        
        self.integral_latex = QLabel("∫f(x)dx = x³/3 - 2x² + 4x + C")
        self.integral_latex.setStyleSheet("font-size: 16px;")
        latex_layout.addWidget(self.integral_latex)
        
        right_layout.addWidget(latex_frame)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set the initial sizes
        splitter.setSizes([400, 800])
        
        viz_layout.addWidget(splitter)
    
    def setup_history_tab(self):
        """Set up the history tab UI."""
        history_layout = QVBoxLayout(self.history_tab)
        
        # Add history table
        self.history_table = HistoryTable(self)
        history_layout.addWidget(self.history_table)
        
        # Add clear history button
        clear_history_button = QPushButton("Clear History")
        clear_history_button.setStyleSheet("""
            QPushButton {
                background-color: #8B2E2E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #9B3E3E;
            }
        """)
        # This button doesn't actually clear the history in this version
        history_layout.addWidget(clear_history_button)
    
    def visualize_function(self):
        """Visualize the function with its derivative and integral."""
        try:
            # Get inputs
            function_text = self.function_input.text()
            x_min = float(self.x_min_input.text())
            x_max = float(self.x_max_input.text())
            show_derivative = self.show_derivative.isChecked()
            derivative_order = self.derivative_order.value()
            show_integral = self.show_integral.isChecked()
            plot_type = self.plot_type.currentText()
            
            # Validate inputs
            if x_min >= x_max:
                x_max = x_min + 1.0
                self.x_max_input.setText(str(x_max))
            
            # Parse the function
            expr = parse_function(function_text)
            
            # Update LaTeX displays
            self.function_latex.setText(f"f(x) = {sp.latex(expr)}")
            
            if show_derivative:
                deriv_expr = compute_derivative(expr, order=derivative_order)
                if derivative_order == 1:
                    self.derivative_latex.setText(f"f'(x) = {sp.latex(deriv_expr)}")
                else:
                    self.derivative_latex.setText(f"f^({derivative_order})(x) = {sp.latex(deriv_expr)}")
                self.derivative_latex.setVisible(True)
            else:
                self.derivative_latex.setVisible(False)
            
            if show_integral:
                integ_expr = compute_integral(expr)
                self.integral_latex.setText(f"∫f(x)dx = {sp.latex(integ_expr)} + C")
                self.integral_latex.setVisible(True)
            else:
                self.integral_latex.setVisible(False)
            
            # Clear the canvas
            self.canvas.axes.clear()
            
            # Create data for plot
            x = np.linspace(x_min, x_max, 1000)
            
            # Convert sympy expressions to numpy functions
            f = sp.lambdify('x', expr, 'numpy')
            y = f(x)
            
            # Plot the original function
            self.canvas.axes.plot(x, y, 'c-', linewidth=2, label=f'f(x)')
            
            # Plot derivative if requested
            if show_derivative:
                deriv_expr = compute_derivative(expr, order=derivative_order)
                df = sp.lambdify('x', deriv_expr, 'numpy')
                dy = df(x)
                
                self.canvas.axes.plot(x, dy, 'm-', linewidth=2, 
                                    label=f'f{"′" * derivative_order}(x)')
            
            # Plot integral if requested
            if show_integral:
                integ_expr = compute_integral(expr)
                intf = sp.lambdify('x', integ_expr, 'numpy')
                inty = intf(x)
                
                # Normalize the integral to start at 0
                inty = inty - inty[0]
                
                self.canvas.axes.plot(x, inty, 'g-', linewidth=2, label='∫f(x)dx')
            
            # Configure axes
            self.canvas.axes.set_xlabel('x')
            self.canvas.axes.set_ylabel('y')
            self.canvas.axes.set_title('Function Visualization')
            self.canvas.axes.legend()
            self.canvas.axes.grid(True, linestyle='--', alpha=0.6)
            
            # Draw the plot
            self.canvas.draw()
            
            # Save to database
            latex_repr = sp.latex(expr)
            db.save_function_entry(
                function_text=function_text,
                latex_representation=latex_repr,
                x_min=x_min,
                x_max=x_max,
                show_derivative=show_derivative,
                derivative_order=derivative_order,
                show_integral=show_integral,
                ai_explanation=None
            )
            
            # Refresh history
            self.load_history()
            
        except Exception as e:
            # Show error in the plot area
            self.canvas.axes.clear()
            self.canvas.axes.text(0.5, 0.5, f"Error: {str(e)}", 
                                horizontalalignment='center',
                                verticalalignment='center',
                                transform=self.canvas.axes.transAxes,
                                fontsize=14, color='red')
            self.canvas.draw()
    
    def load_history(self):
        """Load history from database."""
        history_entries = db.get_all_function_entries(limit=10)
        self.history_table.load_history(history_entries)
    
    def load_history_entry(self, entry_id):
        """Load a function from history."""
        entry = db.get_function_entry(entry_id)
        if entry:
            self.function_input.setText(entry.function_text)
            self.x_min_input.setText(str(entry.x_min))
            self.x_max_input.setText(str(entry.x_max))
            self.show_derivative.setChecked(entry.show_derivative)
            self.derivative_order.setValue(entry.derivative_order)
            self.show_integral.setChecked(entry.show_integral)
            
            # Switch to visualization tab
            self.tab_widget.setCurrentIndex(0)
            
            # Visualize the function
            self.visualize_function()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = CalculusVisualizerApp()
    window.show()
    sys.exit(app.exec_())