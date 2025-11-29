from pyngrok import ngrok, conf
import os

# Correct ngrok path
conf.get_default().ngrok_path = r"C:\Users\TEMP\AppData\Local\Programs\Python\Python313\Scripts\ngrok.exe"

# Start ngrok tunnel
public_url = ngrok.connect(8501)
print("Your app is live at:", public_url)

# Run Streamlit app
os.system("streamlit run app.py")
