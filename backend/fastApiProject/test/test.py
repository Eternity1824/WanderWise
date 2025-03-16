import requests

url = "http://10.245.216.225:3001/api/v1/workspace/llm/chat"

response = requests.post(url, json={
  "message": "What is AnythingLLM?",
  "mode": "query | chat",
  "sessionId": "identifier-to-partition-chats-by-external-id",
  "attachments": [
    {
      "name": "image.png",
      "mime": "image/png",
      "contentString": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
    }
  ]
})
print(response)
