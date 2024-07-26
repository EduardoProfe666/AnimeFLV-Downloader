
import mesop as me

from components.grid_table import GridTableThemeLight, GridTableThemeDark, expander, GridTableExpander, \
    GridTableColumn, on_table_sort, \
    GridTableRow, on_table_cell_click, GridTableHeader, get_data_frame, grid_table, State, image_component, \
    serialize_dataframe, text_component, text_component_bold, actions_component
from utils.api_requests import search_animes
from utils.front import convert_to_dataframe


def on_filter_by_series(e: me.InputBlurEvent | me.InputEnterEvent | me.InputEvent):
    state = me.state(State)
    state.df = serialize_dataframe(convert_to_dataframe(search_animes(e.value)))
    get_data_frame()

@me.page(title="Anime Free Downloader")
def home():
    state = me.state(State)

    with me.box(style=me.Style(margin=me.Margin.all(30))):
        me.text(text="Anime Free Downloader", type="headline-1", style=me.Style(text_align="center", color='green'))
        me.text(text="In order to use the downloader, just write your anime and exit or re-enter the prompt. The engine will start looking for the similar ones. Then you can select whatever you want to download... With this ease you can see offline your favorite japanese cartoons.", type="headline-5", style=me.Style(text_align="center", color='maroon'))

        me.input(
            label="Filter the anime list",
            style=me.Style(width="100%"),
            on_blur=on_filter_by_series,
            on_enter=on_filter_by_series,
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
                    "Actions": GridTableColumn(component=actions_component)
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

        # Used for demonstrating "table button" click example.
        if state.string_output:
            with me.box(
                    style=me.Style(
                        background="#ececec",
                        color="#333",
                        margin=me.Margin(top=20),
                        padding=me.Padding.all(15),
                    )
            ):
                me.text(f"You clicked button: {state.string_output}")
