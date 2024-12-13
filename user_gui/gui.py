import customtkinter as ctk
import pygame
import cv2
import threading
import main

class LoadingScreen(ctk.CTk):
    def __init__(self, g, video_path):
        super().__init__()

        self.g = g
        self.video_path = video_path

        # Automatically detect screen size
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        self.title("Loading...")
        self.geometry(f"{self.screen_width}x{self.screen_height}")
        self.configure(fg_color="#2c2f39")

        # Create a stop event to signal the Pygame loop
        self.stop_event = threading.Event()

        # Start the Pygame loop in the main thread
        self.after(100, self.play_video)

    def play_video(self):
        pygame.init()
        pygame.display.set_caption('Loading....')
        screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        clock = pygame.time.Clock()

        cap = cv2.VideoCapture(self.video_path)
        success, frame = cap.read()

        while success and not self.stop_event.is_set():
            # Resize frame to match screen size
            frame_resized = cv2.resize(frame, (self.screen_width, self.screen_height))
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(frame_rgb)
            screen.blit(frame_surface, (0, 0))
            pygame.display.update()
            success, frame = cap.read()
            clock.tick(30)  # Limit to 30 FPS

        cap.release()
        pygame.quit()

        self.destroy_loading_screen()

    def destroy_loading_screen(self):
        self.stop_event.set()
        self.destroy()
        self.g.gui_main()

# Example usage
if __name__ == "__main__":
    video_path = "a.mp4"
    loading_screen = LoadingScreen(main, video_path)
    loading_screen.mainloop()
