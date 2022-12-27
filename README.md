# VK Comic posting 

This tool allows to automatically download random xkcd comics from the main website, and then post them to a selected group wall.

## How to install

### Requirements 

Python3 should already be installed. 
Use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

### Environment variables

Two external variables are required to use the tool:
1. Vk app access token
2. Vk group id

Instructions on how to obtain the access token can be found in [vk api database](https://dev.vk.com/api/access-token/implicit-flow-user), and group id can be found in the vk group url.

After gaining access to both of the variables, you must create a new file called **tokens.env** in the project folder, and store two variables inside of it as:
1. `VK_ACCESS_TOKEN`
2. `VK_GROUP_ID`

## How to use

Simply launch the main.py file.
```
python main.py
```

## Project Goals

This code was written for educational purposes as part of an online course for web developers at [dvmn.org](https://dvmn.org/).