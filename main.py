import sys
import numpy as np
import sympy as sp
from PyQt6 import QtWidgets, uic, QtCore, QtGui
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QHeaderView, QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QPushButton
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from model import NewtonRaphsonModel


# ==========================================
# 1. THE NEW "VIDEO GAME" START SCREEN
# ==========================================
class StartScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Newton-Raphson: The Game")
        self.resize(600, 500)
        self.setup_ui()

    def setup_ui(self):
        # Main Vertical Layout
        layout = QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        # 1. The Game Title
        self.title_label = QLabel("NEWTON\nRAPHSON\nSOLVER")
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Spacer
        layout.addSpacing(50)

        # 2. The "PRESS START" Button
        self.btn_start = QPushButton("PRESS START")
        self.btn_start.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btn_start.clicked.connect(self.launch_main_app)
        layout.addWidget(self.btn_start)

        # 3. Apply Cyberpunk/Arcade Styles
        self.apply_styles()

    def apply_styles(self):
        # Dark Background
        self.setStyleSheet("background-color: #1e1e2e;")

        # Title Style (Neon Cyan with spacing)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #00e5ff;
                font-family: 'Impact', 'Verdana', sans-serif;
                font-size: 48px;
                font-weight: bold;
                letter-spacing: 5px;
            }
        """)

        # Button Style (Retro Arcade Button - Hot Pink)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #ff0055; /* Hot Pink */
                color: white;
                font-family: 'Segoe UI', sans-serif;
                font-size: 24px;
                font-weight: 900;
                border: none;
                border-bottom: 8px solid #990033; /* 3D Depth */
                border-radius: 25px;
                padding: 20px 60px;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #ff3377; /* Brighter */
                margin-top: 2px;
                border-bottom: 6px solid #990033;
            }
            QPushButton:pressed {
                background-color: #ff0055;
                border-bottom: 2px solid #990033; /* Squished */
                margin-top: 8px; /* Moves down */
            }
        """)

    def launch_main_app(self):
        # Open the Main Controller and close this screen
        self.main_window = NewtonController()
        self.main_window.show()
        self.close()


# ==========================================
# 2. THE MAIN APPLICATION (The Solver)
# ==========================================
class NewtonController(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Load View
        try:
            uic.loadUi('view.ui', self)
        except FileNotFoundError:
            print("Error: view.ui not found.")
            sys.exit(1)

        self.model = NewtonRaphsonModel()
        self.btnSolve.clicked.connect(self.calculate)

        # Table Setup (Aesthetic)
        header = self.tableIterations.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableIterations.setAlternatingRowColors(True)
        self.tableIterations.verticalHeader().setVisible(False)

        # Setup Graph and Theme
        self.setup_graph_ui()
        self.apply_game_theme()

    def setup_graph_ui(self):
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
        self.figure.patch.set_facecolor('#1e1e2e')
        self.ax.set_facecolor('#2b2b40')
        for spine in self.ax.spines.values(): spine.set_color('#5c5c7f')
        self.ax.tick_params(axis='x', colors='#00e5ff')
        self.ax.tick_params(axis='y', colors='#00e5ff')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.set_title("Function Analysis", color='#00e676', fontsize=12, weight='bold')
        self.ax.grid(True, color='#5c5c7f', linestyle='--', alpha=0.5)

    def apply_game_theme(self):
        # Styles for the MAIN solver window
        bg_dark = "#1e1e2e"
        neon_cyan = "#00e5ff"
        neon_green = "#00e676"

        style = f"""
        QMainWindow {{ background-color: {bg_dark}; }}
        QLabel {{ color: white; font-family: 'Segoe UI', sans-serif; font-size: 14px; font-weight: bold; }}
        QLineEdit {{
            background-color: #2b2b40; color: {neon_cyan};
            border: 2px solid #5c5c7f; border-radius: 6px; padding: 8px;
            font-family: 'Consolas', monospace; font-size: 14px;
        }}
        QPushButton {{
            background-color: {neon_green}; color: #000000;
            border-bottom: 5px solid #00a856; border-radius: 8px;
            font-weight: 900; padding: 10px; font-size: 15px;
        }}
        QPushButton:pressed {{ border-bottom: 2px solid #00a856; margin-top: 3px; }}
        QTableWidget {{
            background-color: #2b2b40; alternate-background-color: #383854;
            color: white; gridline-color: #454560; border: 2px solid #454560;
            font-size: 14px; font-family: 'Segoe UI', sans-serif;
        }}
        QHeaderView::section {{
            background-color: #006064; color: white; padding: 8px;
            border: 1px solid #454560; font-weight: bold; text-transform: uppercase;
        }}
        QTableCornerButton::section {{ background-color: #006064; border: 1px solid #454560; }}
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

            points = [h['x_n'] for h in history] + [guess, root]
            min_x, max_x = min(points) - 2, max(points) + 2
            x_vals = np.linspace(min_x, max_x, 400)

            self.ax.plot(x_vals, f_lamb(x_vals), color='#00e5ff', linewidth=2, label='f(x)')
            self.ax.axhline(0, color='white', linestyle='--', alpha=0.5)
            self.ax.scatter([h['x_n'] for h in history], [h['f_x'] for h in history], color='#ff1744', s=30, zorder=5,
                            label='Iterations')
            self.ax.plot(root, 0, marker='*', markersize=15, color='#00e676', markeredgecolor='white', linestyle='None',
                         label='Root')

            legend = self.ax.legend()
            legend.get_frame().set_facecolor('#1e1e2e')
            for text in legend.get_texts(): text.set_color('white')
            self.canvas.draw()
        except Exception as e:
            print(f"Graphing Error: {e}")

    def populate_table(self, history):
        self.tableIterations.setRowCount(0)
        for row_idx, data in enumerate(history):
            self.tableIterations.insertRow(row_idx)
            items = [str(data['iteration']), f"{data['x_n']:.6f}", f"{data['f_x']:.6f}", f"{data['df_x']:.6f}"]
            for col_idx, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(0x0084)  # Center
                self.tableIterations.setItem(row_idx, col_idx, item)

    def show_error(self, message):
        msg = QMessageBox(self)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setStyleSheet("background-color: #1e1e2e; color: white;")
        msg.exec()


# ==========================================
# 3. EXECUTION START
# ==========================================
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # We now start the START SCREEN, not the main controller directly
    start_screen = StartScreen()
    start_screen.show()

    sys.exit(app.exec())