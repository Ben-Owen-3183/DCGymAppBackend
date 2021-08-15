RED=$(tput setaf 1)
NORMAL=$(tput sgr0)
POWDER_BLUE=$(tput setaf 153)
printf "\n"
printf "%40s\n" "${POWDER_BLUE}Starting DC app Backend :)${NORMAL}"
printf "\n"

printf "starting redis...\n"
sudo docker run -p 6379:6379 -d redis:5
printf "\n"
printf "%40s\n" "${POWDER_BLUE}Finshed${NORMAL}"
printf "\n"


# cronjobs
# 5 * * * * python3 -W ignore /path/to/app/manage.py upvimeo >> /path/to/DCGymAppBackend/live_stream/management/commands/logs.txt
# 2 * * * * python3 -W ignore /path/to/app/manage.py upmemstat >> /path/to/DCGymAppBackend/user_account/management/commands/logs.txt
