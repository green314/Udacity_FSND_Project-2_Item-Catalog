# Fullstack Developer Nanodegree Project 2: Item Catalog

The scope of this project is to develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit, and delete their own items. For this specific project, 'categories' are 'genres' and 'items' are 'books'.

*Note:* Facebook User ID is used to authenticate permission to add, edit, and delete books and genres (this is the number included on all entries).

## Submission Overview

1. `project_main.py` contains the main application code in Python.
2. `configure_database.py` contains the database setup code in Python.
3. The `templates` folder contains all html files (with embedded javascript). All CRUD files are labeled as such; `navbar.html` creates a persistent navbar which includes any neccessary Facebook login-related javascript; `index.html` is the 'home' page of the project.

## Python Modules and Prerequisites Required to Run Project

See below for a list of Python modules that are required to run this project:
- sqlalchemy (including sqlalchemy.orm)
- flask
- facebook

See below for a list of prerequisites that are required to run this project:
- Python 3.0
- Virtualbox
- Vagrant

## Getting Started (for Windows)

1. Download Vagrant [here](https://www.vagrantup.com/downloads.html).
2. Download VirtualBox [here](https://www.virtualbox.org/wiki/Downloads).
3. In a new directory, download and extract the FSND-Virtual-Machine included with the Fullstack Developer nanodegree [here](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip).
4. Download the project files and copy them into the `catalog` folder of the `fullstack-nanodegree-vm` directory.
4. Navigate into the `fullstack-nanodegree-vm` directory, and then into the `Vagrant` directory.
5. In the `Vagrant` directory, enter `Vagrant up`, and wait for up to an hour as Vagrant sets up. Resolve any version or port errors by making changes in `VagrantFile`, within the `Vagrant` directory (e.g. `nano VagrantFile`). Ensure that Port 5000 is included in the Vagrantfile.
6. Once Vagrant is set up, enter `Vagrant SSH` to enter the virtual machine.
7. Navigate to the Catalog folder (the default path with this VM seems to be `cd ../..` --> `cd vagrant` --> `cd catalog`)
8. Run the project code (`python project_main.py`), and navigate to http://localhost:5000/ in a browser. If an error occurs when entering `python project_main.py`, attempt to use `python3 project_main.py`.
9. All other project interaction will occur at http://localhost:5000/ on your preferred browser. If any port errors occur on loading the page, attempt to use the Chrome or Firefox browsers instead.
