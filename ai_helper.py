import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sympy as sp
import re

# Download NLTK data
try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# Predefined function explanations and math concept definitions
FUNCTION_EXPLANATIONS = {
    "polynomial": {
        "explanation": "Polynomial functions are expressions with variables raised to non-negative integer powers. They're smooth, continuous, and have predictable behavior.",
        "examples": ["x**2 - 4*x + 4", "x**3 - 6*x**2 + 11*x - 6", "2*x**4 - 3*x**2 + 1"],
        "properties": "Polynomials have continuous derivatives of all orders. The highest exponent determines the degree of the polynomial."
    },
    "trigonometric": {
        "explanation": "Trigonometric functions relate angles to the sides of a right triangle. They're periodic and fundamental to wave analysis.",
        "examples": ["sin(x)", "cos(x)", "tan(x)", "sin(x)**2 + cos(x)**2"],
        "properties": "Trigonometric functions are periodic, with sin(x) and cos(x) having a period of 2π. They are widely used to model oscillatory behavior."
    },
    "exponential": {
        "explanation": "Exponential functions have a constant base raised to a variable power. They model growth and decay processes.",
        "examples": ["exp(x)", "2**x", "exp(-x**2)"],
        "properties": "The derivative of e^x is itself. Exponential functions are used to model population growth, compound interest, and radioactive decay."
    },
    "logarithmic": {
        "explanation": "Logarithmic functions are the inverse of exponential functions. They grow very slowly as x increases.",
        "examples": ["log(x)", "log(x, 10)", "ln(x)"],
        "properties": "Logarithms convert multiplication to addition: log(a*b) = log(a) + log(b). They are used to model phenomena that grow quickly at first, then slow down."
    },
    "rational": {
        "explanation": "Rational functions are ratios of polynomials. They can have vertical asymptotes where the denominator equals zero.",
        "examples": ["1/x", "x/(x**2-1)", "(x**2+1)/(x-2)"],
        "properties": "Rational functions may have vertical asymptotes at points where the denominator is zero. They may also have horizontal or slant asymptotes."
    }
}

CALCULUS_CONCEPTS = {
    "derivative": "The derivative measures the rate of change of a function with respect to a variable. Geometrically, it represents the slope of the tangent line to the function at a point.",
    "integral": "The integral represents the accumulation of quantities. Geometrically, the definite integral is the signed area between the function and the x-axis over a given interval.",
    "limit": "A limit describes the value a function approaches as the input approaches a particular value. Limits are fundamental to calculus concepts of continuity, derivatives, and integrals.",
    "continuity": "A function is continuous at a point if there is no abrupt change (jump) at that point. Formally, a function is continuous at a point if the limit equals the function value at that point.",
    "extrema": "Extrema are the maximum and minimum values of a function. They can be found by determining where the derivative equals zero (critical points) and analyzing the second derivative.",
    "inflection": "An inflection point is where the curvature of a function changes sign. It occurs when the second derivative equals zero and changes sign around that point.",
    "series": "A series is the sum of the terms of a sequence. Power series represent functions as infinite sums of powers of the variable, useful for approximating functions."
}

# Function to classify the type of a mathematical function
def classify_function(expr_str):
    expr_str = expr_str.lower()
    
    if any(trig in expr_str for trig in ['sin', 'cos', 'tan', 'sec', 'csc', 'cot']):
        return "trigonometric"
    elif any(exp in expr_str for exp in ['exp', '**']):
        if 'x**' in expr_str and not any(exp in expr_str for exp in ['exp(', 'e**']):
            # Check if it's just a polynomial
            terms = re.findall(r'x\*\*\d+', expr_str)
            if terms and all(re.match(r'x\*\*\d+', term) for term in terms):
                return "polynomial"
        return "exponential"
    elif any(log in expr_str for log in ['log', 'ln']):
        return "logarithmic"
    elif '/' in expr_str:
        return "rational"
    else:
        # Default to polynomial for simple expressions like x^2, x+1, etc.
        return "polynomial"

# Function to get explanation for a specific function
def get_function_explanation(expr_str):
    function_type = classify_function(expr_str)
    explanation = FUNCTION_EXPLANATIONS.get(function_type, {"explanation": "This is a mathematical function."})
    return explanation

