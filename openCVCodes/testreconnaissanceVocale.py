import speech_recognition as sr
import serial
import time

# Connexion au port série (ajuste COM3 selon ton système)
arduino = serial.Serial('COM9', 9600)
time.sleep(2)

recognizer = sr.Recognizer()
mic = sr.Microphone()

print("Dites 'rotation' pour activer le servo...")

while True:
    with mic as source:
        print("🎤 Écoute...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="fr-FR")
        print(f"Vous avez dit : {text}")

        if "rotation" in text.lower():
            print("✅ Commande reconnue : rotation")
            arduino.write(b'rotation\n')  # envoyer à Arduino

    except sr.UnknownValueError:
        print("❌ Je n'ai pas compris...")
    except sr.RequestError:
        print("⚠️ Problème avec le service Google Speech")
