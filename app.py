import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def get_finger_states(hand_landmarks):
    # Tip IDs: Thumb(4), Index(8), Middle(12), Ring(16), Pinky(20)
    # Pip IDs: Thumb(2), Index(6), Middle(10), Ring(14), Pinky(18)
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    
    states = {
        'thumb': hand_landmarks.landmark[4].y < hand_landmarks.landmark[2].y,
        'index': hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y,
        'middle': hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y,
        'ring': hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y,
        'pinky': hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y
    }
    return states

def draw_globe(img, color, text):
    h, w, _ = img.shape
    cv2.circle(img, (w//2, h//2), 150, color, -1)
    cv2.circle(img, (w//2, h//2), 160, (255,255,255), 3)
    cv2.putText(img, text, (w//2 - 200, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

# Main Loop
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success: break
    
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    active_tech = "NONE"
    
    if results.multi_hand_landmarks:
        hand_data = []
        for hand_lms in results.multi_hand_landmarks:
            # Draw Skeleton
            mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
            hand_data.append(get_finger_states(hand_lms))
            
        # GESTURE ENGINE
        if len(hand_data) == 2:
            # SHRINE: Both palms open
            if hand_data[0]['index'] and hand_data[1]['index'] and hand_data[0]['pinky'] and hand_data[1]['pinky']:
                active_tech = "SHRINE"
        elif len(hand_data) == 1:
            h1 = hand_data[0]
            # PURPLE: Open Palm
            if h1['index'] and h1['middle'] and h1['ring'] and h1['pinky']:
                active_tech = "PURPLE"
            # RED: Rock-on (Thumb, Index, Pinky)
            elif h1['thumb'] and h1['index'] and h1['pinky'] and not h1['middle']:
                active_tech = "RED"
            # VOID: Peace Sign
            elif h1['index'] and h1['middle'] and not h1['ring']:
                active_tech = "VOID"

    # APPLY VISUALS
    if active_tech == "VOID":
        frame = cv2.bitwise_not(frame)
        draw_globe(frame, (255, 100, 0), "UNLIMITED VOID")
    elif active_tech == "RED":
        draw_globe(frame, (0, 0, 255), "TECHNIQUE: RED")
    elif active_tech == "PURPLE":
        draw_globe(frame, (255, 0, 150), "HOLLOW PURPLE")
    elif active_tech == "SHRINE":
        draw_globe(frame, (0, 70, 255), "MALEVOLENT SHRINE")
        
    cv2.imshow('JJK Vision Python', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()