# Function to explain a specific calculus concept
def get_calculus_concept(concept):
    concept = concept.lower()
    
    # Using TF-IDF to find the closest concept
    vectorizer = TfidfVectorizer().fit([concept] + list(CALCULUS_CONCEPTS.keys()))
    vectors = vectorizer.transform([concept] + list(CALCULUS_CONCEPTS.keys()))
    
    # Calculate similarity
    similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
    closest_index = np.argmax(similarities)
    
    # If similarity is too low, return a general message
    if similarities[closest_index] < 0.3:
        return "This is a concept in calculus. For more specific information, please ask about derivatives, integrals, limits, continuity, or other calculus topics."
    
    closest_concept = list(CALCULUS_CONCEPTS.keys())[closest_index]
    return CALCULUS_CONCEPTS[closest_concept]

# Function to analyze a mathematical function and provide insights
def analyze_function(expr_str):
    try:
        x = sp.Symbol('x')
        expr = sp.sympify(expr_str)
        
        # Get function type explanation
        explanation = get_function_explanation(expr_str)
        
        # Add some specific insights based on the function
        insights = []
        
        # Check for symmetry
        try:
            if sp.simplify(expr.subs(x, -x) - expr) == 0:
                insights.append("This function is even: f(-x) = f(x). It's symmetric about the y-axis.")
            elif sp.simplify(expr.subs(x, -x) + expr) == 0:
                insights.append("This function is odd: f(-x) = -f(x). It's symmetric about the origin.")
        except:
            pass
            
        # Check for periodicity for trigonometric functions
        if classify_function(expr_str) == "trigonometric":
            insights.append("This is a trigonometric function, which is periodic in nature.")
        
        # Check for roots (zeros)
        try:
            if isinstance(expr, sp.Poly):
                roots = sp.roots(expr)
                if roots:
                    roots_str = ", ".join([str(root) for root in roots])
                    insights.append(f"The function has roots (zeros) at x = {roots_str}.")
        except:
            pass
        
        # Combine all information
        full_explanation = f"{explanation['explanation']}\n\n"
        
        if insights:
            full_explanation += "Insights:\n" + "\n".join(insights) + "\n\n"
        
        if 'examples' in explanation and explanation['examples']:
            full_explanation += "Similar functions:\n" + ", ".join(explanation['examples']) + "\n\n"
        
        if 'properties' in explanation and explanation['properties']:
            full_explanation += f"Properties: {explanation['properties']}"
        
        return full_explanation
        
    except Exception as e:
        return f"I couldn't fully analyze this function due to its complexity. Basic error: {str(e)}"

# Function to suggest functions to explore
def suggest_functions():
    categories = list(FUNCTION_EXPLANATIONS.keys())
    suggestions = []
    
    for category in categories:
        if 'examples' in FUNCTION_EXPLANATIONS[category]:
            suggestions.append({
                'category': category.capitalize(),
                'example': FUNCTION_EXPLANATIONS[category]['examples'][0]
            })
    
    return suggestions

# Function to answer a question about calculus
def answer_calculus_question(question):
    # List of keywords to match with calculus concepts
    concept_keywords = {
        'derivative': ['derivative', 'differentiation', 'rate of change', 'slope'],
        'integral': ['integral', 'integration', 'area', 'antiderivative'],
        'limit': ['limit', 'approaching', 'tends to'],
        'continuity': ['continuous', 'continuity', 'discontinuity'],
        'extrema': ['maximum', 'minimum', 'extrema', 'extreme', 'peak', 'valley'],
        'inflection': ['inflection', 'concavity', 'curvature'],
        'series': ['series', 'taylor', 'maclaurin', 'power series']
    }
    
    question = question.lower()
    
    # Check for matches with concepts
    for concept, keywords in concept_keywords.items():
        if any(keyword in question for keyword in keywords):
            return get_calculus_concept(concept)
    
    # If no specific concept is found, provide a general response
    return ("Calculus is the mathematical study of continuous change and consists of two main branches: "
            "differential calculus (concerning rates of change and slopes of curves) and "
            "integral calculus (concerning accumulation of quantities and areas under curves). "
            "For more specific information, ask about derivatives, integrals, limits, or other calculus concepts.")