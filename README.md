1. Schemas folder-->Rename the  files, which does not have Schema at the end to add Schema. example Tag.py to TagSchema.py

2. Schemas folder --> Create Schemas for City,Address.

3. Crud Folder --> Create methods for crete_tablerow and get_tablerows by following similar methods in that file.

4. Routes Folder --> Create routers for  User,Item,Tag,Country,State,City,Address by following Attribute,Entity routers as examples. main.py has some methods for user and item so just copy it over to their individual router files

5. main.py--> cleanup methods of user and item once #4 is done.

C:/Python/venv/Scripts/activate.bat

runnning app: uvicorn app.main:app

bash terminal pytest	


c: && cd c:\Python\GitHub\MyAppService\FastAPIProj && cmd /C "C:/Python/venv/Scripts/python.exe c:\Users\adminVM\.vscode\extensions\ms-python.python-2021.1.502429796\pythonFiles\lib\python\debugpy\launcher 63586 -- -m uvicorn app.main:app "