import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import sympy as sp
from function_utils import (
    function_to_callable, 
    compute_derivative, 
    compute_integral,
    numerical_derivative, 
    evaluate_function
)

def generate_plot_data(expr, x_min, x_max, num_points=1000, compute_deriv=True, compute_integ=True, deriv_order=1):
    """
    Generate data for plotting a function and its derivatives/integrals.
    
    Args:
        expr (sympy.Expr): SymPy expression to plot.
        x_min (float): Minimum x value.
        x_max (float): Maximum x value.
        num_points (int): Number of points to evaluate.
        compute_deriv (bool): Whether to compute derivatives.
        compute_integ (bool): Whether to compute integrals.
        deriv_order (int): Order of derivative to compute.
        
    Returns:
        tuple: (x values, function values, derivative values, integral values)
    """
    x = sp.Symbol('x')
    
    # Generate x values
    x_vals = np.linspace(x_min, x_max, num_points)
    
    # Convert to callable functions
    func = function_to_callable(expr)
    
    # Evaluate the original function
    y_vals = evaluate_function(func, x_vals)
    
    deriv_vals = None
    if compute_deriv:
        # Compute symbolic derivative
        deriv_expr = compute_derivative(expr, order=deriv_order)
        deriv_func = function_to_callable(deriv_expr)
        deriv_vals = evaluate_function(deriv_func, x_vals)
    
    integ_vals = None
    if compute_integ:
        # Compute symbolic indefinite integral
        integ_expr = compute_integral(expr)
        integ_func = function_to_callable(integ_expr)
        integ_vals = evaluate_function(integ_func, x_vals)
        
        # Normalize the integral to start at 0 for the first point
        if not np.all(np.isnan(integ_vals)):
            integ_vals = integ_vals - integ_vals[0]
    
    return x_vals, y_vals, deriv_vals, integ_vals

def create_combined_plot(expr, x_min, x_max, num_points=1000, show_deriv=True, show_integ=True, deriv_order=1):
    """
    Create a combined plot of a function, its derivative, and its integral.
    
    Args:
        expr (sympy.Expr): SymPy expression to plot.
        x_min (float): Minimum x value.
        x_max (float): Maximum x value.
        num_points (int): Number of points to evaluate.
        show_deriv (bool): Whether to show derivatives.
        show_integ (bool): Whether to show integrals.
        deriv_order (int): Order of derivative to compute.
        
    Returns:
        matplotlib.figure.Figure: Figure object containing the plot.
    """
    x_vals, y_vals, deriv_vals, integ_vals = generate_plot_data(
        expr, x_min, x_max, num_points, show_deriv, show_integ, deriv_order
    )
    
    # Create the plot
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(1, 1, 1)
    
    # Plot the original function
    ax.plot(x_vals, y_vals, 'b-', label=f'f(x) = {sp.latex(expr)}')
    
    # Plot the derivative if requested
    if show_deriv and deriv_vals is not None:
        deriv_expr = compute_derivative(expr, order=deriv_order)
        if deriv_order == 1:
            ax.plot(x_vals, deriv_vals, 'r-', label=f"f'(x) = {sp.latex(deriv_expr)}")
        else:
            ax.plot(x_vals, deriv_vals, 'r-', label=f"f^({deriv_order})(x) = {sp.latex(deriv_expr)}")
    
    # Plot the integral if requested
    if show_integ and integ_vals is not None:
        integ_expr = compute_integral(expr)
        ax.plot(x_vals, integ_vals, 'g-', label=f"∫f(x)dx = {sp.latex(integ_expr)} + C")
    
    # Configure the plot
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Function Visualization')
    ax.legend(loc='best')
    ax.grid(True)
    
    # Add axis lines
    ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
    
    fig.tight_layout()
    return fig

def create_separate_plots(expr, x_min, x_max, num_points=1000, show_deriv=True, show_integ=True, deriv_order=1):
    """
    Create separate plots for a function, its derivative, and its integral.
    
    Args:
        expr (sympy.Expr): SymPy expression to plot.
        x_min (float): Minimum x value.
        x_max (float): Maximum x value.
        num_points (int): Number of points to evaluate.
        show_deriv (bool): Whether to show derivatives.
        show_integ (bool): Whether to show integrals.
        deriv_order (int): Order of derivative to compute.
        
    Returns:
        matplotlib.figure.Figure: Figure object containing the plots.
    """
    x_vals, y_vals, deriv_vals, integ_vals = generate_plot_data(
        expr, x_min, x_max, num_points, show_deriv, show_integ, deriv_order
    )
    
    # Determine number of subplots needed
    num_plots = 1
    if show_deriv:
        num_plots += 1
    if show_integ:
        num_plots += 1
    
    # Create the figure with subplots
    fig = Figure(figsize=(10, 3 * num_plots))
    
    # Plot counter
    plot_idx = 1
    
    # Plot the original function
    ax1 = fig.add_subplot(num_plots, 1, plot_idx)
    ax1.plot(x_vals, y_vals, 'b-')
    ax1.set_title(f'Original Function: f(x) = {sp.latex(expr)}')
    ax1.set_xlabel('x')
    ax1.set_ylabel('f(x)')
    ax1.grid(True)
    ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax1.axvline(x=0, color='k', linestyle='-', alpha=0.3)
    plot_idx += 1
    
    # Plot the derivative if requested
    if show_deriv and deriv_vals is not None:
        ax2 = fig.add_subplot(num_plots, 1, plot_idx)
        ax2.plot(x_vals, deriv_vals, 'r-')
        deriv_expr = compute_derivative(expr, order=deriv_order)
        if deriv_order == 1:
            ax2.set_title(f"Derivative: f'(x) = {sp.latex(deriv_expr)}")
        else:
            ax2.set_title(f"Derivative: f^({deriv_order})(x) = {sp.latex(deriv_expr)}")
        ax2.set_xlabel('x')
        ax2.set_ylabel("f'(x)")
        ax2.grid(True)
        ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax2.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        plot_idx += 1
    
    # Plot the integral if requested
    if show_integ and integ_vals is not None:
        ax3 = fig.add_subplot(num_plots, 1, plot_idx)
        ax3.plot(x_vals, integ_vals, 'g-')
        integ_expr = compute_integral(expr)
        ax3.set_title(f"Integral: ∫f(x)dx = {sp.latex(integ_expr)} + C")
        ax3.set_xlabel('x')
        ax3.set_ylabel("∫f(x)dx")
        ax3.grid(True)
        ax3.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax3.axvline(x=0, color='k', linestyle='-', alpha=0.3)
    
    fig.tight_layout()
    return fig
