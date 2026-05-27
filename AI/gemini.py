from google import genai

client = genai.Client(api_key="AIzaSyC7mpWNI7cxpXy012WCgVYudizXAdRnrIE")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="介绍一下人工智能"
)

print(response.text)