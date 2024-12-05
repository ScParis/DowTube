from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size=(256, 256)):
    # Criar uma nova imagem com fundo transparente
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Desenhar um círculo vermelho (cor do YouTube)
    circle_color = (255, 0, 0, 255)  # Vermelho
    circle_bounds = (20, 20, size[0]-20, size[1]-20)
    draw.ellipse(circle_bounds, fill=circle_color)
    
    # Desenhar um triângulo branco (símbolo de play)
    triangle_color = (255, 255, 255, 255)  # Branco
    center_x, center_y = size[0] // 2, size[1] // 2
    triangle_size = size[0] // 4
    
    # Pontos do triângulo
    triangle_points = [
        (center_x - triangle_size//2, center_y - triangle_size),
        (center_x + triangle_size, center_y),
        (center_x - triangle_size//2, center_y + triangle_size)
    ]
    draw.polygon(triangle_points, fill=triangle_color)
    
    # Desenhar uma seta para baixo
    arrow_color = (255, 255, 255, 255)  # Branco
    arrow_width = size[0] // 8
    arrow_height = size[1] // 4
    arrow_top = center_y + triangle_size//2
    
    # Pontos da seta
    arrow_points = [
        (center_x - arrow_width, arrow_top),
        (center_x + arrow_width, arrow_top),
        (center_x, arrow_top + arrow_height)
    ]
    draw.polygon(arrow_points, fill=arrow_color)
    
    return image

if __name__ == "__main__":
    # Criar o diretório se não existir
    icon_dir = "debian/usr/share/icons/my-yt-down"
    if not os.path.exists(icon_dir):
        os.makedirs(icon_dir)
    
    # Criar e salvar o ícone
    icon = create_icon()
    icon.save(os.path.join(icon_dir, "my-yt-down.png"))
