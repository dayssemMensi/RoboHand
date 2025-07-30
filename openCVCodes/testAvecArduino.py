import cv2
import mediapipe as mp
import serial
import time
import speech_recognition as sr

# Configuration du port série (⚠️ adapte COM5 selon ton port)
arduino = serial.Serial('COM5', 9600)
time.sleep(2)

# ------------------ MEDIA PIPE SETUP ------------------ #
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
finger_tips = [4, 8, 12, 16, 20]  # [Pouce, Index, Majeur, Annulaire, Auriculaire]

def get_finger_states(hand_landmarks, handedness_label):
    states = []
    if handedness_label == 'Right':
        states.append(int(hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x))
    else:
        states.append(int(hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x))

    for tip in finger_tips[1:]:
        states.append(int(hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y))
    return states

# ------------------ MODE VOCAL ------------------ #
def voice_control():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Parlez maintenant...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language='fr-FR')
            print("Commande vocale :", text)
            text = text.lower()

            if "ouvre tout" in text:
                return "$00000"
            elif "ferme tout" in text:
                return "$11111"
            elif "pouce" in text:
                return "$10000"
            elif "index" in text:
                return "$01000"
            elif "majeur" in text:
                return "$00100"
            elif "annulaire" in text:
                return "$00010"
            elif "auriculaire" in text or "petit doigt" in text:
                return "$00001"
            else:
                print("Commande non reconnue")
                return None
        except sr.UnknownValueError:
            print("Je n’ai pas compris.")
        except sr.RequestError as e:
            print("Erreur du service vocal :", e)
    return None

# ------------------ MENU DE CHOIX ------------------ #
mode = input("Choisir le mode (camera / voix): ").strip().lower()

# ------------------ MODE CAMERA ------------------ #
if mode == "camera":
    cap = cv2.VideoCapture(0)
    print("Mode caméra activé. Appuyez sur 'q' pour quitter.")
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks and result.multi_handedness:
            for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                hand_label = handedness.classification[0].label
                states = get_finger_states(hand_landmarks, hand_label)
                data_str = "$" + ''.join(str(s) for s in states)
                print("Envoi à Arduino :", data_str)
                arduino.write(data_str.encode())

                # Affichage visuel
                cv2.putText(frame, f"Main : {hand_label}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                y = 60
                for i, state in enumerate(states):
                    cv2.putText(frame, f"{['Pouce', 'Index', 'Majeur', 'Annulaire', 'Auriculaire'][i]}: {state}",
                                (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    y += 30

        cv2.imshow("Détection des doigts - OpenCV", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ------------------ MODE VOIX ------------------ #
elif mode == "voix":
    print("Mode vocal activé. Dites une commande. (CTRL+C pour arrêter)")
    while True:
        command = voice_control()
        if command:
            print("Envoi à Arduino :", command)
            arduino.write(command.encode())

        again = input("Voulez-vous refaire une commande ? (o/n) : ").strip().lower()
        if again != 'o':
            break

else:
    print("Mode inconnu. Tapez soit 'camera', soit 'voix'.")
