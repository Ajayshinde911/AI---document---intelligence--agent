from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import random

# Directories
os.makedirs("dataset/printed", exist_ok=True)
os.makedirs("dataset/handwritten", exist_ok=True)

# Fonts
try:
    printed_font = ImageFont.truetype("arial.ttf", 20)
    handwriting_font = ImageFont.truetype("seguisym.ttf", 22)  # cursive style
except:
    printed_font = ImageFont.load_default()
    handwriting_font = ImageFont.load_default()

# Function to add light noise
def add_noise(img):
    draw = ImageDraw.Draw(img)
    width, height = img.size
    for _ in range(200):  # 200 random dots
        x, y = random.randint(0, width-1), random.randint(0, height-1)
        draw.point((x, y), fill=(random.randint(200,255), random.randint(200,255), random.randint(200,255)))
    return img

# -----------------------------
# Create 6 printed invoice images
# -----------------------------
for i in range(1, 7):
    img = Image.new('RGB', (500, 300), color='white')
    draw = ImageDraw.Draw(img)

    # Draw table lines (simulate invoice)
    draw.line((50, 60, 450, 60), fill="black", width=2)
    draw.line((50, 100, 450, 100), fill="black", width=1)
    draw.line((50, 140, 450, 140), fill="black", width=1)
    draw.rectangle((50, 50, 450, 250), outline="black", width=2)

    # Add invoice text
    draw.text((60, 10), f"Invoice #{i}", font=printed_font, fill="black")
    draw.text((60, 70), f"Customer: John Doe {i}", font=printed_font, fill="black")
    draw.text((60, 110), f"Item: Product {i}", font=printed_font, fill="black")
    draw.text((60, 150), f"Amount: ${random.randint(50, 500)}", font=printed_font, fill="black")
    draw.text((60, 190), f"Date: 2025-08-{random.randint(10,28)}", font=printed_font, fill="black")

    # Slight rotation
    img = img.rotate(random.uniform(-2, 2), expand=True, fillcolor='white')

    # Add light noise
    img = add_noise(img)

    filename = f"dataset/printed/midd_0{i}.jpg"
    img.save(filename)
    print(f"Created {filename}")

# -----------------------------
# Create 6 handwritten prescription images
# -----------------------------
medications = ["Paracetamol", "Ibuprofen", "Amoxicillin", "Cetirizine", "Metformin"]

for i in range(1, 7):
    img = Image.new('RGB', (500, 300), color='white')
    draw = ImageDraw.Draw(img)

    y = 20
    # Random offsets for more natural handwriting
    draw.text((random.randint(5,25), y), f"Rx #{i}", font=handwriting_font, fill="black")
    y += random.randint(30,50)
    draw.text((random.randint(5,25), y), f"Patient: Jane Smith", font=handwriting_font, fill="black")
    y += random.randint(30,50)
    draw.text((random.randint(5,25), y), f"Medication: {random.choice(medications)}", font=handwriting_font, fill="black")
    y += random.randint(30,50)
    draw.text((random.randint(5,25), y), f"Dosage: {random.randint(1,2)} tablet(s) {random.randint(1,3)} times/day", font=handwriting_font, fill="black")
    y += random.randint(30,50)
    draw.text((random.randint(5,25), y), f"Duration: {random.randint(3,10)} days", font=handwriting_font, fill="black")

    # Slight rotation
    img = img.rotate(random.uniform(-3, 3), expand=True, fillcolor='white')

    # Add light noise
    img = add_noise(img)

    filename = f"dataset/handwritten/rx_0{i}.jpg"
    img.save(filename)
    print(f"Created {filename}")

print("\nAll complex sample images with noise and rotation created successfully!")
