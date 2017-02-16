.. _CHANGELOG:

CHANGELOG
=========

0.5 Bio/Bibliographical Admin interface
---------------------------------------

Initial project release implements the bio/bibliographical portion of
the database and customized Django admin interface for data import
and managment of biographical and bibliographic data.

Places
~~~~~~
* As a data editor, I want to add or edit a place and associate it with a GeoNames ID so that I can link books and people to places that can be plotted on a map.
* As a data editor, when I’m editing a place I want to be able to look up the GeoNames ID by name and select from suggestions so that I can select the appropriate name within the system.

Book metadata
~~~~~~~~~~~~~
* As a data editor, I want to add a new or edit an existing language so that I can document the languages used in books in a standard way.
* As a data editor, I want to add a new or edit an existing subject so that I can document the relevant subjects of a book in a standard way.
* As a data editor, I want to add a new or edit an existing publisher so that I can track books by publisher in a standard way.
* As a data editor, I want to add a new or edit an existing owning institution so that I can document the current or previously known location of extant books.
* As a data editor, when I’m browsing the list of subjects, languages, publishers, or owning institution, I want to see a count of the number of books associated with each subject, language, publisher, or owning institution so I can get a sense of the distribution of books.
* As a data editor, I want to add a new or edit an existing book so that I can document the publication data, annotation data, and other relevant details.
* As a data editor, when I’m editing a book I want to document the people who interacted with it in ways other than annotation so that I can track which books they owned, read, etc.
* As a data editor, when I’m editing a book I want to be able to associate languages, subjects, and owning institutions on the same page so that I don’t have to edit book information in multiple places.
* As a data editor, when I’m editing a book I want to be able to associate people involved in creating the book so that I can document information about authors and editors.
* As a data editor, when I’m browsing the list of books I want to filter by subject or language or whether extant, annotated, digitized, so that I can quickly look at a particular subset of books.
* As a data editor, when I’m browsing the list of books I want to see the author, short title, publication year, owning institution call number, and whether a book is extant, annotated, and/or digitized so that I can get a quick overview of volumes.
* As a data editor, when I search for books in the admin interface I want to search on title, author, call number, publisher name and notes so that I can find specific items.
* As a data editor, I want to link books that were bound together in a volume held by a particular institution so that I can link a catalog record to individual titles and indicate in which order the associated books/titles were bound.

People
~~~~~~
* As a data editor, I want to add a new or edit an existing person so that I can document people associated with the Winthrop Family and their books.
* As a data editor, I want to add a new or edit an existing relationship type so that I can document the kinds of relationships between people associated with the project.
* As a data editor, I want to add a new or edit an existing relationship type so that I can document the kinds of relationships between people associated with the project.
* As a data editor, when I’m editing a person I want to be able to document known residences and dates on the same page so that I don’t have to edit person information in multiple places.
* As a data editor, when I’m editing a person I want to relate them to other people on the same page so that I don’t have to edit person information in multiple places.
* As a data editor, when I’m editing a person I want to be able to look up the VIAF ID by name and select from suggestions so that I can select the appropriate name within the system.
* As a data editor, when I edit a person and add or change the VIAF ID, I want the birth and death dates and sex in the system populated from data available in VIAF in order to make data entry more efficient.
* As a data editor, when I’m viewing the list of people I want to see authorized name, sort name, birth and death dates, viaf id, and family group so that I can quickly get a sense of the records I’m looking at.
* As a data editor, when I’m editing a person I want to view the list of books they interacted with in ways other than annotation so that I can track which books they owned, read, etc.
* As a data editor, when I’m editing a person I want to view a list of people who are related to the current person so I can compare relationships.
* As a data editor, when I’m browsing the list of people I want to filter by family group so that I can quickly look at a particular group of people.

Footnotes
~~~~~~~~~
* As a data editor, I want to add a new or edit an existing source type so that I can track the kinds of source documents used as evidence in the system.
* As a data editor, I want to add a new or edit an existing footnote and associate it with any other kind of record in the system so that I can document evidence related to assertions made elsewhere in the data.
* As a data editor, when I’m editing a book or a book-person relationship, I want to be able to add footnotes on the same page so that I can add documentation on the same page.

Data Import
~~~~~~~~~~~
* As a data editor, I want a one-time import of books (with associated people, places, publishers, and NYSL cataloguing information) from spreadsheet data into the system so that I can refine and augment the initial person data that’s already been collected.
* As a data editor, when people are imported from spreadsheet data, I want them automatically linked to a VIAF record if possible, so that I don’t have to manually look up matches that can be made automatically.
* As a data editor, when people are imported from spreadsheet data, I want birth and death dates to be added to the record where they can be inferred from the authorized name so that I don’t have to re-enter this data.

Accounts & Permissions
~~~~~~~~~~~~~~~~~~~~~~
* As a project team member, I want to login with my Princeton CAS account so that I can use existing my existing credentials and not have to keep track of a separate username and password.
* As an admin, I want to edit user and group permissions so I can manage project team member access within the system.
* As an admin, I want an easy way to give project team members data editing permissions to that I don’t have to keep track of all the individual required permissions.



