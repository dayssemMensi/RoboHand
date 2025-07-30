import cv2
import mediapipe as mp
import pygame
import speech_recognition as sr
import sys
import threading

### ======== Partie 1 : Mode Caméra ======== ###
def main_camera_mode():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils
    finger_tips = [4, 8, 12, 16, 20]

    cap = cv2.VideoCapture(0)

    def get_finger_states(hand_landmarks, handedness_label):
        states = []
        if handedness_label == 'Right':
            states.append(1 if hand_landmarks.landmark[finger_tips[0]].x < hand_landmarks.landmark[finger_tips[0] - 1].x else 0)
        else:
            states.append(1 if hand_landmarks.landmark[finger_tips[0]].x > hand_landmarks.landmark[finger_tips[0] - 1].x else 0)

        for tip_id in finger_tips[1:]:
            states.append(1 if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y else 0)
        return states

    while True:
        success, frame = cap.read()
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks and result.multi_handedness:
            for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                hand_label = handedness.classification[0].label
                states = get_finger_states(hand_landmarks, hand_label)
                state_labels = ['Pouce', 'Index', 'Majeur', 'Annulaire', 'Auriculaire']
                cv2.putText(frame, f"Main : {hand_label}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                y = 60
                for i, (label, state) in enumerate(zip(state_labels, states)):
                    cv2.putText(frame, f"{label}: {state}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    y += 30

        cv2.imshow("Mode Caméra - Détection des doigts", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


### ======== Partie 2 : Mode Voix (Pygame) ======== ###
def main_voice_mode():
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Main vocale animée")

    WHITE, SKIN, RED, BLACK = (255,255,255), (255,220,177), (255,0,0), (0,0,0)
    palm_center = (300, 250)

    fingers_base = {
        'pouce': [(240, 270), (220, 240), (230, 210), (250, 190)],
        'index': [(270, 220), (270, 180), (280, 140), (290, 110)],
        'majeur': [(300, 220), (300, 170), (310, 130), (320, 100)],
        'annulaire': [(330, 230), (340, 190), (350, 160), (350, 140)],
        'auriculaire': [(360, 240), (370, 210), (380, 190), (390, 180)]
    }

    font = pygame.font.SysFont(None, 28)

    def modifie_doigt(points, ouvert):
        if ouvert: return points
        return [(int(x + 0.7 * (palm_center[0] - x)), int(y + 0.7 * (palm_center[1] - y))) for (x, y) in points]

    def dessiner_main(etats, listening):
        screen.fill(WHITE)
        pygame.draw.circle(screen, SKIN, palm_center, 60)
        doigts = list(fingers_base.keys())
        for i, doigt in enumerate(doigts):
            pts = modifie_doigt(fingers_base[doigt], etats[i])
            for j in range(len(pts)):
                pygame.draw.circle(screen, RED, pts[j], 8)
                if j > 0:
                    pygame.draw.line(screen, BLACK, pts[j-1], pts[j], 6)
            pygame.draw.line(screen, BLACK, palm_center, pts[0], 8)

        text = font.render("Écoute en cours..." if listening else "", True, (0, 0, 255))
        screen.blit(text, (20, 20))
        pygame.display.flip()

    def reconnaissance_vocale():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Parlez maintenant...")
            audio = recognizer.listen(source)
        try:
            texte = recognizer.recognize_google(audio, language="fr-FR").lower()
            print("Commande reconnue :", texte)
            if "ouvre" in texte:
                return [1, 1, 1, 1, 1]
            elif "ferme" in texte:
                return [0, 0, 0, 0, 0]
            else:
                d = ["pouce", "index", "majeur", "annulaire", "auriculaire"]
                return [1 if nom in texte else 0 for nom in d]
        except:
            print("Erreur de reconnaissance.")
            return None

    def thread_reco(etats, flag):
        flag[0] = True
        resultat = reconnaissance_vocale()
        if resultat: etats[:] = resultat
        flag[0] = False

    etats = [0]*5
    flag = [False]
    clock = pygame.time.Clock()
    dessiner_main(etats, False)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not flag[0]:
                    print("Lancement de l’écoute vocale...")
                    threading.Thread(target=thread_reco, args=(etats, flag)).start()
                elif event.key == pygame.K_r:
                    etats[:] = [0]*5

        dessiner_main(etats, flag[0])
        clock.tick(30)


### ======== Menu principal ======== ###
def menu_principal():
    print("=== Choisissez un mode ===")
    print("1 - Mode Caméra (détection des doigts)")
    print("2 - Mode Vocale (commande vocale)")
    choix = input("Votre choix (1/2) : ").strip()

    if choix == '1':
        main_camera_mode()
    elif choix == '2':
        main_voice_mode()
    else:
        print("Choix invalide. Réessayez.")
        menu_principal()

if __name__ == "__main__":
    menu_principal()
