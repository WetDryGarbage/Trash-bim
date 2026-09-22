import pygame
import sys
import time  # 【新增】导入时间模块

# 1. 初始化
pygame.init()
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭 - 我的作业版")
clock = pygame.time.Clock()

# 字体
font_large = pygame.font.SysFont("simhei", 40)
font_medium = pygame.font.SysFont("simhei", 28)

# ================= 游戏数据 =================
LEVELS = [
    [[0, 4, 0, 0],
     [0, 0, 1, 0],
     [0, 0, 0, 0],
     [0, 0, 3, 0]],
    [[0, 4, 0, 0],
     [1, 0, 0, 2],
     [0, 0, 0, 0],
     [0, 3, 0, 0]],
    [[4, 0, 1, 0],
     [0, 2, 0, 3],
     [0, 0, 4, 0],
     [3, 0, 0, 4]]
]

INITIAL_LEVELS = [[row[:] for row in level] for level in LEVELS]

game_state = "START"
current_level_idx = 0
mistakes = 0
MAX_MISTAKES = 3

# 【新增】计时相关的变量
start_time = 0  # 游戏开始的时间戳
elapsed_time = 0  # 已经过去的时间（秒）
final_time = 0  # 通关后的最终时间

CELL_SIZE = 80
GRID_OFFSET_X = (WIDTH - CELL_SIZE * 4) // 2
GRID_OFFSET_Y = 200

RESTART_BTN_RECT = pygame.Rect(WIDTH - 180, 60, 140, 50)
START_BTN_RECT = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)

collision_anim_timer = 0
collision_anim_pos = (0, 0)


# ================= 函数 =================
def check_collision(board, row, col, direction):
    if direction == 1:
        for r in range(row - 1, -1, -1):
            if board[r][col] != 0: return True
    elif direction == 2:
        for r in range(row + 1, 4):
            if board[r][col] != 0: return True
    elif direction == 3:
        for c in range(col - 1, -1, -1):
            if board[row][c] != 0: return True
    elif direction == 4:
        for c in range(col + 1, 4):
            if board[row][c] != 0: return True
    return False


def reset_level():
    global mistakes, game_state, collision_anim_timer
    mistakes = 0
    game_state = "PLAYING"
    collision_anim_timer = 0
    LEVELS[current_level_idx] = [row[:] for row in INITIAL_LEVELS[current_level_idx]]
    print("✅ 关卡已重置！")


def reset_game():
    global current_level_idx, mistakes, game_state, start_time, elapsed_time
    current_level_idx = 0
    mistakes = 0
    game_state = "PLAYING"
    # 【新增】开始游戏时，记录开始时间
    start_time = time.time()
    elapsed_time = 0
    for i in range(len(LEVELS)):
        LEVELS[i] = [row[:] for row in INITIAL_LEVELS[i]]


