#!/usr/bin/env python3
"""
Calculus Visualizer Desktop App Launcher

This script launches the desktop version of the Calculus Visualizer application.
"""

import sys
from desktop_app import CalculusVisualizerApp
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    print("Starting Calculus Visualizer Desktop Application...")
    app = QApplication(sys.argv)
    window = CalculusVisualizerApp()
    window.show()
    sys.exit(app.exec_())