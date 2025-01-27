from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QApplication
import sys
import subprocess

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Script Launcher")
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.launch_button1 = QPushButton("Launch Script 1")
        self.launch_button1.clicked.connect(self.launch_script1)
        self.layout.addWidget(self.launch_button1)

        self.launch_button2 = QPushButton("Launch Script 2")
        self.launch_button2.clicked.connect(self.launch_script2)
        self.layout.addWidget(self.launch_button2)

        self.launch_button3 = QPushButton("Launch Script 3")
        self.launch_button3.clicked.connect(self.launch_script3)
        self.layout.addWidget(self.launch_button3)

    def launch_script1(self):
        self.launch_script("path/to/script1.py")

    def launch_script2(self):
        self.launch_script("path/to/script2.py")

    def launch_script3(self):
        self.launch_script("path/to/script3.py")

    def launch_script(self, script_path):
        subprocess.Popen([sys.executable, script_path])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())