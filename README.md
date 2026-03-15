pull README.

Setup:
pyre:
1- python -m venv venv
2- source venv/bin/activate // activating pyre static analyzer

    requirements:
        pyre-check
        fastapi
        uvicorn
        python-multipart

    launch:
        1- wsl
        2- source venev/bin/activate
        3 uvicorn app.main:app --reload
