"""Pure Mesop Table built using CSS Grid.

Functionality:

- Column sorting
- Header styles
- Row styles
- Cell styles
- Cell templating
- Row click
- Expandable rows
- Sticky header
- Filtering (technically not built-in to the grid table component)

TODOs:

- Pagination
- Sticky column
- Control column width
- Column filtering within grid table
"""

from dataclasses import dataclass, field
from datetime import datetime
from io import StringIO
from typing import Any, Callable, Literal, Protocol, List

import pandas as pd

import mesop as me

from api.animeflv import AnimeInfo, DownloadLinkInfo
from utils.api_requests import get_anime_episode_info_download
from utils.front import convert_to_dataframe_2

SortDirection = Literal["asc", "desc"]


def serialize_dataframe(df: pd.DataFrame) -> str:
    return df.to_json(orient="split")


def deserialize_dataframe(json_str: str) -> pd.DataFrame:
    json_io = StringIO(json_str)
    return pd.read_json(json_io, orient="split")


@me.stateclass
class State:
    expanded_df_row_index: int | None = None
    sort_column: str
    sort_direction: SortDirection = "asc"
    string_output: str
    table_filter: str
    serie: str
    theme: str = "light"
    df: str = serialize_dataframe(pd.DataFrame(
        data={
            "Poster": [],
            "Título": [],
            "Sinopsis": [],
            "Nombre": []
        }
    ))


@dataclass(kw_only=True)
class GridTableHeader:
    """Configuration for the table header

    Attributes:

      sticky: Enables sticky headers
      style: Overrides default header styles
    """

    sticky: bool = False
    style: Callable | None = None


@dataclass(kw_only=True)
class GridTableColumn:
    """Configuration for a table column

    Attributes:

      component: Custom rendering for the table cell
      sortable: Whether this column can be sorted or not
      style: Custom styling for the table cell
    """

    component: Callable | None = None
    sortable: bool = False
    style: Callable | None = None


@dataclass(kw_only=True)
class GridTableExpander:
    """Configuration for expander table row

    Currently only one row can be expanded at a time.

    Attributes:

      component: Custom rendering for the table row
      df_row_index: DataFrame row that is expanded.
      style: Custom styling for the expanded row
    """

    component: Callable | None = None
    df_row_index: int | None = None
    style: Callable | None = None


@dataclass(kw_only=True)
class GridTableRow:
    """Configuration for the table's rows.

    Attributes:

      columns: A map of column name to column specific configuration
      expander: Configuration for expanded row
      style: Custom styles at the row level.
    """

    columns: dict[str, GridTableColumn] = field(default_factory=lambda: {})
    expander: GridTableExpander = field(
        default_factory=lambda: GridTableExpander()
    )
    style: Callable | None = None


@dataclass(kw_only=True)
class GridTableCellMeta:
    """Metadata that is passed into style/component/expander callables.

    This metadata can be used to display things in custom ways based on the data.
    """

    df_row_index: int
    df_col_index: int
    name: str
    row_index: int
    value: Any


class GridTableTheme(Protocol):
    """Interface for theming the grid table"""

    def header(self, sortable: bool = False) -> me.Style:
        return me.Style()

    def sort_icon(self, current_column: str, sort_column: str) -> me.Style:
        return me.Style()

    def cell(self, cell_meta: GridTableCellMeta) -> me.Style:
        return me.Style()

    def expander(self, df_row_index: int) -> me.Style:
        return me.Style()


class GridTableThemeDark(GridTableTheme):
    _HEADER_BG: str = "#28313e"
    _CELL_BG: str = "#141d2c"
    _CELL_BG_ALT: str = "#02060c"
    _COLOR: str = "#fff"
    _PADDING: me.Padding = me.Padding.all(10)
    _BORDER: me.Border = me.Border.all(
        me.BorderSide(width=1, style="solid", color="rgba(255, 255, 255, 0.16)")
    )

    def __init__(self, striped: bool = False):
        self.striped = striped

    def header(self, sortable: bool = False) -> me.Style:
        return me.Style(
            background=self._HEADER_BG,
            color=self._COLOR,
            cursor="pointer" if sortable else "default",
            padding=self._PADDING,
            border=self._BORDER,
        )

    def sort_icon(self, current_column: str, sort_column: str) -> me.Style:
        return me.Style(
            color="rgba(255, 255, 255, .8)"
            if sort_column == current_column
            else "rgba(255, 255, 255, .4)",
            # Hack to make the icon align correctly. Will break if user changes the
            # font size with custom styles.
            height=16,
        )

    def cell(self, cell_meta: GridTableCellMeta) -> me.Style:
        return me.Style(
            background=self._CELL_BG_ALT
            if self.striped and cell_meta.row_index % 2
            else self._CELL_BG,
            color=self._COLOR,
            padding=self._PADDING,
            border=self._BORDER,
        )

    def expander(self, df_row_index: int) -> me.Style:
        return me.Style(
            background=self._CELL_BG,
            color=self._COLOR,
            padding=self._PADDING,
            border=self._BORDER,
        )


