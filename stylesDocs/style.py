class styleConfig:
    back_pri_color = "#1E1E1E"
    back_sec_color = "#2E2E2E"
    border_color = "#444444"
    text_color = "white"
    select_color = "#aaaaaa"

    def __init__(self, theme: str) -> str:
        self.theme = theme
        match self.theme:
            case "orange":
                self.back_pri_color = "White"
                self.back_sec_color = "#f0f0f0"
                self.border_color = "#cccccc"
                self.text_color = "black"
                self.select_color = "#333333"
            case "blue":
                self.back_pri_color = "#ffffff"
                self.back_sec_color = "#f0f0f0"
                self.border_color = "#cccccc"
                self.text_color = "black"
                self.select_color = "#333333"
            case "dark":
                self.back_pri_color = "#1E1E1E"
                self.back_sec_color = "#2E2E2E"
                self.border_color = "#444444"
                self.text_color = "white"
                self.select_color = "#aaaaaa"
            case "light":
                self.back_pri_color = "#ffffff"
                self.back_sec_color = "#f0f0f0"
                self.border_color = "#cccccc"
                self.text_color = "black"
                self.select_color = "#333333"
            case _:
                self.back_pri_color = "#1E1E1E"
                self.back_sec_color = "#2E2E2E"
                self.border_color = "#444444"
                self.text_color = "white"
                self.select_color = "#aaaaaa"

    def get_css(self) -> str:

        return f"""
        :root {{
            --backPriColor: {self.back_pri_color};
            --backSecColor: {self.back_sec_color};
            --borderColor: {self.border_color};
            --textColor: {self.text_color};
            --selectColor: {self.select_color};
        }}

        body {{
            /*background-color: var(--backPriColor);*/
            color: var(--textColor);
            font-size: 13px; 
        }}

        .card-com-hover .botao-detalhes 
        {{
        display: none;
        position: absolute;
    bottom: 10px;
    right: 10px;
    z-index: 10;
}}

.card-com-hover:hover .botao-detalhes {{
    display: inline-block;
}}
        
        .zoom-out {{
            zoom: 80%;
        }}

        .dash-dropdown {{
            background-color: var(--backSecColor);
            color: var(--textColor);
        }}

        .dash-dropdown .Select-menu-outer {{
            background-color: var(--backSecColor);
        }}

        .dash-dropdown .Select-control {{
            background-color: var(--backSecColor);
            color: var(--textColor);
            border-color: var(--borderColor);
        }}

        .dash-dropdown .Select-option {{
            background-color: var(--backSecColor);
            color: var(--textColor);
        }}

        .dash-dropdown .Select-placeholder {{
            color: var(--selectColor);
        }}

        .dash-dropdown .Select-value-label {{
            color: var(--textColor) !important;
            background-color: var(--backSecColor);
        }}

        .dash-dropdown .Select-menu-outer {{
            background-color: var(--backSecColor);
            color: var(--textColor);
        }}

        .dash-graph {{
            background-color: var(--backPriColor);
            color: var(--textColor);
            border-color: var(--borderColor);
        }}

        input {{
            background-color: var(--backSecColor);
            color: var(--textColor);
            border-color: var(--borderColor);
        }}
        """
