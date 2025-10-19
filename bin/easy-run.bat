@echo off

set FILE=app.lock
if exist %FILE% (
  echo 'File %FILE% exists.'
) else (
  echo 'File %FILE% does not exist.
  echo 'Ok'> %FILE%
@REM   start cmd /k python ..\u102_option_trading\option_trading_unbalanced_butterfly.py  --p-id=p102
  start cmd /k "call ..\venv\Scripts\activate && python ..\backend\engine.py  --p-id=p103"

)