class GridTableThemeLight(GridTableTheme):
    _HEADER_BG: str = "#fff"
    _CELL_BG: str = "#fff"
    _CELL_BG_ALT: str = "#f6f6f6"
    _COLOR: str = "#000"
    _PADDING: me.Padding = me.Padding.all(10)
    _HEADER_BORDER: me.Border = me.Border(
        bottom=me.BorderSide(width=1, style="solid", color="#b2b2b2")
    )
    _CELL_BORDER: me.Border = me.Border(
        bottom=me.BorderSide(width=1, style="solid", color="#d9d9d9")
    )

    def __init__(self, striped: bool = False):
        self.striped = striped

    def header(self, sortable: bool = False) -> me.Style:
        return me.Style(
            background=self._HEADER_BG,
            color=self._COLOR,
            cursor="pointer" if sortable else "default",
            font_weight="bold",
            padding=self._PADDING,
            border=self._HEADER_BORDER,
        )

    def sort_icon(self, current_column: str, sort_column: str) -> me.Style:
        return me.Style(
            color="rgba(0, 0, 0, .8)"
            if sort_column == current_column
            else "rgba(0, 0, 0, .4)",
            # Hack to make the icon align correctly. Will break if user changes the
            # font size with custom styles.
            height=18,
        )

    def cell(self, cell_meta: GridTableCellMeta) -> me.Style:
        return me.Style(
            background=self._CELL_BG_ALT
            if self.striped and cell_meta.row_index % 2
            else self._CELL_BG,
            color=self._COLOR,
            padding=self._PADDING,
            border=self._CELL_BORDER,
        )

    def expander(self, df_row_index: int) -> me.Style:
        return me.Style(
            background=self._CELL_BG,
            color=self._COLOR,
            padding=self._PADDING,
            border=self._CELL_BORDER,
        )


def get_data_frame():
    """Helper function to get a sorted/filtered version of the main data frame.

    One drawback of this approach is that we sort/filter the main data frame with every
    refresh, which may not be efficient for larger data frames.
    """
    state = me.state(State)

    # Sort the data frame if sorting is enabled.
    if state.sort_column:
        sorted_df = deserialize_dataframe(state.df).sort_values(
            by=state.sort_column, ascending=state.sort_direction == "asc"
        )
    else:
        sorted_df = deserialize_dataframe(state.df)

    # Simple filtering by the Strings column.
    if state.table_filter:
        return sorted_df[
            sorted_df["Title"].str.lower().str.contains(state.table_filter.lower())
        ]
    else:
        return sorted_df


def on_theme_changed(e: me.SelectSelectionChangeEvent):
    """Changes the theme of the grid table"""
    state = me.state(State)
    state.theme = e.value


def on_filter_by_strings(e: me.InputBlurEvent | me.InputEnterEvent):
    """Saves the filtering string to be used in `get_data_frame`"""
    state = me.state(State)
    state.table_filter = e.value


def on_table_cell_click(e: me.ClickEvent):
    """If the table cell is clicked, show the expanded content."""
    state = me.state(State)
    df_row_index, _ = map(int, e.key.split("-"))
    if state.expanded_df_row_index == df_row_index:
        state.expanded_df_row_index = None
    else:
        state.expanded_df_row_index = df_row_index


def on_table_sort(e: me.ClickEvent):
    """Handles the table sort event by saving the sort information to be used in `get_data_frame`"""
    state = me.state(State)
    column, direction = e.key.split("-")
    if state.sort_column == column:
        state.sort_direction = "asc" if direction == "desc" else "desc"
    else:
        state.sort_direction = direction  # type: ignore
    state.sort_column = column


def expander(df_row_index: int):
    """Rendering logic for expanded row.

    Here we just display the row data in two columns as text inputs.

    But you can do more advanced things, such as:

    - rendering another table inside the table
    - fetching data to show drill down data
    - add a form for data entry
    """
    state = me.state(State)

    columns = list(deserialize_dataframe(state.df).columns)
    with me.box(style=me.Style(padding=me.Padding.all(15))):
        me.text(f"Expanded row: {df_row_index}", type="headline-5")
        with me.box(
                style=me.Style(
                    display="grid",
                    grid_template_columns=f"repeat({len(columns)}, minmax(150px, 1fr))",
                    gap=10,
                )
        ):
            for index, col in enumerate(deserialize_dataframe(state.df).iloc[df_row_index]):
                me.input(
                    label=columns[index], value=str(col), style=me.Style(width="100%")
                )


