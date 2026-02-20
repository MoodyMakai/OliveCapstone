# OliveCapstone

## Overview

This is a capstone project by Olive Food Solutions

This contains both the frontend and backend code for the Black Bear Foodshare App,
a iOS app that connects leftover food at UMaine, to UMaine students.

### Backend

To setup, start in the backend folder and run these commands:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

This should set up a virtual environment and install the requirements you need.

Commands:
Run the app: `quart --app src.app run`

Test: `pytest`

Lint: `ruff check --fix` to fix automatically (may not fix everything)

Format: `ruff format`

### Documentation

The inline code documentation is not implemented yet.

To find all the documents: look in the documents folder.
