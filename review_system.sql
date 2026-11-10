-- Adminer 5.5.1 PostgreSQL 18.4 dump

DROP TABLE IF EXISTS "articles";
CREATE TABLE "public"."articles" (
    "article_id" integer GENERATED ALWAYS AS IDENTITY NOT NULL,
    "author_id" integer NOT NULL,
    "category_id" integer NOT NULL,
    "title" character varying(255) NOT NULL,
    "content" text NOT NULL,
    "status" character varying(30) DEFAULT 'editing' NOT NULL,
    "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "articles_pkey" PRIMARY KEY ("article_id"),
    CONSTRAINT "articles_status_check" CHECK (((status)::text = ANY ((ARRAY['editing'::character varying, 'under_review'::character varying, 'approved'::character varying])::text[])))
)
WITH (oids = false);


DROP TABLE IF EXISTS "categories";
CREATE TABLE "public"."categories" (
    "category_id" integer GENERATED ALWAYS AS IDENTITY NOT NULL,
    "category_name" character varying(100) NOT NULL,
    CONSTRAINT "categories_pkey" PRIMARY KEY ("category_id")
)
WITH (oids = false);

CREATE UNIQUE INDEX categories_category_name_key ON public.categories USING btree (category_name);

INSERT INTO "categories" ("category_id", "category_name") VALUES
(1,	'Technology'),
(2,	'Education'),
(3,	'Lifestyle'),
(4,	'Business'),
(5,	'Science');

DROP TABLE IF EXISTS "reviews";
CREATE TABLE "public"."reviews" (
    "review_id" integer GENERATED ALWAYS AS IDENTITY NOT NULL,
    "article_id" integer NOT NULL,
    "editor_id" integer NOT NULL,
    "comment" text,
    "decision" character varying(20) NOT NULL,
    "reviewed_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "reviews_pkey" PRIMARY KEY ("review_id"),
    CONSTRAINT "reviews_decision_check" CHECK (((decision)::text = ANY ((ARRAY['approved'::character varying, 'returned'::character varying])::text[])))
)
WITH (oids = false);


DROP TABLE IF EXISTS "users";
CREATE TABLE "public"."users" (
    "user_id" integer GENERATED ALWAYS AS IDENTITY NOT NULL,
    "username" character varying(100) NOT NULL,
    "password" character varying(255) NOT NULL,
    "role" character varying(20) NOT NULL,
    "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "users_pkey" PRIMARY KEY ("user_id"),
    CONSTRAINT "users_role_check" CHECK (((role)::text = ANY ((ARRAY['author'::character varying, 'editor'::character varying])::text[])))
)
WITH (oids = false);

CREATE UNIQUE INDEX users_username_key ON public.users USING btree (username);


ALTER TABLE ONLY "public"."articles" ADD CONSTRAINT "articles_author_id_fkey" FOREIGN KEY (author_id) REFERENCES "public".users(user_id);
ALTER TABLE ONLY "public"."articles" ADD CONSTRAINT "articles_category_id_fkey" FOREIGN KEY (category_id) REFERENCES "public".categories(category_id);

ALTER TABLE ONLY "public"."reviews" ADD CONSTRAINT "reviews_article_id_fkey" FOREIGN KEY (article_id) REFERENCES "public".articles(article_id);
ALTER TABLE ONLY "public"."reviews" ADD CONSTRAINT "reviews_editor_id_fkey" FOREIGN KEY (editor_id) REFERENCES "public".users(user_id);

-- 2026-11-08 15:41:49 UTC
