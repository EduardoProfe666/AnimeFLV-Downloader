import pandas as pd

from api.animeflv import AnimeInfo, EpisodeInfoDownload


def convert_to_dataframe_1(anime_list:  list[AnimeInfo]) -> pd.DataFrame:
    posters = [anime.poster for anime in anime_list]
    titles = [anime.title for anime in anime_list]
    synopsis = [anime.synopsis for anime in anime_list]
    ids = [anime.id for anime in anime_list]

    data = {"Poster": posters, "Título": titles, "Sinopsis": synopsis, "Nombre": ids}
    df = pd.DataFrame(data)
    return df

def convert_to_dataframe_2(anime_list:  list[EpisodeInfoDownload]) -> pd.DataFrame:
    episodes = [str(anime.id) for anime in anime_list]
    downloads = [anime.downloads for anime in anime_list]

    data = {"Episodio": episodes, "Descargas": downloads}
    df = pd.DataFrame(data)
    return df