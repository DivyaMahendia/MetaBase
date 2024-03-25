# Metabase: DB Application for handling huge Metadata

The objective of this project is to develop a comprehensive database application that focuses on creating and managing file metadata in a secure and robust manner. The application will involve the following key components:

1. File Metadata Database Creation: The first challenge is to design and
implement a database capable of storing metadata of files. This involves identifying
the essential file attributes and properties to be included in the database schema to
facilitate efficient storage and retrieval of metadata.

2. Key Database Operations: The database application should support key
operations, including adding new file metadata, updating existing records, deleting
outdated information, and querying the database to retrieve specific file details.

3. SQL Server Integration with PyQt5 Application: The project requires
establishing a connection between the SQL Server and the PyQt5 application. This
integration will enable seamless communication and data exchange between the
graphical user interface (GUI) built with PyQt5 and the underlying SQL Server
database.

4. Populating Data from SQL Server Database: Implementing a mechanism to
populate data from the SQL Server database into the PyQt5 application is crucial.
This ensures that users can view, manage, and analyze the file metadata stored in
the database through the user-friendly interface provided by the PyQt5 application.

5. Authentication and Security: Security is paramount for any database
application. The system incorporates the facility to sign-in and login in order to
maintain a secure application and to keep an activity log as well.

6. Activity Log: In order to maintain an audit trail and track user interactions, an
activity log has been integrated into the database application. The activity log will
record details such as login/logout times, performed actions, and the
corresponding user identities.
