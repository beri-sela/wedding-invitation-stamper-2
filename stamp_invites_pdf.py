import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait
from io import BytesIO
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser

# -------------------------------------------------------
# Fit text to width using Pillow 10+ safe method
# -------------------------------------------------------
def fit_text(draw, text, font_path, max_font_size, max_width):
    font_size = max_font_size
    while font_size > 10:
        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            return font
        font_size -= 2
    return ImageFont.truetype(font_path, 10)

# -------------------------------------------------------
# Create final combined PDF
# -------------------------------------------------------
def create_final_pdf(stamped_png_path, destination_pdf_path="utils/details.pdf"):
    """
    Combines stamped PNG as first page + all pages from destination PDF.
    Resizes to match the stamped image's size.
    """
    try:
        img = Image.open(stamped_png_path)
        width_px, height_px = img.size
        dpi = img.info.get("dpi", (300, 300))[0]  # Default to 300 DPI if not embedded
        width_pt = width_px * 72 / dpi
        height_pt = height_px * 72 / dpi
        page_size = portrait((width_pt, height_pt))

        # Convert stamped image to PDF in memory
        img_pdf_buffer = BytesIO()
        c = canvas.Canvas(img_pdf_buffer, pagesize=page_size)
        c.drawInlineImage(stamped_png_path, 0, 0, width=width_pt, height=height_pt)
        c.showPage()
        c.save()
        img_pdf_buffer.seek(0)

        # Read both PDFs
        stamped_pdf = PdfReader(img_pdf_buffer)
        dest_pdf = PdfReader(open(destination_pdf_path, "rb"))

        writer = PdfWriter()
        writer.add_page(stamped_pdf.pages[0])

        # Match page size for all destination pages
        for page in dest_pdf.pages:
            page.scale_to(width_pt, height_pt)
            writer.add_page(page)

        output_pdf_path = stamped_png_path.replace(".png", ".pdf")
        with open(output_pdf_path, "wb") as out_pdf:
            writer.write(out_pdf)

        print(f"✅ Created: {output_pdf_path}")

    except Exception as e:
        print(f"❌ Error generating PDF for {stamped_png_path}: {e}")

# -------------------------------------------------------
# Generate Invitations (PNG + combined PDF)
# -------------------------------------------------------
def generate_invites(template_file, csv_file, name_font_file, table_font_file,
                     name_font_size, table_font_size, name_color, table_color,
                     table_x, table_y, name_x, name_y, destination_pdf):

    out_dir = "invites"
    os.makedirs(out_dir, exist_ok=True)

    df = pd.read_csv(csv_file)

    for _, row in df.iterrows():
        table = str(row["Table"])
        name = str(row["Name"])

        img = Image.open(template_file).convert("RGBA")
        W, H = img.size
        draw = ImageDraw.Draw(img)

        # Format table
        if int(table) < 10:
            table = f"0{table}"
        table_text = f"T&L2k25 - {table}"

        # Fit fonts
        table_font = fit_text(draw, table_text, table_font_file, table_font_size, W * 0.35)
        name_font = fit_text(draw, name, name_font_file, name_font_size, W * 0.8)

        # Draw table
        draw.text((table_x, table_y), table_text, fill=table_color, font=table_font)

        # Draw name (auto-center if name_x == -1)
        if name_x == -1:
            bbox = draw.textbbox((0, 0), name, font=name_font)
            name_w = bbox[2] - bbox[0]
            name_x_calc = (W - name_w) / 2
        else:
            name_x_calc = name_x

        draw.text((name_x_calc, name_y), name, fill=name_color, font=name_font)

        prefix = f"Thea and Louis Wedding Invite - {table} - {name}"
        png_path = os.path.join(out_dir, f"{prefix}.png")
        img.save(png_path, optimize=True)

        # Generate combined PDF
        create_final_pdf(png_path, destination_pdf)

    messagebox.showinfo("Done", f"Invites (PNG + PDF) saved in '{out_dir}'")

# -------------------------------------------------------
# GUI
# -------------------------------------------------------
root = tk.Tk()
root.title("Wedding Invite Stamper")
root.geometry("800x860")

def choose_file(entry):
    file = filedialog.askopenfilename()
    if file:
        entry.delete(0, tk.END)
        entry.insert(0, file)

base = os.path.abspath("")
defaults = {
    "Template PNG": os.path.join(base, "utils", "invitation.png"),
    "Guest CSV": os.path.join(base, "guest_list.csv"),
    "Name Font (.ttf)": os.path.join(base, "utils", "font.otf"),
    "Table Font (.ttf)": os.path.join(base, "utils", "font.otf"),
    "Details PDF": os.path.join(base, "utils", "details.pdf"),
}

entries = {}
for label, default in defaults.items():
    frame = tk.Frame(root)
    frame.pack(fill="x", pady=4)
    tk.Label(frame, text=label, width=18, anchor="w").pack(side="left")
    entry = tk.Entry(frame)
    entry.insert(0, default)
    entry.pack(side="left", fill="x", expand=True)
    tk.Button(frame, text="Browse", command=lambda e=entry: choose_file(e)).pack(side="right")
    entries[label] = entry

tk.Label(root, text="Name Font Size").pack()
name_size_input = tk.Entry(root)
name_size_input.insert(0, "42")
name_size_input.pack()

tk.Label(root, text="Table Font Size").pack()
table_size_input = tk.Entry(root)
table_size_input.insert(0, "23")
table_size_input.pack()

name_color = "#FFFFFF"
table_color = "#FFFFFF"

def pick_name_color():
    global name_color
    color = colorchooser.askcolor(title="Choose Name Color")[1]
    if color:
        name_color = color
        name_color_box.configure(bg=color)

def pick_table_color():
    global table_color
    color = colorchooser.askcolor(title="Choose Table Color")[1]
    if color:
        table_color = color
        table_color_box.configure(bg=color)

tk.Button(root, text="Choose Name Color", command=pick_name_color).pack()
name_color_box = tk.Label(root, text="      ", bg=name_color)
name_color_box.pack(pady=2)

tk.Button(root, text="Choose Table Color", command=pick_table_color).pack()
table_color_box = tk.Label(root, text="      ", bg=table_color)
table_color_box.pack(pady=2)

def coord_input(label, default):
    tk.Label(root, text=label).pack()
    e = tk.Entry(root)
    e.insert(0, default)
    e.pack()
    return e

table_x_input = coord_input("Table X Position", "76")
table_y_input = coord_input("Table Y Position", "42")
name_x_input = coord_input("Name X (-1 auto center)", "84")
name_y_input = coord_input("Name Y Position", "1170")

def run_script():
    generate_invites(
        entries["Template PNG"].get(),
        entries["Guest CSV"].get(),
        entries["Name Font (.ttf)"].get(),
        entries["Table Font (.ttf)"].get(),
        int(name_size_input.get()),
        int(table_size_input.get()),
        name_color,
        table_color,
        int(table_x_input.get()),
        int(table_y_input.get()),
        int(name_x_input.get()),
        int(name_y_input.get()),
        entries["Details PDF"].get()
    )

tk.Button(root, text="Generate Invitations", bg="#4CAF50", fg="white", height=2,
          command=run_script).pack(pady=20)

root.mainloop()
