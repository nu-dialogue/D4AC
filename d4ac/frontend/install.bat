rmdir ..\d4ac_main\templates /s /q
rmdir ..\d4ac_main\static /s /q
mkdir ..\d4ac_main\templates
copy dist\index.html ..\d4ac_main\templates
xcopy /s /e dist\static ..\d4ac_main\static\
xcopy /s /e dist\images ..\d4ac_main\static\images\
pause
