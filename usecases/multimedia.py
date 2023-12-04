from usecases import utils


class Multimedia:
    def __init__(self):
        self.movie_images = utils.get_dicti("data/movie_image.json")
        self.cast_images = utils.get_dicti("data/cast_image.json")

    def create_sparql(self, entity: str) -> str:
        query = f"""
            PREFIX wd: <http://www.wikidata.org/entity/>
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?id WHERE{{ 
                wd:{entity} wdt:P345 ?id.
            }}
            LIMIT 1
        """
        return query

    def find_image(self, imdb_ids: list, label: list) -> list:
        mapping = {"ACTOR": self.cast_images, "MOVIE": self.movie_images}

        images = []
        for imdb_id, l in zip(imdb_ids, label):
            print(imdb_id)
            print(l)
            try:
                image = mapping[l][imdb_id][0]
                print(image)
            except KeyError:
                image = (
                    mapping["ACTOR"][imdb_id][0]
                    if l == "MOVIE"
                    else mapping["MOVIE"][imdb_id][0]
                )
                print(image)
            finally:
                assert image, f"No image found for {imdb_id}"
                images.append(f"image:{image}")

        return images
