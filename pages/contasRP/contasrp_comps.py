from dash import html, dcc
import dash_bootstrap_components as dbc
from pages.contasrp import biexpress
from assets.static import packCode
import dash_daq as daq

pageTag = "contasrp_"
layout = html.Div(
    [
        dcc.Location(id=f"{pageTag}url", refresh=False),
        html.Div(
            packCode.Navbar(
                [
                    dbc.NavItem(
                        html.Div(
                            [
                                html.Div(html.I(className="bi bi-sun-fill")),
                                html.Div(
                                    daq.BooleanSwitch(
                                        id="theme_selector",
                                        on=False,
                                        style={
                "paddingRight":"5px",
                "paddingLeft":"5px",
            }
                                    )
                                ),
                                html.Div(html.I(className="bi bi-moon-fill")),
                            ],
                            style={
                "display": "flex",
                "flexDirection": "row",
                "alignItems": "center",
                "textAlign": "center",
                "paddingRight":"5px",
                "paddingLeft":"5px",
            },className="p-2"
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Home",
                            id=f"{pageTag}lnk_home",
                            href="/contasrp/resumo",
                            active="exact",
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Cubagem",
                            id=f"{pageTag}lnk_cubagem",
                            href="/contasrp/cubagem",
                            active="exact",
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Entregas",
                            id=f"{pageTag}lnk_entregas",
                            href="/contasrp/entregas",
                            active="exact",
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "KM",
                            id=f"{pageTag}lnk_km",
                            href="/contasrp/km",
                            active="exact",
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Tempo Entregas",
                            id=f"{pageTag}lnk_temp_entregas",
                            href="/contasrp/temp_entregas",
                            active="exact",
                        )
                    ),
                    
                ]
            ),
            className="mb-1",
        ),
        html.Div(id=f"{pageTag}content"),
    ]
)
