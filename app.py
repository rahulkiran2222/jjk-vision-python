import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import cv2
import numpy as np

# DIRECT IMPORTS to bypass the "solutions" AttributeError
import mediapipe as mp
from mediapipe.python.solutions import hands as mp_hands
from mediapipe.python.solutions import drawing_utils as mp_draw

# Initialize Hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

class JJKProcessor(VideoProcessorBase):
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        
        # Process MediaPipe
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        
        active_tech = "NONE"
        color = (255, 255, 255)

        if results.multi_hand_landmarks:
            states = []
            for res in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, res, mp_hands.HAND_CONNECTIONS)
                
                # Logic: Index(8), Middle(12), Ring(16), Pinky(20), Thumb(4)
                s = {
                    'index': res.landmark[8].y < res.landmark[6].y,
                    'middle': res.landmark[12].y < res.landmark[10].y,
                    'ring': res.landmark[16].y < res.landmark[14].y,
                    'pinky': res.landmark[20].y < res.landmark[18].y,
                    'thumb': res.landmark[4].y < res.landmark[2].y
                }
                states.append(s)

            # GESTURE ENGINE
            if len(states) == 2:
                # MALEVOLENT SHRINE: Both Palms Open
                if states[0]['index'] and states[1]['index'] and states[0]['pinky'] and states[1]['pinky']:
                    active_tech = "SHRINE"
                    color = (0, 0, 255)
            elif len(states) == 1:
                h1 = states[0]
                # HOLLOW PURPLE: Open Palm
                if h1['index'] and h1['middle'] and h1['ring'] and h1['pinky']:
                    active_tech = "PURPLE"
                    color = (255, 0, 180)
                # RED: Rock-on (Thumb, Index, Pinky UP)
                elif h1['thumb'] and h1['index'] and h1['pinky'] and not h1['middle']:
                    active_tech = "RED"
                    color = (0, 0, 255)
                # VOID: Peace Sign (Index, Middle UP)
                elif h1['index'] and h1['middle'] and not h1['ring']:
                    active_tech = "VOID"
                    color = (255, 120, 0)

        # Draw Visuals
        if active_tech == "VOID":
            img = cv2.bitwise_not(img)
            cv2.putText(img, "UNLIMITED VOID", (50, 100), cv2.FONT_HERSHEY_TRIPLEX, 2, (255,255,255), 5)
        elif active_tech != "NONE":
            cv2.circle(img, (w//2, h//2), 150, color, -1)
            cv2.putText(img, active_tech, (50, 100), cv2.FONT_HERSHEY_TRIPLEX, 2, (255,255,255), 5)

        return frame.from_ndarray(img, format="bgr24")

st.title("Jujutsu High Vision System 🧿")
st.markdown("Peace (Void) | Rock-on (Red) | Palm (Purple) | 2 Palms (Shrine)")

webrtc_streamer(key="jjk", video_processor_factory=JJKProcessor)
