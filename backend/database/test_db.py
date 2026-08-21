from sqlalchemy import text

from db import engine


def test_connection():

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT version();")
        )

        print(
            "PostgreSQL connection successful!"
        )

        print(
            result.fetchone()[0]
        )


if __name__ == "__main__":
    test_connection()