# Explanations

## Sources of data

`dope` tracks several sources of data:
* the local copy of my Joplin database,
* the external synchronization target for my Joplin database,
* my Obsidian vaults.

Paths are set in `dope/paths.py`.

## Joplin files overview

Local directory (~/.config/joplin-desktop/) structure:
├── database.sqlite
├── settings.json
├── userchrome.css
├── userstyle.css
├── resources (directory)
    ├── {32-hex-symbol name} (with extension)
├── tmp (directory)
    ├── edited_resources (directory)

Remote (~/Dropbox/Apps/Joplin) directory structure:
├── .resource (directory)
    ├── {32-hex-symbol name} (without extension)
├── {32-hex-symbol name}.md 

## Joplin database

### "resources" table
* id = 32-symbol unique ID
* title = file name with extension
* mime
  * application/pdf
  * image/png
  * application/xml
  * image/jpeg
  * video/mp4
  * audio/mpeg
  * application/msword
  * application/vnd.oasis.opendocument.graphics
  * application/vnd.oasis.opendocument.text
  * application/vnd.oasis.opendocument.spreadsheet
* size

Some resources may be referenced in a note by the URL from which the resource is downloaded.

### "folders" table (NOTEBOOKs)
* id = 32-symbol unique ID
* title = text
* parent_id = 32-symbol unique ID of the containing folder (NOTEBOOK)

### "notes" table
* id = 32-symbol unique ID
* parent_id = 32-symbol ID of the containing folder (NOTEBOOK)
* title: text
* body: text

### "tags" table

* id
* title
* parent_id (It is empty now which means tags can't be nested.)

### "note_tags" table

* id
* note_id
* tag_id

Some rows in this table have note_id that doesn't correspond to any known note.
