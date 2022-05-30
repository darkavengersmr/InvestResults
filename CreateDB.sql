CREATE DATABASE InvestResults;

CREATE TABLE public.users
(
	id serial NOT NULL,
	username text NOT NULL,
	email text  NOT NULL,
	hashed_password text,
	is_active boolean NOT NULL,
	CONSTRAINT pk_users_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.users
    OWNER to pi;


CREATE TABLE public.categories
(
	id serial NOT NULL,
	category text NOT NULL,
	owner_id integer REFERENCES users(id) ON DELETE CASCADE NOT NULL,
	CONSTRAINT pk_categories_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.categories
    OWNER to pi;



CREATE TABLE public.investments_items
(
	id serial NOT NULL,
	description text NOT NULL,
	category_id integer REFERENCES categories(id) ON DELETE CASCADE,
	owner_id integer REFERENCES users(id) ON DELETE CASCADE NOT NULL,	
	CONSTRAINT pk_investments_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.investments_items
    OWNER to pi;


CREATE TABLE public.investments_history
(
	id serial NOT NULL,
	date timestamp with time zone,
	sum integer,
	investment_id integer REFERENCES investments_items(id) ON DELETE CASCADE,
	CONSTRAINT pk_investment_history_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.investments_history
    OWNER to pi;


CREATE TABLE public.investments_in_out
(
	id serial NOT NULL,
	date timestamp with time zone,
	description text NOT NULL,
	sum integer,
	investment_id integer REFERENCES investments_items(id) ON DELETE CASCADE,
	CONSTRAINT pk_investment_in_out_id PRIMARY KEY (id)
)

WITH (
    OIDS = FALSE
);

ALTER TABLE IF EXISTS public.investments_in_out
    OWNER to pi;


