# To Do App Api

## Installation

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

## Running the app

```bash
./run.sh
```

### Functionalities

- Can Create a User
- Can Login using JWT
- Can View the Tasks of a User using JWT
- CRUD of task only with authenticated state

(Yet to implement)

- Update and Delete of User

#### Frontend

[React TO DO App](https://github.com/Prajwalprakash3722/React_To_Do_App/tree/to_do)
