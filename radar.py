import serial
import pygame
import math
import sys


SERIAL_PORT = "/dev/tty.usbmodem1101"
BAUD_RATE = 9600

WIDTH = 1200
HEIGHT = 700

MAX_DISTANCE = 350   # 👈 rango visual inicial (máx permitido)
MAX_SENSOR_DISTANCE = 400  # 👈 límite físico del sensor

# ---------- INIT ----------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Radar Arduino - Python")

font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 18)

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

angle = 90
distance = 0
servo_active = True
buffer = ""

origin = (WIDTH // 2, HEIGHT - 80)
radar_radius = 500

# ---------- SERIAL ----------
def send_command(cmd):
    global servo_active
    ser.write(cmd.encode())

    if cmd == "S":
        servo_active = False
    elif cmd == "R":
        servo_active = True


def parse_serial():
    global buffer, angle, distance

    while ser.in_waiting:
        char = ser.read().decode(errors="ignore")

        if char == ".":
            try:
                parts = buffer.split(",")
                if len(parts) == 2:
                    a = int(parts[0])
                    d = int(parts[1])

                    # Filtrado de valores inválidos
                    if 0 <= a <= 180:
                        angle = a

                    if 0 <= d <= MAX_SENSOR_DISTANCE:
                        distance = d

            except ValueError:
                pass

            buffer = ""
        else:
            buffer += char


# ---------- DRAW ----------
def draw_radar():
    screen.fill((0, 0, 0))

    # Arcos
    for r in [125, 250, 375, 500]:
        pygame.draw.arc(
            screen,
            (0, 180, 0),
            (origin[0] - r, origin[1] - r, r * 2, r * 2),
            math.radians(0),
            math.radians(180),
            2,
        )

    # Líneas de ángulo
    for a in range(0, 181, 30):
        x = origin[0] + radar_radius * math.cos(math.radians(180 - a))
        y = origin[1] - radar_radius * math.sin(math.radians(180 - a))
        pygame.draw.line(screen, (0, 120, 0), origin, (x, y), 2)

    # Línea del servo
    x = origin[0] + radar_radius * math.cos(math.radians(180 - angle))
    y = origin[1] - radar_radius * math.sin(math.radians(180 - angle))
    pygame.draw.line(screen, (0, 255, 0), origin, (x, y), 3)

    # ---------- DETECCIÓN ----------
    if 0 < distance <= MAX_DISTANCE:
        scaled_distance = (distance / MAX_DISTANCE) * radar_radius

        obj_x = origin[0] + scaled_distance * math.cos(math.radians(180 - angle))
        obj_y = origin[1] - scaled_distance * math.sin(math.radians(180 - angle))

        pygame.draw.circle(screen, (255, 0, 0), (int(obj_x), int(obj_y)), 10)

    # ---------- TEXTOS ----------
    status = "ACTIVO" if servo_active else "PARADO"
    status_color = (0, 255, 0) if servo_active else (255, 120, 0)

    screen.blit(font.render(f"Ángulo: {angle}°", True, (0, 255, 0)), (30, 30))
    screen.blit(font.render(f"Distancia: {distance} cm", True, (0, 255, 0)), (30, 65))
    screen.blit(font.render(f"Rango: {MAX_DISTANCE} cm", True, (0, 255, 0)), (30, 100))
    screen.blit(font.render(f"Servo: {status}", True, status_color), (30, 135))

    # Controles
    screen.blit(small_font.render("S = parar servo", True, (200, 200, 200)), (30, HEIGHT - 110))
    screen.blit(small_font.render("R = reanudar servo", True, (200, 200, 200)), (30, HEIGHT - 85))
    screen.blit(small_font.render("+ / - = cambiar rango", True, (200, 200, 200)), (30, HEIGHT - 60))
    screen.blit(small_font.render("ESC = salir", True, (200, 200, 200)), (30, HEIGHT - 35))

    pygame.display.flip()


# ---------- MAIN ----------
def main():
    global MAX_DISTANCE

    clock = pygame.time.Clock()

    while True:
        parse_serial()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ser.close()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    send_command("S")

                elif event.key == pygame.K_r:
                    send_command("R")

                elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                    MAX_DISTANCE = min(350, MAX_DISTANCE + 10)

                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    MAX_DISTANCE = max(10, MAX_DISTANCE - 10)

                elif event.key == pygame.K_ESCAPE:
                    ser.close()
                    pygame.quit()
                    sys.exit()

        draw_radar()
        clock.tick(30)


if __name__ == "__main__":
    main()