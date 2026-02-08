import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
import mediapipe as mp
import numpy as np

# MediaPipe Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

class JJKTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        
        active_tech = "NONE"
        color = (255, 255, 255)

        if results.multi_hand_landmarks:
            hand_states = []
            for res in results.multi_hand_landmarks:
                # Basic Skeleton
                mp.solutions.drawing_utils.draw_landmarks(img, res, mp_hands.HAND_CONNECTIONS)
                
                # Finger Logic
                s = {
                    'index': res.landmark[8].y < res.landmark[6].y,
                    'middle': res.landmark[12].y < res.landmark[10].y,
                    'ring': res.landmark[16].y < res.landmark[14].y,
                    'pinky': res.landmark[20].y < res.landmark[18].y,
                    'thumb': res.landmark[4].y < res.landmark[2].y
                }
                hand_states.append(s)

            # --- GESTURE ENGINE ---
            if len(hand_states) == 2:
                # SHRINE: Two Palms
                if hand_states[0]['index'] and hand_states[1]['index'] and hand_states[0]['pinky'] and hand_states[1]['pinky']:
                    active_tech = "MALEVOLENT SHRINE"
                    color = (0, 50, 255) # Red-ish BGR
            elif len(hand_states) == 1:
                h1 = hand_states[0]
                # PURPLE: Open Palm
                if h1['index'] and h1['middle'] and h1['ring'] and h1['pinky']:
                    active_tech = "HOLLOW PURPLE"
                    color = (200, 0, 150)
                # RED: Rock-on
                elif h1['thumb'] and h1['index'] and h1['pinky'] and not h1['middle']:
                    active_tech = "REVERSAL: RED"
                    color = (0, 0, 255)
                # VOID: Peace Sign
                elif h1['index'] and h1['middle'] and not h1['ring']:
                    active_tech = "UNLIMITED VOID"
                    color = (255, 100, 0)

        # Draw UI
        if active_tech != "NONE":
            cv2.circle(img, (w//2, h//2), 100, color, -1)
            cv2.putText(img, active_tech, (50, h-50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 4)
            if active_tech == "UNLIMITED VOID":
                img = cv2.bitwise_not(img)

        return img

st.title("🧿 JJK Vision System (Python Web)")
st.write("Pose Guide: Peace (Void) | Rock-on (Red) | Palm (Purple) | 2 Palms (Shrine)")

webrtc_streamer(key="jjk", video_transformer_factory=JJKTransformer)
