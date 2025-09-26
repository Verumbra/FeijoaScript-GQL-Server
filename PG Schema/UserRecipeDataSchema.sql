create schema if not exists UserRecipeData;

CREATE FUNCTION update_recipe_timestamps()
    RETURNS TRIGGER as $$
    BEGIN
        NEW.update_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';

CREATE TRIGGER update_recipe_timestamps
    BEFORE UPDATE ON recipe
    FOR EACH ROW
    EXECUTE FUNCTION update_recipe_timestamps();

create table app_user (
    id SERIAL PRIMARY KEY,
    name varchar(200),
    profile TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    update_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

);

create table recipe (
    id SERIAL PRIMARY KEY,
    name varchar(200),
    Description TEXT,
    img_url varchar(800),
    owner_id int NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    update_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (owner_id) REFERENCES app_user(id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
);



create table collection (

);

