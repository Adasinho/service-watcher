import requests

class Discord:
    def __init__(self, token, botName):
        self.__token = token
        self.__botName = botName
    
    def __prepareData(self, content):
        return {
            "content": content,
            "username": self.__botName
        }
    
    def __prepareEmbeds(self, description, title):
        return {
            "username": self.__botName,
            "embeds": [
                {
                    "description": description,
                    "title": title
                }
            ]
        }
    
    def sendMessage(self, title, description):
        data = self.__prepareEmbeds(description, title)
        result = requests.post(self.__token, json = data)
        
        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))