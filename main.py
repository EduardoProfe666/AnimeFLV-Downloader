import mesop as me
import pandas as pd
from datetime import datetime

from components.grid_table import GridTableThemeLight, GridTableThemeDark, expander, GridTableExpander, \
    strings_component, GridTableColumn, ints_style, floats_component, date_component, bool_component, on_table_sort, \
    GridTableRow, on_table_cell_click, GridTableHeader, get_data_frame, grid_table, on_filter_by_strings, \
    on_theme_changed, State, set_dataframe, image_component

set_dataframe(pd.DataFrame(
  data={
    "Image": ['https://animeflv.net/uploads/animes/covers/2536.jpg', 'https://animeflv.net/uploads/animes/covers/1620.jpg', 'https://animeflv.net/uploads/animes/covers/2731.jpg'],
    "Index": [3, 2, 1],
    "Bools": [True, False, True],
    "Ints": [101, 90, -55],
    "Floats": [1002.3, 4.5, -1050203.021],
    "Date Times": [
      pd.Timestamp("20180310"),
      pd.Timestamp("20230310"),
      datetime(2023, 1, 1, 12, 12, 1),
    ],
    "Strings": ["Fuck", "World", "!"],
  }
))

@me.page(title="AnimeFree-Downloader")
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
            on_blur=on_filter_by_strings,
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
                    "Bools": GridTableColumn(component=bool_component),
                    "Date Times": GridTableColumn(component=date_component),
                    "Floats": GridTableColumn(component=floats_component),
                    "Ints": GridTableColumn(style=ints_style, sortable=True),
                    "Strings": GridTableColumn(
                        component=strings_component, sortable=True
                    ),
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
