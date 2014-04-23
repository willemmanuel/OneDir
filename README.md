## OneDir 3240 Project

### What we're working on now
Please check here: https://github.com/willemmanuel/OneDir/issues/1

### Current branches
- **Master**: contains our server code, our client code, and our tests. This is where most coding will take place. 
- **GUI**: for experimenting with GUI and getting all that working

### Current files 
- **OneDirConnection.py**: this is the main abstraction for the server. Instead of dealing with json requests, you can use this
class to 
- **OneDirClient.py**: this is the main OneDir client. This uses the OneDirConnection abstraction to get and post files, run watchdog, etc. 
- **server.py**: our restful API server. Must be running for tests or client to work. More detail below
- **/tests**: unit tests for server.py. Just makes sure the core API functionality is all good. We need client tests soon!

### Server Info
#### Unauthorized commands
- **/session** [POST]: logs a user in (uses json user + password data)
- **/register** [POST]: registers a user (uses json user + password + email data)

#### Authorized commands (need session cookie)
- **/change_password** [(auth) PUT]: changes user's password (uses json password data) 
- **/session** [DELETE]: logs a user out 
- **/list** [GET]: gets list of user files  
- **/directory/<path>** [POST]: creates a new directory 
- **/directory/<path>** [DELETE]: deletes a directory (should be empty) 
- **/file/<path>** [GET]: gets requested file 
- **/file/<path>** [POST]: uploads a given file. will create directories if needed (multipart file upload)
- **/file** [DELETE]: deletes a given file (uses json path + file data, sorry about the path inconsistency) 
- **/file** [PUT]: updates a file (either rename or move, uses json data)

#### Admin commands
- **/admin/change_password** [PUT] changes any users password (uses json user + password data)
- **/admin/list** [GET]: gets list of all user files
- **/admin/file** [DELETE]: deletes any given file (uses json path + user + file data, sorry about this inconsistency) 

### Client
