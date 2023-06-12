# Contens of this folder

* tests/* = Tests that ensure the consistency of the database and resources.

* expl/* = Miscellaneous temporary scripts for exploring the database and resource.

# TODO

* Resources
  * compare local and remote directory sizes
* check for heading and trailing spaces in headers
* check for nonreadable symbols (don't confuse with Unicode)

# Overview

Local folder (~/.config/joplin-desktop/) structure:
├── database.sqlite
├── settings.json
├── userchrome.css
├── userstyle.css
├── resources (directory)
    ├── <32-symbol name>.<extension>
├── tmp (directory)
    ├── edited_resources (directory)

Remote (~/Dropbox/Apps/Joplin) folder structure:
├── .resource (directory)
    ├── <32-symbol name> (without extension)
├── <32-symbol name>.md 

# database.sqlite

## list of useful tables

## resources table
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

## folders table (NOTEBOOKs)
* id = 32-symbol unique ID
* title = text
* parent_id = 32-symbol unique ID of the containing folder (NOTEBOOK)

## notes table
* id = 32-symbol unique ID
* parent_id = 32-symbol ID of the containing folder (NOTEBOOK)
* title: text
* body: text

## tags table

* id
* title
* parent_id (It is empty now which means tags can't be nested.)

## note_tags table

* id
* note_id
* tag_id

Some rows in this table have note_id that doesn't correspond to any known note.
