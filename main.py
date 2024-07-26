import mesop as me

from components.grid_table import GridTableThemeLight, GridTableThemeDark, expander, GridTableExpander, \
    GridTableColumn, on_table_sort, \
    GridTableRow, on_table_cell_click, GridTableHeader, get_data_frame, grid_table, State, image_component, \
    serialize_dataframe, text_component, text_component_bold, anime_info_component
from utils.api_requests import search_animes
from utils.front import convert_to_dataframe_1


def on_filter_by_series(e: me.ClickEvent | me.InputEnterEvent):
    state = me.state(State)
    if state.serie != '':
        state.df = serialize_dataframe(convert_to_dataframe_1(search_animes(state.serie)))
        get_data_frame()


def on_type(e: me.InputBlurEvent | me.InputEnterEvent | me.InputEvent):
    state = me.state(State)
    state.serie = e.value


@me.page(title="Descargar Anime Gratis")
def home():
    state = me.state(State)

    with me.box(style=me.Style(margin=me.Margin.all(30))):
        me.text(text="Descargar Anime Gratis", type="headline-2",
                style=me.Style(text_align="center", width="100%", color='#20A2FE', font_weight="bold", font_family="Consolas"))
        me.text(
            text="Primero busca el anime que desees. El motor buscará los animes con nombres similares, si existen. Luego selecciona el anime que desees, y podrás descargar cualquier episodio subtitulado al español de forma gratuita, desde varios servidores, que incluyen Mega, 1Fichier y Zippyshare",
            type="headline-5", style=me.Style(text_align="center", color='#5474B4', font_family="Apple Chancery"))

        me.input(
            label="Busca tus animes!",
            style=me.Style(width="100%", margin=me.Margin.all(5)),
            on_input=on_type,
            on_enter=on_filter_by_series,
            type="search"
        )

        with me.box(style=me.Style(display="flex", justify_content="end")):
            me.button(
                label="Buscar",
                type="raised",
                disabled=state.serie == '',
                style=me.Style(text_align="right", align_self="end", margin=me.Margin.all(5)),
                on_click=on_filter_by_series
            )

        with me.box(style=me.Style(margin=me.Margin.all(10), border=me.Border.all(
                me.BorderSide(width=3, color="#5474B4", style='groove')
        ),
                                   border_radius=10, )):
            grid_table(
                get_data_frame(),
                header_config=GridTableHeader(sticky=True),
                on_click=on_table_cell_click,
                on_sort=on_table_sort,
                row_config=GridTableRow(
                    columns={
                        "Poster": GridTableColumn(component=image_component),
                        "Título": GridTableColumn(component=text_component_bold, sortable=True),
                        "Sinopsis": GridTableColumn(component=text_component),
                        "Id en AnimeFLV": GridTableColumn(component=text_component_bold, sortable=True),
                    },
                    expander=GridTableExpander(
                        component=anime_info_component,
                        df_row_index=state.expanded_df_row_index,
                    ),
                ),
                sort_column=state.sort_column,
                sort_direction=state.sort_direction,
                theme=GridTableThemeLight(striped=True)
                if state.theme == "light"
                else GridTableThemeDark(striped=True),
            )