# ================= 主循环 =================
running = True
while running:
    # 【新增】实时计算流逝的时间（仅当在游玩状态时计时）
    if game_state == "PLAYING":
        elapsed_time = int(time.time() - start_time)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            if game_state == "START":
                if START_BTN_RECT.collidepoint(mouse_x, mouse_y):
                    reset_game()
                continue

            if RESTART_BTN_RECT.collidepoint(mouse_x, mouse_y):
                reset_level()
                continue

            if game_state == "WIN":
                # 【修改】如果是最后一关通关了，再点击就重置游戏并重新计时
                if current_level_idx < len(LEVELS) - 1:
                    current_level_idx += 1
                    reset_level()
                else:
                    # 通关全部后，点击重置并重新开始计时
                    reset_game()
                continue

            if game_state == "PLAYING":
                col = (mouse_x - GRID_OFFSET_X) // CELL_SIZE
                row = (mouse_y - GRID_OFFSET_Y) // CELL_SIZE

                if 0 <= row < 4 and 0 <= col < 4:
                    arrow_type = LEVELS[current_level_idx][row][col]
                    if arrow_type != 0:
                        if check_collision(LEVELS[current_level_idx], row, col, arrow_type):
                            mistakes += 1
                            collision_anim_timer = 15
                            collision_anim_pos = (row, col)
                            if mistakes >= MAX_MISTAKES:
                                game_state = "LOSE"
                        else:
                            LEVELS[current_level_idx][row][col] = 0
                            remaining = sum(1 for row_data in LEVELS[current_level_idx] for x in row_data if x != 0)
                            if remaining == 0:
                                # 【新增】如果是最后一关通关了，冻结时间
                                if current_level_idx == len(LEVELS) - 1:
                                    final_time = elapsed_time
                                game_state = "WIN"

    # 2. 动画逻辑
    if collision_anim_timer > 0:
        collision_anim_timer -= 1

    # 3. 绘制背景
    screen.fill((30, 30, 40))

    # 4. 根据状态绘制不同界面
    if game_state == "START":
        title_text = font_large.render("一箭又一箭", True, (0, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(title_text, title_rect)

        pygame.draw.rect(screen, (50, 200, 50), START_BTN_RECT, border_radius=10)
        start_text = font_large.render("开始游戏", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=START_BTN_RECT.center)
        screen.blit(start_text, start_rect)

    else:
        # UI 文字
        remaining = sum(1 for row_data in LEVELS[current_level_idx] for x in row_data if x != 0)

        text_level = font_medium.render(f"关卡: {current_level_idx + 1}", True, (255, 255, 255))
        screen.blit(text_level, (50, 50))

        text_remain = font_medium.render(f"剩余: {remaining}", True, (0, 255, 255))
        screen.blit(text_remain, (50, 100))

        text_mistake = font_medium.render(f"失误: {mistakes} / {MAX_MISTAKES}", True, (255, 100, 100))
        screen.blit(text_mistake, (50, 150))

        # 【新增】绘制计时器（在重开按钮的正下方，或者右上角）
        # 如果正在游玩，显示实时时间；如果通关了，显示通关时间
        display_time = elapsed_time if game_state == "PLAYING" else final_time
        # 将秒转换为 mm:ss 格式
        mins = display_time // 60
        secs = display_time % 60
        time_str = f"{mins:02d}:{secs:02d}"
        text_time = font_medium.render(f"用时: {time_str}", True, (255, 255, 0))  # 黄色醒目
        # 放在“重新开始”按钮下方对齐
        screen.blit(text_time, (WIDTH - 180, 120))

        # 重开按钮
        pygame.draw.rect(screen, (200, 50, 50), RESTART_BTN_RECT, border_radius=10)
        text_restart = font_medium.render("重新开始", True, (255, 255, 255))
        text_rect = text_restart.get_rect(center=RESTART_BTN_RECT.center)
        screen.blit(text_restart, text_rect)

        # 绘制棋盘
        current_board = LEVELS[current_level_idx]
        for row in range(4):
            for col in range(4):
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE

                draw_x, draw_y = x, y
                if collision_anim_timer > 0 and collision_anim_pos == (row, col):
                    offset = 8 if collision_anim_timer % 2 == 0 else -8
                    draw_x += offset

                pygame.draw.rect(screen, (100, 100, 100), (draw_x, draw_y, CELL_SIZE, CELL_SIZE), 2)

                arrow_type = current_board[row][col]
                if arrow_type != 0:
                    center_x = draw_x + CELL_SIZE // 2
                    center_y = draw_y + CELL_SIZE // 2

                    color = (255, 255, 0)
                    if collision_anim_timer > 0 and collision_anim_pos == (row, col):
                        color = (255, 50, 50)
                    else:
                        if arrow_type == 1:
                            color = (0, 255, 255)
                        elif arrow_type == 2:
                            color = (255, 100, 100)
                        elif arrow_type == 3:
                            color = (100, 255, 100)
                        elif arrow_type == 4:
                            color = (255, 255, 0)

                    if arrow_type == 1:
                        points = [(center_x, center_y - 20), (center_x - 15, center_y + 15),
                                  (center_x + 15, center_y + 15)]
                    elif arrow_type == 2:
                        points = [(center_x, center_y + 20), (center_x - 15, center_y - 15),
                                  (center_x + 15, center_y - 15)]
                    elif arrow_type == 3:
                        points = [(center_x - 20, center_y), (center_x + 15, center_y - 15),
                                  (center_x + 15, center_y + 15)]
                    elif arrow_type == 4:
                        points = [(center_x + 20, center_y), (center_x - 15, center_y - 15),
                                  (center_x - 15, center_y + 15)]

                    pygame.draw.polygon(screen, color, points)

        # 胜利/失败遮罩
        if game_state == "WIN":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            # 【修改】如果是最后一关，显示完整通关时间和祝贺语
            if current_level_idx < len(LEVELS) - 1:
                text_win = font_large.render("通关！点击进入下一关", True, (0, 255, 0))
                text_rect = text_win.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
                screen.blit(text_win, text_rect)
            else:
                # 全部通关
                text_win = font_large.render("全部通关！", True, (0, 255, 0))
                text_win_rect = text_win.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
                screen.blit(text_win, text_win_rect)

                # 显示最终用时
                final_mins = final_time // 60
                final_secs = final_time % 60
                final_time_str = f"{final_mins:02d}:{final_secs:02d}"
                text_final_time = font_medium.render(f"总用时: {final_time_str}", True, (255, 255, 0))
                text_time_rect = text_final_time.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
                screen.blit(text_final_time, text_time_rect)

                text_replay = font_medium.render("点击屏幕重新开始", True, (200, 200, 200))
                text_replay_rect = text_replay.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
                screen.blit(text_replay, text_replay_rect)

        elif game_state == "LOSE":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            text_lose = font_large.render("失败！点击右上方重开", True, (255, 0, 0))
            text_rect = text_lose.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text_lose, text_rect)

    # 5. 刷新
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()