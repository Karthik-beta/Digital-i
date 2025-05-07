@echo off
docker exec backend sh -c "python manage.py absentees; python manage.py task; python manage.py mandays"
exit
