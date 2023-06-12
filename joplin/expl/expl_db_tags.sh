#!/bin/bash

source common.sh

sqlite3 -header -box -readonly $FPATH_LOCAL_DB "

PRAGMA table_info(tags);
PRAGMA table_info(note_tags);

-- SELECT
-- 	id, title, parent_id, type(parent_id)
-- FROM tags
-- ;

-- SELECT
-- 	NT.id, NT.note_id, NT.tag_id, T.title, N.title
-- FROM note_tags NT 
-- LEFT JOIN tags T ON NT.tag_id = T.id
-- INNER JOIN notes N ON NT.note_id = N.id
-- ORDER BY T.title
-- ;

SELECT
	NT.id, NT.note_id, NT.tag_id, T.title, N.title
FROM note_tags NT 
LEFT JOIN tags T ON NT.tag_id = T.id
LEFT JOIN notes N ON NT.note_id = N.id
ORDER BY T.title
;



"
