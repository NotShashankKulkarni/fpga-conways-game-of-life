import os
import time
import sys
import numpy as np

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

GRID_SIZE = 32
CELL_SIZE = 20
PADDING = 30
GRID_WIDTH = GRID_SIZE * CELL_SIZE
GRID_HEIGHT = GRID_SIZE * CELL_SIZE

SIDEBAR_WIDTH = 260
WINDOW_WIDTH = GRID_WIDTH + SIDEBAR_WIDTH + (PADDING * 3)
WINDOW_HEIGHT = GRID_HEIGHT + (PADDING * 2)

STATE_PAUSED = 0
STATE_PLAYING = 1

COLOR_BG = (10, 20, 30)
COLOR_PANEL = (16, 32, 48)
COLOR_GRID = (25, 45, 65)
COLOR_CELL = (0, 191, 255)
COLOR_TEXT = (230, 245, 255)
COLOR_TEXT_MUTED = (110, 140, 170)

PRESETS = {
    "Glider": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    "Pulsar Cluster": [
        (-2, -1), (-3, -1), (-4, -1), (-2, -6), (-3, -6), (-4, -6),
        (2, -1), (3, -1), (4, -1), (2, -6), (3, -6), (4, -6),
        (-2, 1), (-3, 1), (-4, 1), (-2, 6), (-3, 6), (-4, 6),
        (2, 1), (3, 1), (4, 1), (2, 6), (3, 6), (4, 6),
        (-1, -2), (-1, -3), (-1, -4), (-6, -2), (-6, -3), (-6, -4),
        (1, -2), (1, -3), (1, -4), (6, -2), (6, -3), (6, -4),
        (-1, 2), (-1, 3), (-1, 4), (-6, 2), (-6, 3), (-6, 4),
        (1, 2), (1, 3), (1, 4), (6, 2), (6, 3), (6, 4)
    ],
    "Methuselah Box": [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)]
}

def matrix_to_hex(matrix):
    flat_vector = matrix.flatten()
    binary_str = "".join(str(int(cell)) for cell in flat_vector)
    hex_val = hex(int(binary_str, 2))[2:].zfill(256)
    return hex_val

def hex_to_matrix(hex_str):
    binary_str = bin(int(hex_str, 16))[2:].zfill(GRID_SIZE * GRID_SIZE)
    flat_vector = np.array([int(bit) for bit in binary_str])
    return flat_vector.reshape((GRID_SIZE, GRID_SIZE))

def run_pipeline_step(current_grid):
    hex_string = matrix_to_hex(current_grid)
    with open("input.txt", "w") as f:
        f.write(hex_string + "\n")
    with open("input.ready", "w") as f:
        f.write("ready")

    while not os.path.exists("output.ready"):
        time.sleep(0.001)

    with open("output.txt", "r") as f:
        next_hex_string = f.readline().strip()

    try:
        os.remove("output.ready")
    except OSError:
        pass

    return hex_to_matrix(next_hex_string)

