import streamlit.components.v1 as components
from pathlib import Path


def load_component_css():
    # Circle styles live in Ui/circles.css (NOT style.css,
    # which is only for the main page).
    css_path = Path(__file__).parent / "circles.css"

    if css_path.exists():
        return css_path.read_text(encoding="utf-8")

    return ""


# - WATER INTAKE CIRCLE -

def render_water_circle(water, goal):
    percentage = min(max(water / goal, 0), 1) if goal > 0 else 0
    wave_y = round(155 - percentage * 130, 2)
    text_color = "#FFFFFF" if percentage > 0.60 else "#24563A"

    css = load_component_css()

    # width/height are set directly on the <svg> so the circle
    # keeps its size even if the CSS file fails to load.
    html = f"""
    <html>
    <head>
        <style>
            {css}
            body {{
                margin: 0;
                padding: 0;
                background: transparent;
            }}
        </style>
    </head>
    <body>
        <div class="hm-circle-wrap">
            <svg class="hm-circle-svg"
                 width="200" height="200"
                 viewBox="0 0 180 180"
                 xmlns="http://www.w3.org/2000/svg">

                <defs>
                    <clipPath id="waterClip">
                        <circle cx="90" cy="90" r="65"/>
                    </clipPath>
                </defs>

                <circle cx="90" cy="90" r="68"
                        fill="#F1F8F3"
                        stroke="#CDE7D6"
                        stroke-width="2"/>

                <g clip-path="url(#waterClip)">
                    <path
                        d="M-10 {wave_y}
                           Q20 {wave_y - 8} 65 {wave_y}
                           T110 {wave_y}
                           T190 {wave_y}
                           L190 190 L-10 190 Z"
                        fill="#4BA3DF"/>

                    <path
                        d="M-10 {wave_y + 8}
                           Q20 {wave_y} 65 {wave_y + 8}
                           T110 {wave_y + 8}
                           T190 {wave_y + 8}
                           L190 190 L-10 190 Z"
                        fill="#339DD4"
                        opacity="0.55"/>
                </g>

                <circle cx="90" cy="90" r="65"
                        fill="none"
                        stroke="#CDE7D6"
                        stroke-width="2"/>

                <text x="90" y="86"
                      text-anchor="middle"
                      font-family="Arial, sans-serif"
                      font-size="23"
                      font-weight="bold"
                      fill="{text_color}">{water:.1f} L</text>

                <text x="90" y="109"
                      text-anchor="middle"
                      font-family="Arial, sans-serif"
                      font-size="13"
                      fill="{text_color}">of {goal:.1f} L</text>
            </svg>
        </div>
    </body>
    </html>
    """

    components.html(html, height=205, scrolling=False)

# - EXERCISE CIRCLE -

def render_exercise_circle(exercise_minutes, goal):
    percentage = (
        min(max(exercise_minutes / goal, 0), 1)
        if goal > 0 else 0
    )
    radius = 65
    circumference = 2 * 3.14159265 * radius
    offset = circumference * (1 - percentage)

    css = load_component_css()

    html = f"""
    <html>
    <head>
        <style>
            {css}
            body {{
                margin: 0;
                padding: 0;
                background: transparent;
            }}
        </style>
    </head>
    <body>
        <div class="hm-circle-wrap">
            <svg class="hm-circle-svg"
                 width="200" height="200"
                 viewBox="0 0 180 180"
                 xmlns="http://www.w3.org/2000/svg">

                <circle cx="90" cy="90" r="{radius}"
                        fill="#F1F8F3"
                        stroke="#E0EAE3"
                        stroke-width="12"/>

                <circle cx="90" cy="90" r="{radius}"
                        fill="none"
                        stroke="#47A875"
                        stroke-width="12"
                        stroke-linecap="round"
                        stroke-dasharray="{circumference}"
                        stroke-dashoffset="{offset}"
                        transform="rotate(-90 90 90)"/>

                <text x="90" y="86"
                      text-anchor="middle"
                      font-family="Arial, sans-serif"
                      font-size="23"
                      font-weight="bold"
                      fill="#24563A">{exercise_minutes} min</text>

                <text x="90" y="109"
                      text-anchor="middle"
                      font-family="Arial, sans-serif"
                      font-size="13"
                      fill="#607768">of {goal} min</text>
            </svg>
        </div>
    </body>
    </html>
    """

    components.html(html, height=205, scrolling=False)