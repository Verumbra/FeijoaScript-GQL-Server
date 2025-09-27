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


CREATE TABLE Instruction_List (
    Recipe_ref_number INT NOT NULL,
    id Serial PRIMARY KEY,
    name varchar(200),
    FOREIGN KEY (Recipe_ref_number) REFERENCES recipe(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE Step_List (
    Inst_Ref_ID INT NOT NULL,
    name varchar(200),
    step_index INT NOT NULL,
    step_body TEXT NOT NULL,
    FOREIGN KEY (Inst_Ref_ID) REFERENCES Instruction_List(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE Ingredient_List (
    Recipe_Ref_Number INT NOT NULL,
    id Serial PRIMARY KEY,
    name varchar(200),
    FOREIGN KEY (Recipe_Ref_Number) REFERENCES Recipe(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE Ingredient (
    Ing_List_Ref_Number INT NOT NULL,
    id Serial PRIMARY KEY,
    name varchar(200),
    amount varchar,
    ing_id INT,
    FOREIGN KEY (Ing_List_Ref_Number) REFERENCES Ingredient_List(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
