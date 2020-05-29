# Aerobotics Data Challenge

This repo is the code to reproduce the results from the writeup.

# Quickstart
Code is in notebooks. To start the notebook server run:
`$make create-all`

This will build the docker container that runs the notebook server.

## Directory structure

├── Makefile           <- Makefile with commands like `make create-all` or `make help`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├─ weight_data.csv <- weights data
│   ├─ count_data.csv <- berry count data
├── notebooks <- code to reproduce predictions from writeup
│   ├─ Agent_model.ipynb <- notebook used for writeup
│   ├─ HMM_model.ipynb <- test of HMM model but not complete
│     
├── src <- modules for models 
│   ├─ berry.py <- contains code for berry agent
│   ├─ simulation.py <- code to simulate berries ripening
├── Dockerfile <- docker file to build notebook enviroment

## Docker commands
The docker environment can be controlled using the make file. Use `$make help` to see list of commands.

Important commands are:
`make create-all` -creates image and container
`make run-container` start container if environment is built
`make clean` removes images and container


 
Jupyter notebook will require a token to log in, see command line for token.