def on_click_strings(e: me.ClickEvent):
    """Click event for the cell button example."""
    state = me.state(State)
    state.string_output = e.key


def strings_component(meta: GridTableCellMeta):
    """Example of a cell rendering a button with a click event.

    Note that the behavior is slightly buggy if there is also a cell click event. This
    event will fire, but so will the cell click event. This is due to
    https://github.com/google/mesop/issues/268.
    """
    me.button(
        meta.value,
        key=meta.value,
        on_click=on_click_strings,
        style=me.Style(
            border_radius=3,
            background="#334053",
            border=me.Border.all(
                me.BorderSide(width=1, style="solid", color="rgba(255, 255, 255, 0.16)")
            ),
            font_weight="bold",
            color="#fff",
        ),
    )


def bool_component(meta: GridTableCellMeta):
    """Example of a cell rendering icons based on the cell value."""
    if meta.value:
        me.icon("check_circle", style=me.Style(color="green"))
    else:
        me.icon("cancel", style=me.Style(color="red"))


def anime_info_component(meta: GridTableCellMeta):
    state = me.state(State)
    anime = deserialize_dataframe(state.df)['Nombre'].get(meta)

    dataf = convert_to_dataframe_2(get_anime_episode_info_download(anime))

    with me.box(style=me.Style(margin=me.Margin.all(10), border=me.Border.all(
          me.BorderSide(width=3, color="#5474B4", style='groove')
        ),
        border_radius=10,)):
        grid_table(
            dataf,
            on_sort=on_table_sort,
            header_config=GridTableHeader(sticky=True),
            row_config=GridTableRow(
                columns={
                    "Episodio": GridTableColumn(component=text_component_bold),
                    "Descargas": GridTableColumn(component=download_component),
                },
            ),
            sort_column=state.sort_column,
            sort_direction=state.sort_direction,
            theme=GridTableThemeLight(striped=True)
            if state.theme == "light"
            else GridTableThemeDark(striped=True),
        )



def download_component(meta: GridTableCellMeta):
    data: List[DownloadLinkInfo] = meta.value

    with me.box(style=me.Style(display="flex", flex_wrap="wrap", gap=5)):
        for x in data:
            match x.server:
                case "MEGA":
                    color = "#FE1B19"
                case "1Fichier":
                    color = "#FEB01F"
                case "Zippyshare":
                    color = "#CA4600"
                case "Stape":
                    color = "#21328C"
                case _:
                    color = "#F01879"

            me.link(
                text=x.server,
                url=x.url,
                open_in_new_tab=True,
                style=me.Style(
                    display="inline-block",
                    padding=me.Padding.all(10),
                    border=me.Border().all(me.BorderSide(width=1, color=color, style="solid")),
                    border_radius=5,
                    color=color,
                    text_decoration="none",
                    text_align="center",
                    font_weight="bold",
                    flex_grow=1,
                    flex_shrink=1,
                    flex_basis="auto",
                    min_width="100px",
                )
            )

def text_component_bold(meta: GridTableCellMeta):
    me.text(meta.value, type="body-1", style=me.Style(font_weight='bold', cursor="pointer"))


def text_component(meta: GridTableCellMeta):
    me.text(meta.value, type="body-1", style=me.Style(cursor="pointer"))


def ints_style(meta: GridTableCellMeta) -> me.Style:
    """Example of a cell style based on the integer value."""
    return me.Style(
        cursor="pointer",
        background="#29a529" if meta.value > 0 else "#db4848",
        color="#fff",
        padding=me.Padding.all(10),
        border=me.Border.all(
            me.BorderSide(width=1, style="solid", color="rgba(255, 255, 255, 0.16)")
        ),
    )


def floats_component(meta: GridTableCellMeta):
    """Example of a cell rendering using string formatting."""
    me.text(f"${meta.value:,.2f}")


def date_component(meta: GridTableCellMeta):
    """Example of a cell rendering using custom date formatting."""
    me.text(meta.value.strftime("%b %d, %Y at %I:%M %p"))


def image_component(meta: GridTableCellMeta):
    """Example of a cell rendering using image."""
    me.image(
        src=meta.value,
        alt='Anime Image',
        style=me.Style(
            cursor="pointer",
            width='100%',
            height='auto',
            max_width='15rem',
            max_height='15rem',
        )
    )