class Button:
    def __init__(self, x, y, w, h, text, base_color, accent_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.base_color = base_color
        self.accent_color = accent_color
        self.is_hovered = False

    def draw(self, screen, font, txt_color):
        color = self.accent_color if self.is_hovered else self.base_color
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        txt_surf = font.render(self.text, True, txt_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

def main():
    if os.path.exists("input.ready"): os.remove("input.ready")
    if os.path.exists("output.ready"): os.remove("output.ready")

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Conway's Game of Life: Interactive Co-Design Engine")
    
    font_small = pygame.font.SysFont("Arial", 12, bold=False)
    font_med = pygame.font.SysFont("Arial", 14, bold=True)
    font_large = pygame.font.SysFont("Arial", 16, bold=True)
    clock = pygame.time.Clock()

    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    sim_state = STATE_PAUSED
    generation = 0
    active_placement_preset = None

    sidebar_x = GRID_WIDTH + (PADDING * 2) + 10
    element_w = SIDEBAR_WIDTH - 20
    
    y_status    = PADDING + 10
    y_controls  = y_status + 55
    y_presets   = y_controls + 155
    y_footer    = y_presets + 200

    btn_play = Button(sidebar_x, y_controls, element_w, 36, "PLAY SIMULATION", (38, 166, 91), (46, 204, 113))
    btn_pause = Button(sidebar_x, y_controls + 44, element_w, 36, "PAUSE ENGINE", (190, 40, 40), (210, 50, 50))
    btn_clear = Button(sidebar_x, y_controls + 88, element_w, 36, "CLEAR SYSTEM DATA", (70, 80, 95), (90, 105, 120))
    
    preset_buttons = []
    curr_y = y_presets + 30
    for name in PRESETS.keys():
        preset_buttons.append((name, Button(sidebar_x, curr_y, element_w, 32, f"+ Load {name}", (44, 62, 80), (52, 73, 94))))
        curr_y += 40

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        btn_play.check_hover(mouse_pos)
        btn_pause.check_hover(mouse_pos)
        btn_clear.check_hover(mouse_pos)
        for _, btn in preset_buttons:
            btn.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if btn_play.rect.collidepoint(mouse_pos):
                        sim_state = STATE_PLAYING
                        active_placement_preset = None
                    elif btn_pause.rect.collidepoint(mouse_pos):
                        sim_state = STATE_PAUSED
                    elif btn_clear.rect.collidepoint(mouse_pos):
                        grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
                        generation = 0
                        sim_state = STATE_PAUSED
                        active_placement_preset = None

                    for name, btn in preset_buttons:
                        if btn.rect.collidepoint(mouse_pos):
                            active_placement_preset = name

                    grid_rect = pygame.Rect(PADDING, PADDING, GRID_WIDTH, GRID_HEIGHT)
                    if grid_rect.collidepoint(mouse_pos):
                        c = (mouse_pos[0] - PADDING) // CELL_SIZE
                        r = (mouse_pos[1] - PADDING) // CELL_SIZE
                        
                        if active_placement_preset:
                            for dr, dc in PRESETS[active_placement_preset]:
                                target_r = (r + dr) % GRID_SIZE
                                target_col = (c + dc) % GRID_SIZE
                                grid[target_r, target_col] = 1
                            if not pygame.key.get_mods() & pygame.KMOD_SHIFT:
                                active_placement_preset = None 
                        else:
                            grid[r, c] = 1
                elif event.button == 3:
                    active_placement_preset = None

        mouse_buttons = pygame.mouse.get_pressed()
        grid_rect = pygame.Rect(PADDING, PADDING, GRID_WIDTH, GRID_HEIGHT)
        if grid_rect.collidepoint(mouse_pos) and not active_placement_preset and sim_state == STATE_PAUSED:
            c = (mouse_pos[0] - PADDING) // CELL_SIZE
            r = (mouse_pos[1] - PADDING) // CELL_SIZE
            if mouse_buttons[0]: grid[r, c] = 1
            elif mouse_buttons[2]: grid[r, c] = 0

        if sim_state == STATE_PLAYING:
            grid = run_pipeline_step(grid)
            generation += 1

        screen.fill(COLOR_BG)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(PADDING + c * CELL_SIZE, PADDING + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if grid[r, c] == 1:
                    pygame.draw.rect(screen, COLOR_CELL, rect)
                else:
                    pygame.draw.rect(screen, COLOR_GRID, rect, 1)

        if active_placement_preset and grid_rect.collidepoint(mouse_pos):
            c = (mouse_pos[0] - PADDING) // CELL_SIZE
            r = (mouse_pos[1] - PADDING) // CELL_SIZE
            ghost_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            ghost_surf.fill((*COLOR_CELL, 90))
            for dr, dc in PRESETS[active_placement_preset]:
                target_r = (r + dr) % GRID_SIZE
                target_col = (c + dc) % GRID_SIZE
                screen.blit(ghost_surf, (PADDING + target_col * CELL_SIZE, PADDING + target_r * CELL_SIZE))

        panel_rect = pygame.Rect(sidebar_x - 15, PADDING, SIDEBAR_WIDTH, GRID_HEIGHT)
        pygame.draw.rect(screen, COLOR_PANEL, panel_rect, border_radius=10)

        status_text = "COMPUTING" if sim_state == STATE_PLAYING else "HALTED"
        status_color = (46, 204, 113) if sim_state == STATE_PLAYING else (231, 76, 60)
        
        lbl_status_lbl = font_large.render("SYSTEM ENG:", True, COLOR_TEXT_MUTED)
        lbl_status     = font_large.render(status_text, True, status_color)
        lbl_gen        = font_med.render(f"Hardware Tick: {generation}", True, COLOR_TEXT)
        
        screen.blit(lbl_status_lbl, (sidebar_x, y_status))
        screen.blit(lbl_status, (sidebar_x + 110, y_status))
        screen.blit(lbl_gen, (sidebar_x, y_status + 24))

        pygame.draw.line(screen, COLOR_GRID, (sidebar_x, y_controls - 12), (sidebar_x + element_w, y_controls - 12), 1)

        btn_play.draw(screen, font_med, COLOR_TEXT)
        btn_pause.draw(screen, font_med, COLOR_TEXT)
        btn_clear.draw(screen, font_med, COLOR_TEXT)

        pygame.draw.line(screen, COLOR_GRID, (sidebar_x, y_presets - 12), (sidebar_x + element_w, y_presets - 12), 1)

        lbl_shapes = font_large.render("HARDWARE BLUEPRINTS", True, COLOR_TEXT_MUTED)
        screen.blit(lbl_shapes, (sidebar_x, y_presets))
        for _, btn in preset_buttons:
            btn.draw(screen, font_med, COLOR_TEXT)

        pygame.draw.line(screen, COLOR_GRID, (sidebar_x, y_footer - 12), (sidebar_x + element_w, y_footer - 12), 1)

        lbl_h1 = font_small.render("• Mouse Drag: Canvas Draw / Erase", True, COLOR_TEXT_MUTED)
        lbl_h2 = font_small.render("• Blueprint Selection: Stamp to Grid", True, COLOR_TEXT_MUTED)
        lbl_h3 = font_small.render("• Right-Click Canvas: Drop blueprint", True, COLOR_TEXT_MUTED)
        screen.blit(lbl_h1, (sidebar_x, y_footer))
        screen.blit(lbl_h2, (sidebar_x, y_footer + 16))
        screen.blit(lbl_h3, (sidebar_x, y_footer + 32))

        pygame.display.flip()
        clock.tick(15)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
