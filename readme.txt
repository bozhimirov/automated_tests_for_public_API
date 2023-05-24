Dependency Modules:

Python Version 3.10
requests==2.30.0
pytest==7.3.1
pytest-html==3.2.0
pytest-metadata==2.0.4
pytest-reportlog==0.4.0


Public Urls Tested:
https://demoqa.com/Account/v1/Authorized
https://demoqa.com/Account/v1/GenerateToken
https://demoqa.com/Account/v1/User
https://demoqa.com/Account/v1/User/{UUID}
https://demoqa.com/BookStore/v1/Books
https://demoqa.com/BookStore/v1/Book
https://demoqa.com/BookStore/v1/Books/{ISBN}

Usage:

python -m pytest --html=report_entries.html  test_A_tests.py

python -m pytest -v -s test_A_tests.py -q --report-log=log.jsonl

Execution Log are placed in the parent Directory


