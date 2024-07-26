from typing import List

import mesop as me
import pandas as pd
from datetime import datetime
from api.animeflv import AnimeFLV, AnimeInfo

from components.grid_table import GridTableThemeLight, GridTableThemeDark, expander, GridTableExpander, \
    strings_component, GridTableColumn, ints_style, floats_component, date_component, bool_component, on_table_sort, \
    GridTableRow, on_table_cell_click, GridTableHeader, get_data_frame, grid_table, on_filter_by_strings, \
    on_theme_changed, State, image_component, serialize_dataframe


def convert_to_dataframe(anime_list:  list[AnimeInfo]) -> pd.DataFrame:
    posters = [anime.poster for anime in anime_list if anime.poster is not None or '']
    print(posters)
    data = {"Image": posters}
    df = pd.DataFrame(data)
    return df

def on_filter_by_series(e: me.InputBlurEvent | me.InputEnterEvent):
    """Saves the filtering string to be used in `get_data_frame`"""
    with AnimeFLV() as api:
        state = me.state(State)
        state.df = serialize_dataframe(convert_to_dataframe(api.search(e.value)))

@me.page(title="Anime Free Downloader")
def home():
    state = me.state(State)

    with me.box(style=me.Style(margin=me.Margin.all(30))):
        me.select(
            label="Theme",
            options=[
                me.SelectOption(label="Light", value="light"),
                me.SelectOption(label="Dark", value="dark"),
            ],
            on_selection_change=on_theme_changed,
        )

        # Simple example of filtering a data table. This is implemented separately of the
        # grid table component. For simplicity, we only filter against a single column.
        me.input(
            label="Filter by Strings column",
            style=me.Style(width="100%"),
            on_blur=on_filter_by_series,
            on_enter=on_filter_by_strings,
        )

        # Grid Table demonstrating all features.
        grid_table(
            get_data_frame(),
            header_config=GridTableHeader(sticky=True),
            on_click=on_table_cell_click,
            on_sort=on_table_sort,
            row_config=GridTableRow(
                columns={
                    "Image": GridTableColumn(component=image_component),
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
