# APSI-Ideas
Projekt realizowany w semestrze 2022Z w ramach przedmiotu APSI


### docker
Uruchomienie w nowym środowisku (flaga -d powoduje uruchomienie kontenera w tle):
1. docker-compose up -d

Usunięcie zbudowanego kontenera i ponowne uruchomienie
1. docker-compose down 
2. docker rm -f $(docker ps -a -q) 
3. docker volume rm $(docker volume ls -q)
4. docker-compose up -d 


