import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
import numpy as np
import mediapipe as mp

# RESILIENT IMPORT LOGIC
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

class JJKTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        
        # Process MediaPipe
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        
        active_tech = "NONE"
        color = (255, 255, 255)

        if results.multi_hand_landmarks:
            hand_states = []
            for res in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(img, res, mp_hands.HAND_CONNECTIONS)
                
                # Finger State Logic
                # Index Tip (8) < Index Pip (6)
                s = {
                    'index': res.landmark[8].y < res.landmark[6].y,
                    'middle': res.landmark[12].y < res.landmark[10].y,
                    'ring': res.landmark[16].y < res.landmark[14].y,
                    'pinky': res.landmark[20].y < res.landmark[18].y,
                    'thumb': res.landmark[4].y < res.landmark[2].y
                }
                hand_states.append(s)

            # --- MASTER GESTURE ENGINE ---
            if len(hand_states) == 2:
                # SHRINE: Double Palm (Both hands show index and pinky up)
                if hand_states[0]['index'] and hand_states[0]['pinky'] and \
                   hand_states[1]['index'] and hand_states[1]['pinky']:
                    active_tech = "MALEVOLENT SHRINE"
                    color = (0, 0, 255)
            elif len(hand_states) == 1:
                h1 = hand_states[0]
                # PURPLE: Open Palm (All 4 main fingers up)
                if h1['index'] and h1['middle'] and h1['ring'] and h1['pinky']:
                    active_tech = "HOLLOW PURPLE"
                    color = (255, 0, 150)
                # RED: Rock-on (Thumb, Index, Pinky up, Middle/Ring down)
                elif h1['thumb'] and h1['index'] and h1['pinky'] and not h1['middle']:
                    active_tech = "REVERSAL: RED"
                    color = (0, 0, 255)
                # VOID: Peace Sign (Index, Middle up, Ring down)
                elif h1['index'] and h1['middle'] and not h1['ring']:
                    active_tech = "UNLIMITED VOID"
                    color = (255, 100, 0)

        # Apply Visuals
        if active_tech != "NONE":
            cv2.putText(img, active_tech, (50, 100), cv2.FONT_HERSHEY_TRIPLEX, 2, color, 5)
            if active_tech == "UNLIMITED VOID":
                img = cv2.bitwise_not(img)
            else:
                cv2.circle(img, (w//2, h//2), 160, color, -1)

        return img

st.title("Jujutsu High Vision System")
webrtc_streamer(key="jjk", video_transformer_factory=JJKTransformer)
