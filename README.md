# Movie_Title_Game System for Cosc483
A final project for Cosc483 providing a movie title guessing game.<br>
You can see the details in the final report.

## Setup
Python 3.7+ is recommended. The file requirements.txt includes all necessary libraries working for this project.<br>
You can enter command to install them.
```python
pip install -r requirements.txt
```

## How to Start
### Rasa Models
Rasa models are attached in the [*directory*](https://github.com/georgetown-dialogue-systems-2022/Movie_Title_Game-Rasa/tree/main/src/game_system/models). Thus you can directly run them. Two terminals are needed, one for running actions and the other for loading model. Enter the command line respectively:
```
rasa run actions --cors "*"
rasa run -m models --enable-api --cors "*"
```
If you want to run your own Rasa model, edit the configuration following the formal documents on the [*Rasa*](https://rasa.com/docs/rasa/) website, and then use command in the game_system directory:
```python
rasa train
```
Now you can enter the coomands above to start the system!

### Web UI
All our web Ui is edited by [*chatbot-widget*](https://github.com/JiteshGaikwad/Chatbot-Widget). After running the system, just double click the [*index.html*](https://github.com/georgetown-dialogue-systems-2022/Movie_Title_Game-Rasa/blob/main/src/game_system/index.html), the web server would show in your browser.

