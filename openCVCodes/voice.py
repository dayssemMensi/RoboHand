import serial
import time
import speech_recognition as sr

# Modifier selon ton port série
arduino = serial.Serial('COM5', 9600)
time.sleep(2)

recognizer = sr.Recognizer()
mic = sr.Microphone()

def chiffre_to_command(text):
    text = text.lower()
    command = ['0'] * 5

    if "1" in text or "un" in text:
        command[0] = '1'  # pouce
    if "2" in text or "deux" in text:
        command[1] = '1'  # index
    if "3" in text or "trois" in text:
        command[2] = '1'  # majeur
    if "4" in text or "quatre" in text:
        command[3] = '1'  # annulaire
    if "5" in text or "cinq" in text:
        command[4] = '1'  # auriculaire
    if "6" in text or "six" in text:
        command = ['1'] * 5  # ouvrir la main
    if "7" in text or "sept" in text:
        command = ['0'] * 5  # fermer la main

    return ''.join(command)

print("🎤 Dites un chiffre entre 1 et 7 :")
print("  1 à 5 → activer un doigt")
print("  6 → ouvrir la main")
print("  7 → fermer la main")
print("  'stop' → quitter")

try:
    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("🔊 Parlez...")
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language='fr-FR')
            print("🗣️ Vous avez dit :", text)

            if "stop" in text.lower():
                print("🛑 Fin du programme vocale.")
                break

            cmd = chiffre_to_command(text)
            if cmd == "00000":
                print("⚠️ Aucun doigt activé.")
                continue

            serial_cmd = f"${cmd}"
            print("📤 Envoi vers Arduino :", serial_cmd)
            arduino.write(serial_cmd.encode())
            time.sleep(1)

        except sr.UnknownValueError:
            print("🤷 Je n'ai pas compris.")
        except sr.RequestError:
            print("❌ Erreur réseau avec Google Speech API.")

except KeyboardInterrupt:
    print("\n🛑 Programme arrêté manuellement.")

finally:
    arduino.close()
