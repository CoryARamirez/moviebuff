import os
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Genres(Base):
    __tablename__ = 'genres'

    name = Column(
        String(80),
        nullable=False)

    id = Column(
        Integer,
        primary_key=True)

    movies = relationship("Movies")

    @property
    def serialize(self):
        return {
            "name": self.name,
            "id": self.id,
            "movies": [movie.serialize for movie in self.movies]
        }


class Movies(Base):
    __tablename__ = 'movies'

    name = Column(
        String(80),
        nullable=False)

    id = Column(
        Integer,
        primary_key=True)

    author = Column(
        String(80),
        nullable=False)

    description = Column(
        String(250))

    genre_id = Column(
        Integer,
        ForeignKey('genres.id'))

    genres = relationship(Genres)

    @property
    def serialize(self):
        return {
            "name": self.name,
            "description": self.description,
            "id": self.id,
        }


def new_engine(db_name):
    if os.path.exists(db_name + ".db"):
        os.remove(db_name + ".db")
    else:
        print("Requested db does not previously exist. Creating clean.")

    # Todo: Understand why I was getting a thread synchronization error
    engine = create_engine("sqlite:///" + db_name + ".db", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)

    return engine


def new_session(engine):
    db_session = sessionmaker(bind=engine)
    session = db_session()

    return session


def seed_db(session):
    # HORROR CATEGORY W/ MOVIES (CATALOG ITEMS)
    category_horror = Genres(name="Horror")
    session.add(category_horror)
    session.commit()

    horror_1 = Movies(name="Anabelle", description="Annabelle is a 2014 American supernatural horror film directed by "
                                                   "John R. Leonetti, written by Gary Dauberman and produced by Peter "
                                                   "Safran and James Wan.", genres=category_horror, author="admin")
    session.add(horror_1)
    session.commit()

    # COMEDY CATEGORY W/ MOVIES (CATALOG ITEMS)
    category_comedy = Genres(name="Comedy")
    session.add(category_comedy)
    session.commit()

    comedy_1 = Movies(name="Spy", description="Spy is a 2015 American action comedy spy film written and directed by "
                                              "Paul Feig. ... It follows the life of a secret agent, Susan Cooper ("
                                              "McCarthy), trying to trace a stolen portable nuclear device.",
                      genres=category_comedy, author="admin")
    session.add(comedy_1)
    session.commit()

    # SCI-FI CATEGORY W/ MOVIES (CATALOG ITEMS)
    category_sci_fi = Genres(name="Sci-Fi")
    session.add(category_sci_fi)
    session.commit()

    sci_fi_1 = Movies(name="Interstellar", description="Interstellar is a 2014 American epic science fiction film "
                                                       "directed and produced by Christopher Nolan. ... Set in a "
                                                       "dystopian future where humanity is struggling to survive, "
                                                       "the film follows a group of astronauts who travel through a "
                                                       "wormhole near Saturn in search of a new home for humanity.",
                      genres=category_sci_fi, author="admin")
    session.add(sci_fi_1)
    session.commit()

    # ANIMATION CATEGORY W/ MOVIES (CATALOG ITEMS)
    category_animation = Genres(name="Animation")
    session.add(category_animation)
    session.commit()

    animation_1 = Movies(name="Abominable", description="Abominable is a movie about a Chinese girl who discovers a "
                                                        "yeti, an imaginary creature living on top of her house.",
                         genres=category_animation, author="admin")
    session.add(animation_1)
    session.commit()

    # ACTION CATEGORY W/ MOVIES (CATALOG ITEMS)
    category_action = Genres(name="Action")
    session.add(category_action)
    session.commit()

    action_1 = Movies(name="Jack Reacher", description="Jack Reacher (formerly called One Shot, or alternatively "
                                                       "known as Jack Reacher: One Shot) is a 2012 American action "
                                                       "thriller film written and directed by Christopher McQuarrie, "
                                                       "based on Lee Child's 2005 novel One Shot. ... Cruise "
                                                       "performed all of his own driving stunts during the film's car "
                                                       "chase sequence.", genres=category_action, author="admin")
    session.add(action_1)
    session.commit()

    # FANTASY CATEGORY W/ MOVIES (CATALOG ITEMS)
    category_fantasy = Genres(name="Fantasy")
    session.add(category_fantasy)
    session.commit()

    fantasy_1 = Movies(name="Harry Potter", description="Harry Potter is an orphaned boy brought up by his unkind "
                                                        "Muggle (non-magical) aunt and uncle. ... Harry became "
                                                        "extremely famous in the Wizarding World as a result. Harry "
                                                        "begins his first year at Hogwarts School of Witchcraft and "
                                                        "Wizardry and learns about magic.", genres=category_fantasy,
                       author="admin")
    session.add(fantasy_1)
    session.commit()

    print("Seeded database with default movie categories and items!")
