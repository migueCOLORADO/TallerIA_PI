import random
from urllib.parse import quote

from django.core.management.base import BaseCommand

from movie.models import Movie, Review

POSTER = "https://placehold.co/300x450?text={}"

REVIEWERS = ["Ana", "Carlos", "Laura", "Diego", "Valentina", "Santiago", "Camila", "Julián"]
COMMENTS = [
    "Muy recomendada, superó mis expectativas.",
    "Buena, aunque el ritmo se siente lento en algunos tramos.",
    "Una de mis favoritas, la volvería a ver.",
    "Está bien pero no es para todos los gustos.",
    "Excelente dirección y actuaciones sólidas.",
    "Entretenida de principio a fin.",
]

MOVIES = [
    dict(title="The Godfather", release_year=1972, genre="Crimen", director="Francis Ford Coppola", duration=175,
         synopsis="El patriarca de una familia mafiosa italoamericana cede el control de su imperio a su reticente hijo."),
    dict(title="The Dark Knight", release_year=2008, genre="Acción", director="Christopher Nolan", duration=152,
         synopsis="Batman enfrenta al Joker, un criminal anarquista que sumerge a Gotham en el caos."),
    dict(title="Pulp Fiction", release_year=1994, genre="Crimen", director="Quentin Tarantino", duration=154,
         synopsis="Las vidas de dos mafiosos, un boxeador y una pareja de ladrones se entrelazan en Los Ángeles."),
    dict(title="Forrest Gump", release_year=1994, genre="Drama", director="Robert Zemeckis", duration=142,
         synopsis="Un hombre de buen corazón atraviesa décadas de historia estadounidense casi por accidente."),
    dict(title="Inception", release_year=2010, genre="Ciencia Ficción", director="Christopher Nolan", duration=148,
         synopsis="Un ladrón especializado en robar secretos infiltrándose en sueños recibe una última misión imposible."),
    dict(title="The Matrix", release_year=1999, genre="Ciencia Ficción", director="Lana Wachowski", duration=136,
         synopsis="Un programador descubre que la realidad es una simulación controlada por máquinas."),
    dict(title="Titanic", release_year=1997, genre="Romance", director="James Cameron", duration=195,
         synopsis="Un romance nace entre dos pasajeros de distintas clases sociales a bordo del trasatlántico."),
    dict(title="Jurassic Park", release_year=1993, genre="Aventura", director="Steven Spielberg", duration=127,
         synopsis="Un parque temático con dinosaurios clonados se convierte en una trampa mortal."),
    dict(title="The Shawshank Redemption", release_year=1994, genre="Drama", director="Frank Darabont", duration=142,
         synopsis="Un banquero condenado injustamente encuentra esperanza y amistad en prisión."),
    dict(title="Fight Club", release_year=1999, genre="Drama", director="David Fincher", duration=139,
         synopsis="Un oficinista insomne funda un club de lucha clandestino que se transforma en algo mucho más peligroso."),
    dict(title="Interstellar", release_year=2014, genre="Ciencia Ficción", director="Christopher Nolan", duration=169,
         synopsis="Un grupo de astronautas viaja a través de un agujero de gusano para salvar a la humanidad."),
    dict(title="The Lion King", release_year=1994, genre="Animación", director="Roger Allers", duration=88,
         synopsis="Un joven león debe reclamar su lugar como rey tras la muerte de su padre."),
    dict(title="Toy Story", release_year=1995, genre="Animación", director="John Lasseter", duration=81,
         synopsis="Los juguetes de un niño cobran vida y enfrentan celos y aventuras cuando llega un nuevo juguete."),
    dict(title="Get Out", release_year=2017, genre="Terror", director="Jordan Peele", duration=104,
         synopsis="Un joven descubre un oscuro secreto al conocer a la familia de su novia."),
    dict(title="The Conjuring", release_year=2013, genre="Terror", director="James Wan", duration=112,
         synopsis="Un matrimonio de investigadores paranormales ayuda a una familia atormentada por una presencia maligna."),
    dict(title="La La Land", release_year=2016, genre="Romance", director="Damien Chazelle", duration=128,
         synopsis="Una actriz y un pianista de jazz persiguen sus sueños en Los Ángeles mientras su relación florece."),
    dict(title="Parasite", release_year=2019, genre="Drama", director="Bong Joon-ho", duration=132,
         synopsis="Una familia pobre se infiltra en la vida de una familia rica con consecuencias inesperadas."),
    dict(title="Mad Max: Fury Road", release_year=2015, genre="Acción", director="George Miller", duration=120,
         synopsis="En un desierto postapocalíptico, una guerrera ayuda a un grupo de mujeres a escapar de un tirano."),
    dict(title="Gladiator", release_year=2000, genre="Acción", director="Ridley Scott", duration=155,
         synopsis="Un general romano traicionado busca venganza como gladiador en el Coliseo."),
    dict(title="The Grand Budapest Hotel", release_year=2014, genre="Comedia", director="Wes Anderson", duration=99,
         synopsis="Las aventuras de un legendario conserje y su botones en un hotel europeo entre guerras."),
    dict(title="Superbad", release_year=2007, genre="Comedia", director="Greg Mottola", duration=113,
         synopsis="Dos amigos inseparables intentan comprar alcohol para una fiesta antes de separarse para la universidad."),
    dict(title="Coco", release_year=2017, genre="Animación", director="Lee Unkrich", duration=105,
         synopsis="Un niño mexicano viaja a la Tierra de los Muertos para descubrir la historia de su familia."),
    dict(title="Spirited Away", release_year=2001, genre="Animación", director="Hayao Miyazaki", duration=125,
         synopsis="Una niña queda atrapada en un mundo de espíritus y debe trabajar en una casa de baños mágica."),
    dict(title="Whiplash", release_year=2014, genre="Drama", director="Damien Chazelle", duration=106,
         synopsis="Un joven baterista se somete a los métodos extremos de un profesor de música despiadado."),
    dict(title="Se7en", release_year=1995, genre="Crimen", director="David Fincher", duration=127,
         synopsis="Dos detectives persiguen a un asesino en serie que castiga los siete pecados capitales."),
    dict(title="No Country for Old Men", release_year=2007, genre="Crimen", director="Ethan Coen", duration=122,
         synopsis="Un cazador encuentra dinero de un trato de drogas fallido y desata la persecución de un asesino implacable."),
    dict(title="The Avengers", release_year=2012, genre="Acción", director="Joss Whedon", duration=143,
         synopsis="Un grupo de superhéroes se une para detener la invasión alienígena de Loki."),
    dict(title="Spider-Man: Into the Spider-Verse", release_year=2018, genre="Animación", director="Bob Persichetti", duration=117,
         synopsis="Miles Morales descubre el multiverso y se une a otros Spider-Man de realidades distintas."),
    dict(title="Coraline", release_year=2009, genre="Fantasía", director="Henry Selick", duration=100,
         synopsis="Una niña descubre una versión paralela y siniestra de su vida detrás de una puerta secreta."),
    dict(title="Her", release_year=2013, genre="Ciencia Ficción", director="Spike Jonze", duration=126,
         synopsis="Un hombre solitario desarrolla una relación con un sistema operativo de inteligencia artificial."),
]

