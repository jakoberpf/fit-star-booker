sql_create_course_table = """ CREATE TABLE IF NOT EXISTS courses (
                                    id integer PRIMARY KEY,
                                    datetime date NOT NULL,
                                ); """

sql_create_participation_table = """CREATE TABLE IF NOT EXISTS participation (
                                id integer PRIMARY KEY,
                                course_id integer NOT NULL,
                                participants_id integer NOT NULL,
                                FOREIGN KEY (course_id) REFERENCES courses (id),
                                FOREIGN KEY (participants_id) REFERENCES participants (id)
                            );"""

sql_create_participants_table = """CREATE TABLE IF NOT EXISTS participants (
                                id integer PRIMARY KEY,
                                name text NOT NULL,
                                priority integer,
                                status_id integer NOT NULL,
                                begin_date text NOT NULL,
                                end_date text NOT NULL,
                            );"""