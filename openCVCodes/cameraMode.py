import cv2
import mediapipe as mp

# Initialisation MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Points clés des bouts de doigts
finger_tips = [4, 8, 12, 16, 20]  # [Pouce, Index, Majeur, Annulaire, Auriculaire]

# Ouvrir la caméra
cap = cv2.VideoCapture(0)

def get_finger_states(hand_landmarks, handedness_label):
    states = []

    # Détection du pouce : comparaison horizontale
    if handedness_label == 'Right':
        # Si main droite : pouce pointé vers la gauche -> tip.x < joint.x
        if hand_landmarks.landmark[finger_tips[0]].x < hand_landmarks.landmark[finger_tips[0] - 1].x:
            states.append(1)
        else:
            states.append(0)
    else:  # Left
        # Si main gauche : pouce pointé vers la droite -> tip.x > joint.x
        if hand_landmarks.landmark[finger_tips[0]].x > hand_landmarks.landmark[finger_tips[0] - 1].x:
            states.append(1)
        else:
            states.append(0)

    # Autres doigts : comparaison verticale (y)
    for tip_id in finger_tips[1:]:
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
            states.append(1)
        else:
            states.append(0)

    return states

while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks and result.multi_handedness:
        for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Déterminer main gauche ou droite
            hand_label = handedness.classification[0].label  # 'Left' ou 'Right'

            # Calcul des états
            states = get_finger_states(hand_landmarks, hand_label)
            state_labels = ['Pouce', 'Index', 'Majeur', 'Annulaire', 'Auriculaire']

            # Afficher le label de la main
            cv2.putText(frame, f"Main : {hand_label}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # Afficher l'état de chaque doigt
            y = 60
            for i, (label, state) in enumerate(zip(state_labels, states)):
                cv2.putText(frame, f"{label}: {state}", (10, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y += 30

    cv2.imshow("Test caméra - Détection des doigts", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()