SERIES = [
    dict(title="Breaking Bad", release_year=2008, genre="Drama", director="Vince Gilligan", duration=47,
         synopsis="Un profesor de química con cáncer terminal se convierte en fabricante de metanfetamina."),
    dict(title="Game of Thrones", release_year=2011, genre="Fantasía", director="David Benioff", duration=57,
         synopsis="Varias casas nobles luchan por el control del Trono de Hierro en el continente de Poniente."),
    dict(title="Stranger Things", release_year=2016, genre="Ciencia Ficción", director="The Duffer Brothers", duration=51,
         synopsis="Un grupo de niños se enfrenta a fuerzas sobrenaturales y experimentos secretos en su pueblo."),
    dict(title="The Office", release_year=2005, genre="Comedia", director="Greg Daniels", duration=22,
         synopsis="Un falso documental sobre la vida diaria de los empleados de una empresa de papel."),
    dict(title="Friends", release_year=1994, genre="Comedia", director="David Crane", duration=22,
         synopsis="Seis amigos veinteañeros navegan el amor y la vida adulta en Nueva York."),
    dict(title="The Wire", release_year=2002, genre="Crimen", director="David Simon", duration=59,
         synopsis="Retrato coral del tráfico de drogas y las instituciones de Baltimore."),
    dict(title="Sherlock", release_year=2010, genre="Crimen", director="Steven Moffat", duration=88,
         synopsis="Una versión moderna del detective Sherlock Holmes resuelve crímenes en Londres."),
    dict(title="The Crown", release_year=2016, genre="Drama", director="Peter Morgan", duration=58,
         synopsis="La vida política y personal de la reina Isabel II desde su ascenso al trono."),
    dict(title="Black Mirror", release_year=2011, genre="Ciencia Ficción", director="Charlie Brooker", duration=48,
         synopsis="Antología que explora los efectos inquietantes de la tecnología en la sociedad."),
    dict(title="The Mandalorian", release_year=2019, genre="Ciencia Ficción", director="Jon Favreau", duration=40,
         synopsis="Un cazarrecompensas solitario protege a una misteriosa criatura en los confines de la galaxia."),
    dict(title="Better Call Saul", release_year=2015, genre="Drama", director="Vince Gilligan", duration=46,
         synopsis="Los orígenes del abogado Saul Goodman antes de los eventos de Breaking Bad."),
    dict(title="Dark", release_year=2017, genre="Ciencia Ficción", director="Baran bo Odar", duration=52,
         synopsis="La desaparición de niños en un pueblo alemán desata un misterio de viajes en el tiempo."),
    dict(title="Peaky Blinders", release_year=2013, genre="Crimen", director="Steven Knight", duration=58,
         synopsis="Una familia de gánsteres de Birmingham lucha por el poder tras la Primera Guerra Mundial."),
    dict(title="The Simpsons", release_year=1989, genre="Animación", director="Matt Groening", duration=22,
         synopsis="La vida cotidiana y satírica de una familia disfuncional en la ciudad de Springfield."),
    dict(title="Rick and Morty", release_year=2013, genre="Animación", director="Justin Roiland", duration=22,
         synopsis="Un científico excéntrico y su nieto viven aventuras interdimensionales absurdas."),
    dict(title="Narcos", release_year=2015, genre="Crimen", director="Chris Brancato", duration=49,
         synopsis="El auge y la caída del cartel de Medellín y su líder, Pablo Escobar."),
    dict(title="Money Heist", release_year=2017, genre="Crimen", director="Álex Pina", duration=48,
         synopsis="Un grupo de atracadores planea el mayor golpe de la historia en la Casa de la Moneda española."),
    dict(title="Chernobyl", release_year=2019, genre="Drama", director="Craig Mazin", duration=60,
         synopsis="Reconstrucción del desastre nuclear de Chernóbil y sus consecuencias humanas."),
    dict(title="Fargo", release_year=2014, genre="Crimen", director="Noah Hawley", duration=52,
         synopsis="Una serie de crímenes conecta a personajes insospechados en la nevada Minnesota."),
    dict(title="Avatar: The Last Airbender", release_year=2005, genre="Animación", director="Michael Dante DiMartino", duration=23,
         synopsis="Un joven maestro del aire debe dominar los cuatro elementos para restaurar el equilibrio del mundo."),
]


