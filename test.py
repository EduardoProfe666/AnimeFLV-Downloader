from api.animeflv import AnimeFLV


with AnimeFLV() as api:
    print(api.search('Nanatsu no Taizai'))
