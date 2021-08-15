#/bin/bash
## Coloring style Text shell script
RED=$(tput setaf 1)
NORMAL=$(tput sgr0)
printf "\n\n"
printf "%40s\n" "${RED}!!!!!! THIS SCRIPT SHOULD NOT BE RUN IN PRODUCTION !!!!!!${NORMAL}"
printf "\n\n"
sudo docker run -p 6379:6379 -d redis:5
python3 manage.py runserver 192.168.43.167:8000
