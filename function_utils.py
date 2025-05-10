import numpy as np
import sympy as sp
from scipy import integrate, misc
import re

def parse_function(function_str):
    """
    Parse a string representation of a mathematical function.
    
    Args:
        function_str (str): String representation of a function in Python syntax.
        
    Returns:
        sympy.Expr: SymPy expression representing the function.
    """
    # Define x as a sympy symbol
    x = sp.Symbol('x')
    
    # Clean up the input
    function_str = function_str.strip()
    
    # Replace common math functions with their sympy equivalents
    function_str = re.sub(r'\bsin\b', 'sp.sin', function_str)
    function_str = re.sub(r'\bcos\b', 'sp.cos', function_str)
    function_str = re.sub(r'\btan\b', 'sp.tan', function_str)
    function_str = re.sub(r'\blog\b', 'sp.log', function_str)
    function_str = re.sub(r'\bexp\b', 'sp.exp', function_str)
    function_str = re.sub(r'\bsqrt\b', 'sp.sqrt', function_str)
    function_str = re.sub(r'\babs\b', 'sp.Abs', function_str)
    
    # Ensure ** is used for exponentiation
    function_str = function_str.replace('^', '**')
    
    try:
        # Use sympy's sympify to parse the expression
        expr = sp.sympify(function_str, locals={'x': x})
        return expr
    except Exception as e:
        raise ValueError(f"Error parsing function: {str(e)}")

def function_to_callable(expr):
    """
    Convert a SymPy expression to a callable Python function.
    
    Args:
        expr (sympy.Expr): SymPy expression.
        
    Returns:
        callable: Python function that evaluates the expression.
    """
    x = sp.Symbol('x')
    return sp.lambdify(x, expr, 'numpy')

def compute_derivative(expr, order=1):
    """
    Compute the derivative of a SymPy expression.
    
    Args:
        expr (sympy.Expr): SymPy expression to differentiate.
        order (int): Order of the derivative.
        
    Returns:
        sympy.Expr: Derivative expression.
    """
    x = sp.Symbol('x')
    derivative = expr
    for _ in range(order):
        derivative = sp.diff(derivative, x)
    return derivative

def numerical_derivative(func, x, order=1, dx=1e-6):
    """
    Compute the numerical derivative of a function at x.
    
    Args:
        func (callable): Function to differentiate.
        x (float or array): Point(s) at which to evaluate the derivative.
        order (int): Order of the derivative.
        dx (float): Step size for finite difference.
        
    Returns:
        float or array: Derivative evaluated at x.
    """
    return misc.derivative(func, x, dx=dx, n=order)

def compute_integral(expr, lower_bound=None, upper_bound=None):
    """
    Compute the indefinite or definite integral of a SymPy expression.
    
    Args:
        expr (sympy.Expr): SymPy expression to integrate.
        lower_bound (float, optional): Lower bound for definite integral.
        upper_bound (float, optional): Upper bound for definite integral.
        
    Returns:
        sympy.Expr: Integral expression.
    """
    x = sp.Symbol('x')
    
    if lower_bound is not None and upper_bound is not None:
        # Definite integral
        result = sp.integrate(expr, (x, lower_bound, upper_bound))
        return result
    else:
        # Indefinite integral
        return sp.integrate(expr, x)

def numerical_integral(func, lower_bound, upper_bound):
    """
    Compute the numerical definite integral of a function.
    
    Args:
        func (callable): Function to integrate.
        lower_bound (float): Lower bound of integration.
        upper_bound (float): Upper bound of integration.
        
    Returns:
        float: Definite integral value.
    """
    result, error = integrate.quad(func, lower_bound, upper_bound)
    return result

def evaluate_function(func, x_range):
    """
    Evaluate a function over a range of x values.
    
    Args:
        func (callable): Function to evaluate.
        x_range (array): Array of x values.
        
    Returns:
        array: Function values.
    """
    try:
        return func(x_range)
    except Exception as e:
        # Handle potential numerical errors
        if isinstance(x_range, np.ndarray):
            result = np.zeros_like(x_range, dtype=float)
            for i, x in enumerate(x_range):
                try:
                    result[i] = func(x)
                except:
                    result[i] = np.nan
            return result
        else:
            return np.nan
