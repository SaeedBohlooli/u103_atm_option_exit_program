@echo off

set FILE=app.lock
if exist %FILE% (
  echo 'File %FILE% exists. probably the application is running. '
  pause 5
) else (
  echo 'File %FILE% does not exist.
  echo 'Ok'> %FILE%
  start cmd /k "call   python ..\backend\engine.py  --portfolio-id=p103"
  start cmd /k "call   python ..\backend\backend.py  --portfolio-id=p103"

)
