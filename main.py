import mesop as me

from components.grid_table import GridTableThemeLight, GridTableThemeDark, expander, GridTableExpander, \
    GridTableColumn, on_table_sort, \
    GridTableRow, on_table_cell_click, GridTableHeader, get_data_frame, grid_table, State, image_component, \
    serialize_dataframe, text_component, text_component_bold
from utils.api_requests import search_animes
from utils.front import convert_to_dataframe


def on_filter_by_series(e: me.ClickEvent | me.InputEnterEvent):
    state = me.state(State)
    if state.serie != '':
        state.df = serialize_dataframe(convert_to_dataframe(search_animes(state.serie)))
        get_data_frame()


def on_type(e: me.InputBlurEvent | me.InputEnterEvent | me.InputEvent):
    state = me.state(State)
    state.serie = e.value


@me.page(title="Anime Free Downloader")
def home():
    state = me.state(State)

    with me.box(style=me.Style(margin=me.Margin.all(30))):
        me.text(text="Anime Free Downloader", type="headline-2",
                style=me.Style(text_align="center", width="100%", color='#20A2FE', font_weight="bold", font_family="Consolas"))
        me.text(
            text="In order to use the downloader, fist search the desired anime. The engine will start looking for the similar ones. Then you can select it, and then download any of its episodes from different servers... With this ease you can see offline your favorite japanese cartoons.",
            type="headline-5", style=me.Style(text_align="center", color='#5474B4', font_family="Apple Chancery"))

        me.input(
            label="Search your animes!",
            style=me.Style(width="100%", margin=me.Margin.all(5)),
            on_input=on_type,
            on_enter=on_filter_by_series,
            type="search"
        )

        with me.box(style=me.Style(display="flex", justify_content="end")):
            me.button(
                label="Search",
                type="raised",
                disabled=state.serie == '',
                style=me.Style(text_align="right", align_self="end", margin=me.Margin.all(5)),
                on_click=on_filter_by_series
            )

        grid_table(
            get_data_frame(),
            header_config=GridTableHeader(sticky=True),
            on_click=on_table_cell_click,
            on_sort=on_table_sort,
            row_config=GridTableRow(
                columns={
                    "Image": GridTableColumn(component=image_component),
                    "Title": GridTableColumn(component=text_component_bold, sortable=True),
                    "Synopsis": GridTableColumn(component=text_component),
                    # "Bools": GridTableColumn(component=bool_component),
                    # "Date Times": GridTableColumn(component=date_component),
                    # "Floats": GridTableColumn(component=floats_component),
                    # "Ints": GridTableColumn(style=ints_style, sortable=True),
                    # "Strings": GridTableColumn(
                    #     component=strings_component, sortable=True
                    # ),
                },
                expander=GridTableExpander(
                    component=expander,
                    df_row_index=state.expanded_df_row_index,
                ),
            ),
            sort_column=state.sort_column,
            sort_direction=state.sort_direction,
            theme=GridTableThemeLight(striped=True)
            if state.theme == "light"
            else GridTableThemeDark(striped=True),
        )
