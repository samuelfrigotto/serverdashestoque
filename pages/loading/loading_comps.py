import dash_bootstrap_components as dbc
from pages.loading import loading
from dash import html, dcc

pageTag = "loading_"
layout = html.Div(
    [
        dcc.Location(id=f"{pageTag}url", refresh=False),
        dbc.Container(
            [
                dbc.Row(
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        "Beta",
                                        className="badge bg-warning text-dark",
                                        style={
                                            "fontSize": "1rem",
                                            "padding": "0.5em 1em",
                                            "position": "absolute",
                                            "top": "20px",
                                            "right": "20px",
                                            "zIndex": "10",
                                        },
                                    ),
                                    html.H2(
                                        "Estamos preparando tudo para você!",
                                        className="mb-4 text-primary text-center",
                                        style={"fontWeight": "bold"},
                                    ),
                                    dcc.Loading(
                                        id="loading_page",
                                        type="default",
                                        children=[
                                            html.Div(
                                                id="ret_loading",
                                                children=[],
                                                style={"height": "100px"},
                                            )
                                        ],
                                    ),
                                    html.Div(
                                        "Aguarde um momento, logo estará tudo pronto para começar.",
                                        className="text-center text-muted mt-3",
                                        style={"fontSize": "1.2rem"},
                                    ),
                                ],
                                className="d-flex flex-column align-items-center justify-content-center position-relative",
                                style={
                                    "minHeight": "80vh",
                                    "background": "linear-gradient(135deg, #eef2f3 0%, #8e9eab 100%)",
                                    "borderRadius": "15px",
                                    "boxShadow": "0 8px 16px rgba(0, 0, 0, 0.2)",
                                    "padding": "2rem",
                                    "position": "relative",
                                },
                            )
                        ],
                        width={"size": 8, "offset": 2},
                    )
                )
            ],
            fluid=True,
            className="py-5",
        )
    ]
)
