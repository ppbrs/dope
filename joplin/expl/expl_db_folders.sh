#!/bin/bash

source common.sh

sqlite3 -header -box -readonly $FPATH_LOCAL_DB "

-- PRAGMA table_info(folders);

--
-- Explore folders:
--
SELECT
	id, parent_id, title
FROM folders
LIMIT 15
;

SELECT
	L.id, L.parent_id, L.title, R.title
FROM folders L
LEFT JOIN folders R ON
	L.parent_id = R.id
LIMIT 15
;
"
