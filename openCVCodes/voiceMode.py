import pygame
import speech_recognition as sr
import sys
import threading

pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Main vocale animée avec points rouges")

WHITE = (255, 255, 255)
SKIN = (255, 220, 177)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

palm_center = (300, 250)

fingers_base = {
    'pouce': [(palm_center[0] - 60, palm_center[1] + 20),
              (palm_center[0] - 80, palm_center[1] - 10),
              (palm_center[0] - 70, palm_center[1] - 40),
              (palm_center[0] - 50, palm_center[1] - 60)],
    'index': [(palm_center[0] - 30, palm_center[1] - 30),
              (palm_center[0] - 30, palm_center[1] - 70),
              (palm_center[0] - 20, palm_center[1] - 110),
              (palm_center[0] - 10, palm_center[1] - 140)],
    'majeur': [(palm_center[0], palm_center[1] - 30),
               (palm_center[0], palm_center[1] - 80),
               (palm_center[0] + 10, palm_center[1] - 120),
               (palm_center[0] + 20, palm_center[1] - 150)],
    'annulaire': [(palm_center[0] + 30, palm_center[1] - 20),
                  (palm_center[0] + 40, palm_center[1] - 60),
                  (palm_center[0] + 50, palm_center[1] - 90),
                  (palm_center[0] + 50, palm_center[1] - 110)],
    'auriculaire': [(palm_center[0] + 60, palm_center[1] - 10),
                    (palm_center[0] + 70, palm_center[1] - 40),
                    (palm_center[0] + 80, palm_center[1] - 60),
                    (palm_center[0] + 90, palm_center[1] - 70)]
}

font = pygame.font.SysFont(None, 28)

def modifie_doigt(points, ouvert):
    if ouvert:
        return points
    else:
        new_points = []
        for (x, y) in points:
            dx = palm_center[0] - x
            dy = palm_center[1] - y
            new_x = x + 0.7 * dx
            new_y = y + 0.7 * dy
            new_points.append((int(new_x), int(new_y)))
        return new_points

def dessiner_main_etats(etats, listening):
    screen.fill(WHITE)
    pygame.draw.circle(screen, SKIN, palm_center, 60)

    doigts = ['pouce', 'index', 'majeur', 'annulaire', 'auriculaire']

    for i, doigt in enumerate(doigts):
        pts = modifie_doigt(fingers_base[doigt], etats[i])
        for j in range(len(pts)):
            pygame.draw.circle(screen, RED, pts[j], 8)
            if j > 0:
                pygame.draw.line(screen, BLACK, pts[j-1], pts[j], 6)
        pygame.draw.line(screen, BLACK, palm_center, pts[0], 8)

    # Texte mode écoute
    status_text = "Écoute vocale en cours..." if listening else "   "
    txt_surface = font.render(status_text, True, (0, 0, 255))
    screen.blit(txt_surface, (20, 20))

    pygame.display.flip()

def reconnaissance_vocale():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Parlez maintenant...")
        audio = recognizer.listen(source)

    try:
        texte = recognizer.recognize_google(audio, language="fr-FR").lower()
        print("Commande vocale reconnue :", texte)

        if "ouvre" in texte:
            return [1,1,1,1,1]
        elif "ferme" in texte:
            return [0,0,0,0,0]
        else:
            pattern = [0,0,0,0,0]
            if "pouce" in texte:
                pattern[0] = 1
            if "index" in texte:
                pattern[1] = 1
            if "majeur" in texte:
                pattern[2] = 1
            if "annulaire" in texte:
                pattern[3] = 1
            if "auriculaire" in texte or "petit doigt" in texte:
                pattern[4] = 1
            if sum(pattern) == 0:
                print("Commande vocale non reconnue pour les doigts.")
                return None
            return pattern
    except sr.UnknownValueError:
        print("Audio non compris.")
        return None
    except sr.RequestError as e:
        print("Erreur service vocal:", e)
        return None

def thread_reco_vocale(etats_doigts, flag_listening):
    flag_listening[0] = True
    nouveau_etat = reconnaissance_vocale()
    if nouveau_etat is not None:
        etats_doigts[:] = nouveau_etat
    flag_listening[0] = False

def boucle_principale():
    etats_doigts = [0,0,0,0,0]
    flag_listening = [False]  # mutable pour état écoute

    dessiner_main_etats(etats_doigts, False)

    clock = pygame.time.Clock()
    running = True

    reco_thread = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not flag_listening[0]:
                        print("Lancement reconnaissance vocale...")
                        reco_thread = threading.Thread(target=thread_reco_vocale, args=(etats_doigts, flag_listening))
                        reco_thread.start()
                elif event.key == pygame.K_r:
                    print("Réinitialisation main (doigts fermés).")
                    etats_doigts[:] = [0,0,0,0,0]

        dessiner_main_etats(etats_doigts, flag_listening[0])
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    print("Programme lancé.")
    print("Appuie ESPACE pour lancer reconnaissance vocale.")
    print("Appuie R pour fermer tous les doigts (reset).")
    boucle_principale()
