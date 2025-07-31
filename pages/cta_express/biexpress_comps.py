from dash import html, dcc
import dash_bootstrap_components as dbc
from pages.cta_express import biexpress
from assets.static import packCode
import dash_daq as daq

pageTag = "expressBI_"
layout = html.Div(
    [
        dcc.Location(id=f"{pageTag}url", refresh=False),
        html.Div(
            packCode.Navbar(
                [
                    dbc.NavItem(
                        dbc.NavLink(
                            "Home",
                            id=f"{pageTag}lnk_home",
                            href="/cta_express/resumo",
                            active="exact",
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Cubagem",
                            id=f"{pageTag}lnk_cubagem",
                            href="/cta_express/cubagem",
                            active="exact",
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Entregas",
                            id=f"{pageTag}lnk_entregas",
                            href="/cta_express/entregas",
                            active="exact",
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "KM",
                            id=f"{pageTag}lnk_km",
                            href="/cta_express/km",
                            active="exact",
                        )
                    ),
                    #dbc.NavItem(
                    #    dbc.NavLink(
                    #        "Estoque",
                    #        id=f"{pageTag}lnk_estoque",
                    #        href="/cta_express/estoque",
                    #        active="exact",
                    #    )
                    #),
                    # dbc.NavItem(
                    #    dbc.NavLink(
                    #        "Tempo Entregas",
                    #        id=f"{pageTag}lnk_temp_entregas",
                    #        href="/cta_express/temp_entregas",
                    #        active="exact",
                    #    )
                    # ),
                ]
            ),
            className="mb-1",
            style={
                "position": "sticky",
                "top": "0px",
                "zIndex": "1000",
            },
        ),
        html.Div(id=f"{pageTag}content"),
    ]
)
