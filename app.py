import cmath
from math import pi
from typing import List

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.colors import LinearSegmentedColormap

ij = complex(0, 1)


def generate_roots_of_unity(n: int) -> List[complex]:
    """Generate n roots of unity, including 0.

    Parameters:
    - n (int): The number of roots of unity to generate.

    Returns:
    - List[complex]: A list of complex numbers representing the roots of unity.
    """
    if n > 0:
        return [0] + [cmath.exp(2j * pi * k / n) for k in range(1, n + 1)]
    return [0]  # Default to just include 0 if n <= 0


def from_repr(s: str, radix: complex, symbols: List[complex]) -> complex:
    """Convert a string representation of a number in a given base to a complex
    number.

    Parameters:
    - s (str): The string representation of the number.
    - radix (complex): The base of the numeral system.
    - symbols (List[complex]): The symbols used in the numeral system.

    Returns:
    - complex: The complex number representation of the input string.
    """
    result = 0
    for index, digit in enumerate(s[::-1]):
        result += symbols[int(digit)] * pow(radix, index)
    return result


def to_base(num: int, base: int) -> str:
    """Convert an integer number to its string representation in a given base.

    Parameters:
    - num (int): The number to convert.
    - base (int): The base of the numeral system.

    Returns:
    - str: The string representation of the number in the given base.
    """
    if num == 0:
        return "0"
    rep = ""
    while num > 0:
        remainder = num % base
        rep = str(remainder) + rep
        num = num // base
    return rep


digits_gradient = LinearSegmentedColormap.from_list(
    "blue_green_red",
    ["black", "brown", "purple", "blue", "green", "yellow", "orange", "red", "pink"],
)


def draw(
    ax: plt.Axes,
    symbols: List[complex],
    radix: complex,
    num_points: int = 2048,
    draw_lines: bool = False,
    fixed_limit: int = 400,
) -> None:
    """Draw a visualization of numbers in a complex base numeral system.

    Parameters:
    - ax (plt.Axes): Matplotlib Axes object to draw on.
    - symbols (List[complex]): The symbols used in the numeral system.
    - radix (complex): The base of the numeral system.
    - num_points (int, optional): The number of points to generate and plot.
    - draw_lines (bool, optional): Whether to draw lines between consecutive points.
    - fixed_limit (int, optional): The limit for the x and y axis.
    """
    ax.clear()
    level = len(symbols)
    lengths = [len(to_base(i, level)) for i in range(num_points)]
    max_length = max(lengths)  # To normalize lengths to [0, 1] for colormap
    complex_numbers = [
        from_repr(to_base(i, level), radix, symbols) for i in range(num_points)
    ]
    real_parts = [z.real for z in complex_numbers]
    imaginary_parts = [z.imag for z in complex_numbers]

    # Normalize lengths for color mapping
    normalized_lengths = [length / max_length for length in lengths]

    # Map normalized lengths to the custom blue to red colormap
    colors = digits_gradient(normalized_lengths)

    # Plotting
    if draw_lines:
        for i in range(len(complex_numbers) - 1):
            ax.plot(
                [real_parts[i], real_parts[i + 1]],
                [imaginary_parts[i], imaginary_parts[i + 1]],
                color=colors[i],
            )
    else:
        ax.scatter(
            real_parts, imaginary_parts, c=colors, s=1
        )  # Use custom colormap for point colors

    ax.set_xlabel("Real")
    ax.set_ylabel("Imaginary")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    ax.axis("equal")
    ax.axhline(y=0, color="k", linestyle="-", linewidth=0.5)
    ax.axvline(x=0, color="k", linestyle="-", linewidth=0.5)
    ax.set_xlim(-fixed_limit, fixed_limit)
    ax.set_ylim(-fixed_limit, fixed_limit)


# Streamlit UI
st.title("Complex Base Numeral Systems Navigator")
st.write(
    "Explore how numbers are represented in complex base numeral systems. The color on the plot signifies the number of digits in the representation of each point."
)

# Moving UI elements to the sidebar
input_mode = st.sidebar.radio(
    "Digits Input Mode",
    ["Manual", "Roots of Unity"],
    help="Choose how to input the digits: manually or by generating roots of unity.",
)

symbols = []
if input_mode == "Roots of Unity":
    n_roots = st.sidebar.number_input(
        "Enter n for nth roots of unity (including 0):",
        value=1,
        min_value=1,
        help="Specify the number of roots of unity to include.",
    )
    symbols = generate_roots_of_unity(n_roots)
    st.sidebar.write("Symbols:", symbols)
else:
    symbols_input = st.sidebar.text_input(
        "Enter symbols manually (separate with commas, use 'j' for imaginary unit):",
        "0, 1",
        help="Input symbols manually, separated by commas. Use 'j' for the imaginary unit.",
    )
    symbols = [complex(s.strip()) for s in symbols_input.split(",")]

# Radix Input Mode selection
radix_mode = st.sidebar.radio(
    "Radix Input Mode",
    ["Manual", "Absolute & Angle"],
    help="Select the input mode for the radix: manually enter a complex number or specify its magnitude and angle.",
)

if radix_mode == "Manual":
    radix_input = st.sidebar.text_input(
        "Enter radix manually (e.g., '2', '1+1j'):",
        st.session_state.get("radix_manual", "1+j"),
        help="Manually enter the radix as a complex number.",
    )
    try:
        radix = complex(radix_input)
        st.session_state["radix_manual"] = radix_input
        # Update session state for consistency
        st.session_state["radix_abs"], angle_rad = cmath.polar(radix)
        st.session_state["radix_angle_degrees"] = np.degrees(angle_rad)
    except ValueError:
        st.sidebar.error("Invalid complex number.")
else:
    # Absolute & Angle input
    st.session_state["radix_abs"] = st.sidebar.number_input(
        "Enter radix absolute value:",
        value=float(st.session_state.get("radix_abs", 2.0)),
        format="%f",
        help="Specify the absolute value of the radix.",
    )
    st.session_state["radix_angle_degrees"] = st.sidebar.slider(
        "Radix Angle Degrees",
        min_value=0,
        max_value=360,
        value=int(st.session_state.get("radix_angle_degrees", 90)),
        step=1,
        help="Adjust the angle of the radix in degrees.",
    )
    # Convert angle to radians and calculate complex radix
    radix_angle_rad = np.radians(st.session_state["radix_angle_degrees"])
    radix = st.session_state["radix_abs"] * cmath.exp(1j * radix_angle_rad)

# Configuration sliders
fixed_limit = st.slider(
    "Field Size",
    min_value=50,
    max_value=500,
    value=100,
    help="Adjust the size of the field for the plot.",
)
num_points = st.slider(
    "Number of Points",
    min_value=2**4,
    max_value=2**15,
    value=2**9,
    help="Select the number of points to plot.",
)
draw_lines = st.checkbox(
    "Draw Lines Between Points",
    value=False,
    help="Toggle to draw lines between consecutive points.",
)

fig, ax = plt.subplots()
draw(ax, symbols, radix, num_points, draw_lines, fixed_limit)
st.pyplot(fig)
