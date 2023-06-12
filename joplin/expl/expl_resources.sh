#!/bin/bash

source common.sh

sqlite3 -header -box -readonly $FPATH_LOCAL_DB "

--
-- Explore resources:
--
SELECT
	id, title, mime, size
FROM resources
ORDER BY size DESC
LIMIT 20
;
"

echo
