import customtkinter as ctk
import threading
import main

class LoadingScreen(ctk.CTk):
    def __init__(self, g):
        super().__init__()

        self.g = g

        self.title("Welcome")
        self.geometry("400x200")  # Smaller window size
        self.configure(fg_color="#2c2f39")

        # Display welcome message
        self.label = ctk.CTkLabel(self, text="Welcome", font=("Arial", 24))
        self.label.pack(expand=True)

        # Proceed after 1 second
        self.after(1000, self.destroy_loading_screen)

    def destroy_loading_screen(self):
        self.destroy()
        self.g.gui_main()

# Example usage
if __name__ == "__main__":
    loading_screen = LoadingScreen(main)
    loading_screen.mainloop()
