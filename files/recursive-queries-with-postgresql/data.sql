DROP TABLE IF EXISTS node;

CREATE TABLE node (
    id integer,
    parent_id integer,
    name varchar(255),
    PRIMARY KEY(id)
);

INSERT INTO node VALUES
    (1, null, 'node 1'),
    (2, null, 'node 2'),
    (3,    1, 'node 3'),
    (4,    3, 'node 4'),
    (5,    2, 'node 5'),
    (6,    4, 'node 6'),
    (7,    6, 'node 7'),
    (8,    7, 'node 8'),
    (9,    1, 'node 9');
