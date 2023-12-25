Достаем https линк через ngrok(нужен в credentials.yml)
```sh
ngrok http 5005
```

В отдельном терминале
```sh
cd actions
rasa run actions
```

В отдельном терминале
```sh
rasa run -m models -p 5005 --connector telegram --credentials credentials.yml --debug
```
