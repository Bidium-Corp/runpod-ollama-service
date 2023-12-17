# *************************************************************************** #
#                                                                              #
#    Makefile                                                                  #
#                                                                              #
#    By: Widium <ebennace@student.42lausanne.ch>                               #
#    Github : https://github.com/widium                                        #
#                                                                              #
#    Created: 2023/11/21 14:47:41 by Widium                                    #
#    Updated: 2023/11/21 14:47:41 by Widium                                    #
#                                                                              #
# **************************************************************************** #

CONTAINER_NAME = runpod

all : build run

# build the image with no chache
build :
	sudo docker-compose build

# build the image with no chache
re-build :
	sudo docker-compose build --no-cache

# run container and exit after entrypoint
run :
	sudo docker-compose up -d

# run no-detached container
run-server :
	sudo docker-compose up

# Open konsole in container
debug :
	sudo docker exec -it $(CONTAINER_NAME) bash

# Stop a running container
stop :
	sudo docker-compose down -v


.PHONY : all debug run build
