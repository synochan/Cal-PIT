import streamlit as st
import sympy as sp
import numpy as np
from function_utils import parse_function, compute_derivative, compute_integral
from visualization import create_combined_plot, create_separate_plots

# Set page config
st.set_page_config(
    page_title="Calculus Visualizer",
    page_icon="📈",
    layout="wide",
)

st.title("Calculus Visualizer")
st.markdown("""
This application allows you to visualize mathematical functions, their derivatives, and integrals.
Enter a function below and adjust the parameters to see how it behaves.
""")

# Initialize session state for default values
if 'function_input' not in st.session_state:
    st.session_state.function_input = "x**2 - 4*x + 4"
if 'x_min' not in st.session_state:
    st.session_state.x_min = -10.0
if 'x_max' not in st.session_state:
    st.session_state.x_max = 10.0
if 'derivative_order' not in st.session_state:
    st.session_state.derivative_order = 1

# Sidebar for inputs
with st.sidebar:
    st.header("Function Input")
    
    function_input = st.text_area(
        "Enter a mathematical function in terms of x:",
        value=st.session_state.function_input,
        height=100,
        help="Example: x**2 - 4*x + 4 or sin(x) + cos(x)"
    )
    
    st.markdown("""
    **Function Syntax Help:**
    - Use `x` as the variable
    - Use `**` for powers (e.g., `x**2` for x²)
    - Available functions: `sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `abs`
    - Example: `sin(x)`, `x**2 - 4*x + 4`, `exp(-x**2)`
    """)
    
    st.header("Plot Settings")
    
    x_min = st.number_input(
        "Minimum x value:", 
        value=st.session_state.x_min,
        step=1.0
    )
    
    x_max = st.number_input(
        "Maximum x value:", 
        value=st.session_state.x_max,
        step=1.0
    )
    
    # Correct the range if min > max
    if x_min >= x_max:
        st.warning("Minimum x value must be less than maximum x value.")
        x_max = x_min + 1.0
    
    st.header("Derivative & Integral Options")
    
    show_derivative = st.checkbox("Show Derivative", value=True)
    
    if show_derivative:
        derivative_order = st.slider(
            "Derivative Order:", 
            min_value=1, 
            max_value=5, 
            value=st.session_state.derivative_order,
            step=1
        )
    else:
        derivative_order = 1
    
    show_integral = st.checkbox("Show Integral", value=True)
    
    plot_type = st.radio(
        "Plot Type:",
        options=["Combined", "Separate"],
        index=0
    )

# Update session state
st.session_state.function_input = function_input
st.session_state.x_min = x_min
st.session_state.x_max = x_max
st.session_state.derivative_order = derivative_order

# Main content area
try:
    # Parse the function
    expr = parse_function(function_input)
    
    # Display the parsed expression in LaTeX
    st.header("Parsed Function")
    st.latex(f"f(x) = {sp.latex(expr)}")
    
    # Display symbolic derivatives if requested
    if show_derivative:
        st.header(f"Derivative (Order {derivative_order})")
        deriv_expr = compute_derivative(expr, order=derivative_order)
        st.latex(f"f^{{{derivative_order}}}(x) = {sp.latex(deriv_expr)}")
    
    # Display symbolic integral if requested
    if show_integral:
        st.header("Indefinite Integral")
        integ_expr = compute_integral(expr)
        st.latex(f"\\int f(x) \\, dx = {sp.latex(integ_expr)} + C")
    
    # Create and display plot
    st.header("Visualization")
    
    if plot_type == "Combined":
        fig = create_combined_plot(
            expr, 
            x_min, 
            x_max, 
            show_deriv=show_derivative, 
            show_integ=show_integral,
            deriv_order=derivative_order
        )
    else:  # Separate plots
        fig = create_separate_plots(
            expr, 
            x_min, 
            x_max, 
            show_deriv=show_derivative, 
            show_integ=show_integral,
            deriv_order=derivative_order
        )
    
    st.pyplot(fig)
    
    # Additional explanation
    st.header("About the Visualization")
    st.markdown("""
    - **Blue line**: Original function f(x)
    - **Red line**: Derivative f'(x) (or higher-order derivative)
    - **Green line**: Indefinite integral ∫f(x)dx
    
    You can zoom in/out and pan the plots using the controls in the top-right corner of the plot.
    """)
    
    # Educational information
    with st.expander("Learn about Derivatives and Integrals"):
        st.markdown("""
        ## Derivatives
        
        The derivative of a function represents its rate of change. 
        Geometrically, it corresponds to the slope of the tangent line at a given point.
        
        - First derivative (f'(x)): Rate of change of the original function
        - Second derivative (f''(x)): Rate of change of the first derivative (acceleration)
        - Higher-order derivatives: Continuing this pattern
        
        ## Integrals
        
        The integral of a function can be thought of as the area under its curve.
        
        - Indefinite integral (∫f(x)dx): A function whose derivative is the original function
        - Definite integral (∫[a,b]f(x)dx): The signed area under the curve from a to b
        
        ## Relationships
        
        - The derivative of the integral of a function gives the original function
        - The integral of the derivative of a function gives the original function (plus a constant)
        """)

except ValueError as e:
    st.error(f"Error: {str(e)}")
    st.info("Please check your function syntax and try again.")
except Exception as e:
    st.error(f"An unexpected error occurred: {str(e)}")
    st.info("Please try a different function or adjust the range of x values.")
