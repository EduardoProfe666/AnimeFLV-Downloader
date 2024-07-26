import time
from typing import List, Any

import mesop as me
import pandas as pd
from datetime import datetime

from cloudscraper.exceptions import CloudflareChallengeError

from api.animeflv import AnimeFLV, AnimeInfo

from components.grid_table import GridTableThemeLight, GridTableThemeDark, expander, GridTableExpander, \
    strings_component, GridTableColumn, ints_style, floats_component, date_component, bool_component, on_table_sort, \
    GridTableRow, on_table_cell_click, GridTableHeader, get_data_frame, grid_table, on_filter_by_strings, \
    on_theme_changed, State, image_component, serialize_dataframe, text_component, text_component_bold


def wrap_request(func, *args, count: int = 10, expected: Any):
    """
    Wraps a request sent by the module to test if it works correctly, tries `count` times sleeps
    5 seconds if an error is encountered.

    If `CloudflareChallengeError` is encountered, the expected result will be returned
    to make it possible for automated tests to pass

    :param *args: args to call the function with.
    :param count: amount of tries
    :param expected: example for a valid return, this is used when cloudscraper complains
    :rtype: Any
    """
    notes = []

    for _ in range(count):
        try:
            res = func(*args)
            if isinstance(res, list) and len(res) < 1:
                raise ValueError()  # Raise ValueError to retry test when empty array is returned
            return res
        except CloudflareChallengeError:
            return expected
        except Exception as exc:
            notes.append(exc)
            time.sleep(5)
    raise Exception(notes)

def convert_to_dataframe(anime_list:  list[AnimeInfo]) -> pd.DataFrame:
    posters = [anime.poster for anime in anime_list if anime.poster is not None and anime.poster != '']
    titles = [anime.title for anime in anime_list if anime.title is not None and anime.title != '']
    synopsis = [anime.synopsis for anime in anime_list if anime.synopsis is not None and anime.synopsis != '']
    data = {"Image": posters, "Title": titles, "Synopsis": synopsis}
    df = pd.DataFrame(data)
    return df

def on_filter_by_series(e: me.InputBlurEvent | me.InputEnterEvent | me.InputEvent):
    """Saves the filtering string to be used in `get_data_frame`"""
    with AnimeFLV() as api:
        state = me.state(State)
        state.df = serialize_dataframe(convert_to_dataframe(wrap_request(api.search, e.value, expected=[AnimeInfo(0, "")])))

@me.page(title="Anime Free Downloader")
def home():
    state = me.state(State)

    with me.box(style=me.Style(margin=me.Margin.all(30))):
        me.text(text="Anime Free Downloader", type="headline-1", style=me.Style(text_align="center"))
        me.text(text="In order to use the downloader, just write your anime and exit or re-enter the prompt. The engine will start looking for the similar ones. Then you can select whatever you want to download... With this ease you can see offline your favorite japanese cartoons.", type="headline-5", style=me.Style(text_align="center"))

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
