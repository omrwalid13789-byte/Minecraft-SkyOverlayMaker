import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from PIL import Image, ImageTk


class SkyboxGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("2x3 Skybox Generator")
        self.root.geometry("560x580")
        self.root.resizable(False, False)

        self.input_image_path = None
        self.preview_window = None

        # --- Create GUI ---
        self.create_widgets()

    def create_widgets(self):
        """Creates and arranges all the GUI widgets."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # --- Title ---
        title_label = ttk.Label(main_frame, text="2x3 Skybox Generator", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # --- Image Selection ---
        ttk.Label(main_frame, text="Select Any Image to Use as Skybox:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.select_button = ttk.Button(main_frame, text="Browse...", command=self.select_image)
        self.select_button.grid(row=1, column=1, sticky=tk.E, pady=5, padx=(10, 0))

        self.image_path_label = ttk.Label(main_frame, text="No image selected", wraplength=350, foreground="gray")
        self.image_path_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # --- Output Resolution ---
        ttk.Label(main_frame, text="Output Resolution:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.resolution_var = tk.StringVar(value="512x512")
        resolution_combo = ttk.Combobox(main_frame, textvariable=self.resolution_var,
                                        values=["256x256", "512x512", "1024x1024", "2048x2048"], state="readonly",
                                        width=15)
        resolution_combo.grid(row=3, column=1, sticky=tk.E, pady=5, padx=(10, 0))

        # --- Action Buttons ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        self.preview_button = ttk.Button(button_frame, text="Show Low-Res Preview", command=self.show_preview,
                                         state=tk.DISABLED)
        self.preview_button.pack(side=tk.LEFT, padx=5)

        self.generate_button = ttk.Button(button_frame, text="Generate Full-Res Skybox", command=self.generate_skybox,
                                          state=tk.DISABLED)
        self.generate_button.pack(side=tk.LEFT, padx=5)

        # --- Output Format Options ---
        self.generate_net_var = tk.BooleanVar(value=True)
        self.generate_separate_var = tk.BooleanVar(value=True)
        net_check = ttk.Checkbutton(main_frame, text="Generate Combined Net Image", variable=self.generate_net_var)
        net_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=2)
        separate_check = ttk.Checkbutton(main_frame, text="Generate 6 Separate Files (for Minecraft)",
                                         variable=self.generate_separate_var)
        separate_check.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=2)

        # --- Status Label ---
        self.status_label = ttk.Label(main_frame, text="Status: Ready", font=("Helvetica", 10, "italic"))
        self.status_label.grid(row=7, column=0, columnspan=2, pady=10)

        # --- Final Layout Preview (Updated to 2x3) ---
        ttk.Label(main_frame, text="This is the exact layout the generator will create:",
                  font=("Helvetica", 11, "bold")).grid(row=8, column=0, columnspan=2, pady=(15, 5))

        layout_frame = ttk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=2)
        layout_frame.grid(row=9, column=0, columnspan=2, pady=5)

        # Visual guide to the NEW 2x3 layout
        layout_data = [
            ("  Bottom  ", "   Top   ", "   Back  "),
            ("   Left   ", "  Front  ", "  Right  "),
        ]
        for r, row_data in enumerate(layout_data):
            for c, text in enumerate(row_data):
                ttk.Label(layout_frame, text=text, relief=tk.RIDGE, padding=10).grid(row=r, column=c, padx=1, pady=1)

        # --- Instructions ---
        instructions_text = (
            "Use 'Show Preview' to check if your image looks good\n"
            "with the template before generating the final files."
        )
        instructions_label = ttk.Label(main_frame, text=instructions_text, justify=tk.CENTER, foreground="blue",
                                       font=("Helvetica", 9))
        instructions_label.grid(row=10, column=0, columnspan=2, pady=5)

    def select_image(self):
        """Opens a file dialog to select an image."""
        filepath = filedialog.askopenfilename(
            title="Select an Image to Use as Skybox",
            filetypes=(("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*"))
        )
        if filepath:
            self.input_image_path = filepath
            filename = os.path.basename(filepath)
            self.image_path_label.config(text=filename, foreground="black")
            self.preview_button.config(state=tk.NORMAL)
            self.generate_button.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Image loaded. Use 'Show Preview' first.")

    def create_net_image(self, output_size):
        """Core logic to crop and assemble the net image."""
        with Image.open(self.input_image_path) as img:
            width, height = img.size

            side_width = width // 4
            side_height = height // 2

            faces = {
                "posz": (side_width, side_height // 2, side_width * 2, side_height // 2 + side_height),  # Front
                "negx": (0, side_height // 2, side_width, side_height // 2 + side_height),  # Left
                "negz": (side_width * 3, side_height // 2, width, side_height // 2 + side_height),  # Back
                "posx": (side_width * 2, side_height // 2, side_width * 3, side_height // 2 + side_height),  # Right
                "posy": (side_width, 0, side_width * 2, side_height // 2),  # Top
                "negy": (side_width, height - side_height // 2, side_width * 2, height)  # Bottom
            }

            # --- UPDATED: Create a 2x3 grid ---
            net_width = output_size * 3
            net_height = output_size * 2  # Changed from 3 to 2
            net_image = Image.new('RGB', (net_width, net_height))

            # --- UPDATED: Layout for the 2x3 grid ---
            layout = {
                "negy": (0, 0), "posy": (1, 0), "negz": (2, 0),
                "negx": (0, 1), "posz": (1, 1), "posx": (2, 1),
            }

            for face_name, box in faces.items():
                face_img = img.crop(box)
                face_img = face_img.resize((output_size, output_size), Image.Resampling.LANCZOS)
                grid_x, grid_y = layout[face_name]
                paste_x = grid_x * output_size
                paste_y = grid_y * output_size
                net_image.paste(face_img, (paste_x, paste_y))

            return net_image

    def show_preview(self):
        """Generates and displays a low-resolution preview."""
        if not self.input_image_path:
            messagebox.showerror("Error", "Please select an image first.")
            return

        self.status_label.config(text="Status: Generating preview...")
        self.root.update_idletasks()

        try:
            preview_img = self.create_net_image(output_size=128)

            if self.preview_window:
                self.preview_window.destroy()

            self.preview_window = tk.Toplevel(self.root)
            self.preview_window.title("Skybox Preview")

            photo = ImageTk.PhotoImage(preview_img)

            label = ttk.Label(self.preview_window, image=photo)
            label.image = photo
            label.pack(padx=10, pady=10)

            self.status_label.config(text="Status: Preview generated. Check the new window.")

        except Exception as e:
            messagebox.showerror("Preview Error", f"Could not generate preview.\nError: {e}")
            self.status_label.config(text="Status: Preview failed.")

    def generate_skybox(self):
        """Main function to process the image and create the final skybox."""
        if not self.generate_net_var.get() and not self.generate_separate_var.get():
            messagebox.showerror("Error", "Please select at least one output format.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Folder for Skybox")
        if not output_dir:
            self.status_label.config(text="Status: Generation cancelled.")
            return

        try:
            self.status_label.config(text="Status: Generating full-resolution files...")
            self.root.update_idletasks()

            output_size = int(self.resolution_var.get().split('x')[0])

            if self.generate_net_var.get():
                net_image = self.create_net_image(output_size=output_size)
                # --- UPDATED: Filename for the new layout ---
                net_image.save(os.path.join(output_dir, "skybox_2x3_template.png"))

            if self.generate_separate_var.get():
                with Image.open(self.input_image_path) as img:
                    width, height = img.size
                    side_width = width // 4
                    side_height = height // 2
                    faces = {
                        "posz": (side_width, side_height // 2, side_width * 2, side_height // 2 + side_height),
                        "negx": (0, side_height // 2, side_width, side_height // 2 + side_height),
                        "negz": (side_width * 3, side_height // 2, width, side_height // 2 + side_height),
                        "posx": (side_width * 2, side_height // 2, side_width * 3, side_height // 2 + side_height),
                        "posy": (side_width, 0, side_width * 2, side_height // 2),
                        "negy": (side_width, height - side_height // 2, side_width * 2, height)
                    }
                    for face_name, box in faces.items():
                        face_img = img.crop(box)
                        face_img = face_img.resize((output_size, output_size), Image.Resampling.LANCZOS)
                        face_img.save(os.path.join(output_dir, f"skybox_{face_name}.png"))

            self.status_label.config(text=f"Status: Success! Files saved to {output_dir}")
            messagebox.showinfo("Success", f"Skybox generated successfully in:\n{output_dir}")

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")
            self.status_label.config(text="Status: An error occurred.")


if __name__ == "__main__":
    root = tk.Tk()
    app = SkyboxGeneratorApp(root)
    root.mainloop()