class Command(BaseCommand):
    help = "Crea datos de prueba de películas y series reales (idempotente)."

    def handle(self, *args, **options):
        created = 0
        for entry in MOVIES:
            created += self._seed(entry, "movie")
        for entry in SERIES:
            created += self._seed(entry, "series")

        posters_fixed = self._backfill_posters()
        reviews_created = self._backfill_reviews()

        self.stdout.write(self.style.SUCCESS(
            f"Seed completo. {created} títulos nuevos, "
            f"{posters_fixed} posters corregidos, {reviews_created} reviews creadas."
        ))

    def _seed(self, entry, content_type):
        title = entry["title"]
        defaults = {k: v for k, v in entry.items() if k != "title"}
        defaults["content_type"] = content_type
        defaults["poster"] = POSTER.format(quote(title))
        _, was_created = Movie.objects.get_or_create(title=title, defaults=defaults)
        return int(was_created)

    def _backfill_posters(self):
        fixed = 0
        for movie in Movie.objects.filter(poster=""):
            movie.poster = POSTER.format(quote(movie.title))
            movie.save(update_fields=["poster"])
            fixed += 1
        return fixed

    def _backfill_reviews(self):
        created = 0
        for movie in Movie.objects.filter(reviews__isnull=True):
            for _ in range(random.randint(2, 3)):
                Review.objects.create(
                    movie=movie,
                    reviewer_name=random.choice(REVIEWERS),
                    rating=random.randint(5, 10),
                    comment=random.choice(COMMENTS),
                )
                created += 1
        return created
