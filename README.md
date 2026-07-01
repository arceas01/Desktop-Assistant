# Desktop-Assistant
This project is a modular, high-performance Windows desktop virtual assistant framework engineered using Python and the Flet UI framework. Dubbed AIRA Core UI, it combines a clean, dark-themed, responsive user interface with an intelligent background automation engine.

A standout feature of the project is its always-on continuous listening pipeline, which operates via PyAudioWPatch and SpeechRecognition. By monitoring voice streams smoothly in the background, it completely eliminates the need for an unreliable wake word. Users can seamlessly issue spoken commands—such as "Open Notepad" or "Open WhatsApp"—and the engine captures, transcribes, and executes them instantly. It also integrates custom image branding (logo.jpg) directly into the status bar and supports an app-focused global hotkey (Ctrl + Alt + A) to manually force microphone capture.

On the backend, the architecture optimizes system tasks like launching applications, querying local weather details, or playing media streams. It resolves deep Windows app-routing edge cases by using direct OS protocol hooks (like whatsapp://), ensuring instant, native desktop execution without interfering with browser shortcuts or falling back to the Windows File Manager.
<img width="542" height="870" alt="image" src="https://github.com/user-attachments/assets/865d3475-f19d-4b2e-b867-1003822dc452" /> <img width="545" height="871" alt="image" src="https://github.com/user-attachments/assets/11f8f47f-067b-4a6b-bfab-2972e6edef80" />

