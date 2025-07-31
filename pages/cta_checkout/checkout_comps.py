from dash import html, dcc
import dash_bootstrap_components as dbc
from pages.cta_checkout import checkout
from assets.static import packCode
import dash_daq as daq

pageTag = "checkout_"
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
                            href="/cta_checkout/resumo",
                            active="exact",
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Montador",
                            id=f"{pageTag}lnk_montador",
                            href="/cta_checkout/montador",
                            active="exact",
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Conferente",
                            id=f"{pageTag}lnk_conferente",
                            href="/cta_checkout/conferente",
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
