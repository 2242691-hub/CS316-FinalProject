import sys
import numpy as np
import sympy as sp
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QHeaderView, QWidget, QHBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from model import NewtonRaphsonModel


class NewtonController(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Load the View
        try:
            uic.loadUi('view.ui', self)
        except FileNotFoundError:
            print("Error: view.ui not found. Please ensure it is in the same directory.")
            sys.exit(1)

        # 2. Initialize the Model
        self.model = NewtonRaphsonModel()

        # 3. Connect UI signals FIRST
        self.btnSolve.clicked.connect(self.calculate)

        # 4. Table Configuration (Crucial for the "Clean" look)
        header = self.tableIterations.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # ENABLE ALTERNATING COLORS for readability
        self.tableIterations.setAlternatingRowColors(True)
        # Hide the vertical header (row numbers 1, 2, 3...) since we have an "Iter" column
        self.tableIterations.verticalHeader().setVisible(False)

        # 5. Setup the Graph
        self.setup_graph_ui()

        # 6. Apply the Theme
        self.apply_game_theme()

    def setup_graph_ui(self):
        """Safely re-arranges the UI to put controls on Left and Graph on Right."""
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.style_plot_area()

        old_central = self.centralWidget()
        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)

        if old_central:
            old_central.setParent(wrapper)
            wrapper_layout.addWidget(old_central, stretch=1)
            wrapper_layout.addWidget(self.canvas, stretch=2)
            self.setCentralWidget(wrapper)

    def style_plot_area(self):
        """Sets the Cyberpunk/Arcade look for the Matplotlib chart."""
        self.figure.patch.set_facecolor('#1e1e2e')
        self.ax.set_facecolor('#2b2b40')

        for spine in self.ax.spines.values():
            spine.set_color('#5c5c7f')

        self.ax.tick_params(axis='x', colors='#00e5ff')
        self.ax.tick_params(axis='y', colors='#00e5ff')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.set_title("Function Analysis", color='#00e676', fontsize=12, weight='bold')
        self.ax.grid(True, color='#5c5c7f', linestyle='--', alpha=0.5)

    def apply_game_theme(self):
        """Applies a High-Contrast Table style + Cyberpunk UI."""

        # Colors
        bg_dark = "#1e1e2e"
        text_white = "#ffffff"
        neon_green = "#00e676"
        neon_cyan = "#00e5ff"

        # Table Specific Colors (Matches the readable aesthetic)
        table_header_bg = "#006064"  # Deep Cyan/Teal for headers
        table_row_even = "#2b2b40"  # Dark Grey
        table_row_odd = "#383854"  # Slightly lighter Grey
        table_grid = "#454560"

        style = f"""
        QMainWindow {{ background-color: {bg_dark}; }}

        QLabel {{ 
            color: {text_white}; 
            font-family: 'Segoe UI', sans-serif; 
            font-size: 14px;
            font-weight: bold; 
        }}

        QLineEdit {{
            background-color: #2b2b40; 
            color: {neon_cyan};
            border: 2px solid #5c5c7f; 
            border-radius: 6px; 
            padding: 8px;
            font-family: 'Consolas', monospace;
            font-size: 14px;
        }}

        QPushButton {{
            background-color: {neon_green}; 
            color: #000000;
            border-bottom: 5px solid #00a856; 
            border-radius: 8px;
            font-weight: 900; 
            padding: 10px;
            font-size: 15px;
        }}
        QPushButton:pressed {{
            border-bottom: 2px solid #00a856; 
            margin-top: 3px;
        }}

        /* --- THE AESTHETIC TABLE STYLES --- */
        QTableWidget {{
            background-color: {table_row_even};
            alternate-background-color: {table_row_odd};
            color: white;
            gridline-color: {table_grid};
            border: 2px solid {table_grid};
            font-size: 14px;
            font-family: 'Segoe UI', sans-serif;
        }}

        /* The Header (Top Bar) */
        QHeaderView::section {{
            background-color: {table_header_bg};
            color: white;
            padding: 8px;
            border: 1px solid {table_grid};
            font-weight: bold;
            font-size: 14px;
            text-transform: uppercase; /* Makes it look like a dashboard */
        }}

        /* The Corner Button (Top Left) */
        QTableCornerButton::section {{
            background-color: {table_header_bg};
            border: 1px solid {table_grid};
        }}
        """
        self.setStyleSheet(style)

    def calculate(self):
        func_str = self.inputFunction.text()
        guess_str = self.inputGuess.text()
        tol_str = self.inputTol.text()

        if not func_str or not guess_str:
            self.show_error("Input Missing!")
            return
        try:
            guess = float(guess_str)
            tol = float(tol_str)
        except ValueError:
            self.show_error("Invalid Numbers!")
            return

        result = self.model.solve(func_str, guess, tol)

        if 'error' in result:
            self.show_error(f"Math Error: {result['error']}")
            return

        if result['root'] is not None:
            self.lblResult.setText(f"ROOT FOUND: {result['root']:.6f}")
            self.lblResult.setStyleSheet(
                "color: #00e676; font-size: 14pt; font-weight: bold; border: 2px dashed #00e676; padding: 5px;")
            self.update_graph(func_str, result['root'], result['history'], guess)
        else:
            self.lblResult.setText("Failed to converge")
            self.lblResult.setStyleSheet("color: #ff1744; font-size: 12pt;")

        self.populate_table(result['history'])

    def update_graph(self, func_str, root, history, guess):
        self.ax.clear()
        self.style_plot_area()

        try:
            x_sym = sp.symbols('x')
            f_expr = sp.sympify(func_str)
            f_lamb = sp.lambdify(x_sym, f_expr, 'numpy')

            points = [h['x_n'] for h in history]
            points.append(guess)
            points.append(root)

            min_x = min(points) - 2
            max_x = max(points) + 2

            x_vals = np.linspace(min_x, max_x, 400)
            y_vals = f_lamb(x_vals)

            self.ax.plot(x_vals, y_vals, color='#00e5ff', linewidth=2, label=f'f(x)')
            self.ax.axhline(0, color='white', linestyle='--', alpha=0.5)

            path_x = [h['x_n'] for h in history]
            path_y = [h['f_x'] for h in history]
            self.ax.scatter(path_x, path_y, color='#ff1744', s=30, zorder=5, label='Iterations')
            self.ax.plot(root, 0, marker='*', markersize=15, color='#00e676', markeredgecolor='white', linestyle='None',
                         label='Root')

            legend = self.ax.legend()
            frame = legend.get_frame()
            frame.set_facecolor('#1e1e2e')
            frame.set_edgecolor('#5c5c7f')
            for text in legend.get_texts():
                text.set_color('white')
            self.canvas.draw()

        except Exception as e:
            print(f"Graphing Error: {e}")

    def populate_table(self, history):
        self.tableIterations.setRowCount(0)
        for row_idx, data in enumerate(history):
            self.tableIterations.insertRow(row_idx)

            # Align text to Center for better readability
            items = [
                str(data['iteration']),
                f"{data['x_n']:.6f}",
                f"{data['f_x']:.6f}",
                f"{data['df_x']:.6f}"
            ]

            for col_idx, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(0x0084)  # Qt.AlignmentFlag.AlignCenter
                self.tableIterations.setItem(row_idx, col_idx, item)

    def show_error(self, message):
        msg = QMessageBox(self)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setStyleSheet("background-color: #1e1e2e; color: white;")
        msg.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = NewtonController()
    window.show()
    sys.exit(app.exec())