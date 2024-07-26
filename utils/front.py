import pandas as pd

from api.animeflv import AnimeInfo


def convert_to_dataframe(anime_list:  list[AnimeInfo]) -> pd.DataFrame:
    posters = [anime.poster for anime in anime_list]
    titles = [anime.title for anime in anime_list]
    synopsis = [anime.synopsis for anime in anime_list]
    ids = [anime.id for anime in anime_list]

    data = {"Image": posters, "Title": titles, "Synopsis": synopsis, "Id in AnimeFLV": ids}
    df = pd.DataFrame(data)
    return df