@me.component
def grid_table(
        data,
        *,
        header_config: GridTableHeader | None = None,
        on_click: Callable | None = None,
        on_sort: Callable | None = None,
        row_config: GridTableRow | None = None,
        sort_column: str = "",
        sort_direction: SortDirection = "asc",
        theme: Any
               | None = None,  # Using Any since Pydantic complains about using a class.
):
    """Grid table component.

    Args:

      data: Pandas data frame
      header_config: Configuration for the table header
      on_click: Click event that fires when a cell is clicked
      on_sort: Click event that fires when a sortable header column is clicked
      row_config: Configuration for the tables's rows
      sort_column: Current sort column
      sort_direction: Current sort direction
      theme: Table theme
    """
    with me.box(
            style=me.Style(
                display="grid",
                # This creates a grid with "equal" sized rows based on the columns. We may want to
                # override this to allow custom widths.
                grid_template_columns=f"repeat({len(data.columns)}, minmax(70px, 1fr))",
                gap=10
            )
    ):
        _theme: GridTableTheme = GridTableThemeLight()
        if theme:
            _theme = theme

        if not header_config:
            header_config = GridTableHeader()

        if not row_config:
            row_config = GridTableRow()

        col_index_name_map = {}

        # Render the table header
        for col_index, col in enumerate(data.columns):
            col_index_name_map[col_index] = col
            sortable_col = row_config.columns.get(col, GridTableColumn()).sortable
            with me.box(
                    # Sort key format: ColumName-SortDirection
                    key=_make_sort_key(col, sort_column, sort_direction),
                    style=_make_header_style(
                        theme=_theme, header_config=header_config, sortable=sortable_col
                    ),
                    on_click=on_sort if sortable_col else None,
            ):
                with me.box(
                        style=me.Style(
                            display="flex",
                            align_items="center",
                        )
                ):
                    if sortable_col:
                        # Render sorting icons for sortable columns
                        #
                        # If column is sortable and not selected, always render an up arrow that is de-emphasized
                        # If column is sortable and selected, render the arrow with emphasis
                        # If the column is newly selected, render the up arrow to sort ascending
                        # If the column is selected and reselected, render the opposite arrow
                        me.icon(
                            "arrow_downward"
                            if sort_column == col and sort_direction == "desc"
                            else "arrow_upward",
                            style=_theme.sort_icon(col, sort_column),
                        )
                    me.text(col)

        # Render table rows
        for row_index, row in enumerate(data.itertuples(name=None)):
            for col_index, col in enumerate(row[1:]):
                cell_config = row_config.columns.get(
                    col_index_name_map[col_index], GridTableColumn()
                )
                cell_meta = GridTableCellMeta(
                    df_row_index=row[0],
                    df_col_index=col_index,
                    name=col_index_name_map[col_index],
                    row_index=row_index,
                    value=col,
                )
                with me.box(
                        # Store the df row index and df col index for the cell click event so we know
                        # which cell is clicked.
                        key=f"{row[0]}-{col_index}",
                        style=_make_cell_style(
                            theme=_theme,
                            cell_meta=cell_meta,
                            column=cell_config,
                            row_style=row_config.style,
                        ),
                        on_click=on_click,
                ):
                    if cell_config.component:
                        # Render custom cell markup
                        cell_config.component(cell_meta)
                    else:
                        me.text(str(col))

            # Render the expander if it's enabled and a row has been selected.
            if (
                    row_config.expander.component
                    and row_config.expander.df_row_index == row[0]
            ):
                with me.box(
                        style=_make_expander_style(
                            df_row_index=row[0],
                            col_span=len(data.columns),
                            expander_style=row_config.expander.style,
                            theme=_theme,
                        )
                ):
                    row_config.expander.component(row[0])


def _make_header_style(
        *, theme: GridTableTheme, header_config: GridTableHeader, sortable: bool
) -> me.Style:
    """Renders the header style

    Precendence of styles:

    - Header style override
    - Theme default
    """

    # Default styles
    style = theme.header(sortable)
    if header_config.style:
        style = header_config.style(sortable)

    if header_config.sticky:
        style.position = "sticky"
        style.top = 0

    return style


def _make_sort_key(col: str, sort_column: str, sort_direction: SortDirection):
    if col == sort_column:
        return f"{sort_column}-{sort_direction}"
    return f"{col}-asc"


def _make_cell_style(
        *,
        theme: GridTableTheme,
        cell_meta: GridTableCellMeta,
        column: GridTableColumn,
        row_style: Callable | None = None,
) -> me.Style:
    """Renders the cell style

    Precendence of styles:

    - Cell style override
    - Row style override
    - Theme Default
    """
    style = theme.cell(cell_meta)

    if column.style:
        style = column.style(cell_meta)
    elif row_style:
        style = row_style(cell_meta)

    style.width = "100%"
    style.box_sizing = "border-box"

    return style


def _make_expander_style(
        *,
        theme: GridTableTheme,
        df_row_index: int,
        col_span: int,
        expander_style: Callable | None = None,
) -> me.Style:
    """Renders the expander style

    Precendence of styles:

    - Cell style override
    - Theme default
    """
    style = theme.expander(df_row_index)
    if expander_style:
        style = expander_style(df_row_index)

    style.grid_column = f"span {col_span}"
    style.width = "100%"

    return style
