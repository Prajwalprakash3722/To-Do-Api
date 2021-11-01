# Flask_SQl_Boilerplate

## Description

This repository is a boilerplate for creating a flask application with SQLAlchemy.

- Steps:
  - Clone this repository
  - Make Your Necessary Changes
  - Run the following commands:
    - `pip3 install -r requirements.txt`
    - `./run.sh`
  - Open the browser and go to http://localhost:5000/
  - To create Database go to python shell and run the following command:
    - `python3`
    ```python3
    from app import db
    db.create_all()
    ```
