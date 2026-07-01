import flet as ft
import threading
import time 
import gc
import os
import config
from engine import WindowsAssistantEngine

def main(page: ft.Page):
    page.title = f"{config.ASSISTANT_NAME} Core UI"
    page.bgcolor = config.COLOR_BG_DARK
    page.padding = 20
    
    page.window_width = config.WINDOW_WIDTH
    page.window_height = config.WINDOW_HEIGHT
    page.window_resizable = True
    page.window_min_width = config.WINDOW_MIN_WIDTH
    page.window_min_height = config.WINDOW_MIN_HEIGHT
    
    engine = WindowsAssistantEngine()
    chat_history_list = ft.ListView(expand=True, spacing=14, auto_scroll=True)

    # --- FIXED LOGO AND ATTRIBUTE FALLBACK ICON ---
    from config import logo_path
    if os.path.exists(logo_path):
        logo_widget = ft.Image(src=logo_path, width=24, height=24, border_radius=12)
    else:
        logo_widget = ft.Icon(ft.icons.ACCOUNT_CIRCLE_ROUNDED, color=config.COLOR_ACCENT, size=24)

    status_indicator = ft.Icon(ft.icons.HEARING_ROUNDED, color=config.COLOR_ACCENT, size=18)
    status_text = ft.Text(f"{config.ASSISTANT_NAME} Always-On • {engine.current_city}", size=11, color=config.COLOR_TEXT_MUTED, weight=ft.FontWeight.W_500)

    mic_icon = ft.Icon(ft.icons.MIC_ROUNDED, color=config.COLOR_ACCENT, size=24)
    mic_container = ft.Container(
        content=mic_icon, width=50, height=50, bgcolor=config.COLOR_INPUT_BG, shape=ft.BoxShape.CIRCLE,
        alignment=ft.alignment.center, animate=ft.Animation(200, ft.AnimationCurve.DECELERATE)
    )

    send_icon = ft.Icon(ft.icons.SEND_ROUNDED, color=ft.colors.WHITE, size=20)
    send_container = ft.Container(
        content=send_icon, width=50, height=50, bgcolor=config.COLOR_ACCENT, border_radius=10,
        alignment=ft.alignment.center, animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
    )

    def build_chat_bubble(sender: str, message: str):
        is_user = (sender == "You")
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text(sender, weight=ft.FontWeight.BOLD, size=11, color=config.COLOR_TEXT_MUTED),
                        ft.Text(message, size=14, color=config.COLOR_TEXT_PRIMARY, selectable=True),
                    ], spacing=4),
                    bgcolor=config.COLOR_BUBBLE_USER if is_user else config.COLOR_BUBBLE_AIRA,
                    padding=12,
                    border_radius=ft.border_radius.all(12),
                    width=340,  
                )
            ],
            alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
        )

    def handle_text_submit(e):
        user_raw_text = text_input_field.value.strip()
        if not user_raw_text:
            return
        text_input_field.value = ""
        process_and_respond(user_raw_text)

    def process_and_respond(user_text):
        chat_history_list.controls.append(build_chat_bubble("You", str(user_text)))
        
        status_indicator.icon = ft.icons.AUTORENEW
        status_indicator.icon_color = ft.colors.BLUE_ACCENT_200
        status_text.value = f"{config.ASSISTANT_NAME}: Working..."
        page.update()
        
        engine_response = engine.execute_intent(user_text)
        
        status_indicator.icon = ft.icons.HEARING_ROUNDED
        status_indicator.icon_color = config.COLOR_ACCENT
        status_text.value = f"{config.ASSISTANT_NAME} Always-On • {engine.current_city}"
        
        chat_history_list.controls.append(build_chat_bubble(config.ASSISTANT_NAME, engine_response))
        page.update()

        threading.Thread(target=lambda: engine.speak(engine_response), daemon=True).start()
        gc.collect() 

    async def state_update_listening():
        status_indicator.icon = ft.icons.RECORD_VOICE_OVER_ROUNDED
        status_indicator.icon_color = ft.colors.RED_ACCENT_400
        status_text.value = f"{config.ASSISTANT_NAME}: Listening..."
        mic_container.bgcolor = "#E81123"  
        mic_icon.color = ft.colors.WHITE
        mic_container.scale = 1.15         
        page.update()

    def UI_listening_trigger():
        page.run_task(state_update_listening)

    def UI_command_trigger(text_out, success):
        async def thread_safe_append():
            status_indicator.icon = ft.icons.HEARING_ROUNDED
            status_indicator.icon_color = config.COLOR_ACCENT
            status_text.value = f"{config.ASSISTANT_NAME} Always-On • {engine.current_city}"
            mic_container.bgcolor = config.COLOR_INPUT_BG
            mic_icon.color = config.COLOR_ACCENT
            mic_container.scale = 1.0
            page.update()
            if success:
                process_and_respond(text_out)
        page.run_task(thread_safe_append)

    def start_listening_thread(e):
        def loop_start():
            time.sleep(1.0)
            engine.monitor_continuous_stream(UI_listening_trigger, UI_command_trigger)
        threading.Thread(target=loop_start, daemon=True).start()

    def trigger_manual_listening():
        engine.pause_background_mic = True
        UI_listening_trigger()
        
        def manual_audio_fetch():
            try:
                import speech_recognition as sr
                import pyaudiowpatch as pyaudio
                time.sleep(0.1)
                p = pyaudio.PyAudio()
                idx = p.get_default_input_device_info().get("index")
                p.terminate()
                
                with sr.Microphone(device_index=idx) as manual_src:
                    engine.recognizer.adjust_for_ambient_noise(manual_src, duration=0.2)
                    audio_captured = engine.recognizer.listen(manual_src, timeout=3, phrase_time_limit=4)
                    spoken_text = engine.recognizer.recognize_google(audio_captured)
                    UI_command_trigger(spoken_text, True)
            except Exception:
                UI_command_trigger("", False)
            finally:
                engine.pause_background_mic = False

        threading.Thread(target=manual_audio_fetch, daemon=True).start()

    # Bind Interactions
    mic_container.on_click = lambda e: trigger_manual_listening()
    mic_container.on_hover = lambda e: setattr(mic_container, "scale", 1.1 if e.data == "true" else 1.0) or mic_container.update()

    # Keyboard Shortcut Trigger Handler
    def handle_global_shortcuts(e: ft.KeyboardEvent):
        if e.ctrl and e.alt and e.key.lower() == "a":
            trigger_manual_listening()

    page.on_keyboard_event = handle_global_shortcuts

    text_input_field = ft.TextField(
        hint_text="Type command or press Ctrl+Alt+A...", fill_color=config.COLOR_INPUT_BG, filled=True, border_radius=10,
        border_color=ft.colors.TRANSPARENT, focused_border_color=config.COLOR_ACCENT,
        text_style=ft.TextStyle(color=config.COLOR_TEXT_PRIMARY), hint_style=ft.TextStyle(color=config.COLOR_TEXT_MUTED),
        on_submit=handle_text_submit, expand=True
    )

    header_row = ft.Row([logo_widget, status_indicator, status_text], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    page.add(
        ft.Column([
            ft.Container(content=header_row, padding=8, border=ft.border.only(bottom=ft.BorderSide(1, "#1F232D"))),
            chat_history_list,
            ft.Row([text_input_field, mic_container, send_container], spacing=8)
        ], expand=True)
    )

    page.on_connect = start_listening_thread

if __name__ == "__main__":
    ft.app(target=main)