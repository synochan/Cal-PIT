# Calculus Visualizer

An interactive Python application for visualizing mathematical functions, their derivatives, and integrals. This application allows users to input mathematical functions, visualize their behavior, and store the visualization history in a database.

## Features

- Function visualization with interactive plotting
- Support for derivative calculation and visualization (up to 5th order)
- Support for integral calculation and visualization
- LaTeX rendering of mathematical expressions
- Database-backed history for saving previous calculations
- Interactive controls for adjusting plot parameters
- Educational information about calculus concepts

## Running the Application

To run the application, you'll need Python with the required dependencies installed:

```bash
# Install required packages
pip install -r dependencies.txt
```

Once dependencies are installed, you can run the application using:

```bash
streamlit run app.py
```

Or open the project in VS Code and run it from there.

## Usage

1. Enter a mathematical function in the text area (e.g., `x**2 - 4*x + 4`, `sin(x)`, or `exp(-x**2)`)
2. Adjust the x-range and visualization options as needed
3. View the function, its derivative, and integral in the main visualization area
4. Check the History tab to see your previously visualized functions

## Function Syntax

- Use `x` as the variable
- Use `**` for powers (e.g., `x**2` for x²)
- Available functions: `sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `abs`

## Project Structure

- `app.py` - Main Streamlit application
- `function_utils.py` - Utilities for parsing and computing functions
- `visualization.py` - Functions for generating visualizations
- `database.py` - Database connectivity and history storage