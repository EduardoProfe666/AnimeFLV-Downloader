import pandas as pd

from api.animeflv import AnimeInfo


def convert_to_dataframe(anime_list:  list[AnimeInfo]) -> pd.DataFrame:
    posters = [anime.poster for anime in anime_list if anime.poster is not None and anime.poster != '']
    titles = [anime.title for anime in anime_list if anime.title is not None and anime.title != '']
    synopsis = [anime.synopsis for anime in anime_list if anime.synopsis is not None and anime.synopsis != '']
    ids = [anime.id for anime in anime_list if anime.id is not None and anime.id != '']

    data = {"Image": posters, "Title": titles, "Synopsis": synopsis, "Actions": ids}
    df = pd.DataFrame(data)
    return df