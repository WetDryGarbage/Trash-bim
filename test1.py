import pygame
import sys
import time
import random

# 1. 初始化
pygame.init()
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭 - 我的作业版")
clock = pygame.time.Clock()

# 字体
font_large = pygame.font.SysFont("simhei", 40)
font_medium = pygame.font.SysFont("simhei", 28)

# ================= 核心：自动生成绝对有解的关卡 =================
def generate_solvable_level(num_arrows):
    """
    生成一个保证有解的关卡。
    核心思路：从外向内填充，先放外围（朝外的方向不会被挡），再放内圈。
    """
    board = [[0] * 4 for _ in range(4)]
    arrows = []

    # 1. 划分外围格子和内圈格子
    outer_cells = []
    inner_cells = []
    for r in range(4):
        for c in range(4):
            if r == 0 or r == 3 or c == 0 or c == 3:
                outer_cells.append((r, c))
            else:
                inner_cells.append((r, c))

    # 2. 打乱顺序，先放外围，再放内圈
    random.shuffle(outer_cells)
    random.shuffle(inner_cells)
    all_cells = outer_cells + inner_cells

    # 3. 依次放置箭头
    for (r, c) in all_cells:
        if len(arrows) >= num_arrows:
            break
        # 随机选一个方向
        d = random.choice([1, 2, 3, 4])
        # 对于内圈箭头，检查它的正前方（到边界方向）有没有阻挡
        # 如果发现该方向会被外圈挡住，就换个方向
        has_block = False
        if d == 1:  # 上
            for rr in range(r - 1, -1, -1):
                if board[rr][c] != 0: has_block = True; break
        elif d == 2:  # 下
            for rr in range(r + 1, 4):
                if board[rr][c] != 0: has_block = True; break
        elif d == 3:  # 左
            for cc in range(c - 1, -1, -1):
                if board[r][cc] != 0: has_block = True; break
        elif d == 4:  # 右
            for cc in range(c + 1, 4):
                if board[r][cc] != 0: has_block = True; break

        if not has_block:
            board[r][c] = d
            arrows.append((r, c, d))

    return board


# ================= 游戏数据（7个关卡） =================
LEVELS = [
    # 第1关（4个箭头，入门）
    [[0, 4, 0, 0],
     [0, 0, 1, 0],
     [0, 0, 0, 0],
     [0, 0, 3, 0]],

    # 第2关（4个箭头，学习顺序）
    [[0, 4, 0, 0],
     [1, 0, 0, 2],
     [0, 0, 0, 0],
     [0, 3, 0, 0]],

    # 第3关（6个箭头，初识交织）
    [[4, 0, 1, 0],
     [0, 2, 0, 3],
     [0, 0, 4, 0],
     [3, 0, 0, 4]],

    # 第4关（6个箭头，自动生成，保证有解）
    generate_solvable_level(6),

    # 第5关（7个箭头，自动生成，保证有解）
    generate_solvable_level(7),

    # 第6关（9个箭头，自动生成，保证有解）
    generate_solvable_level(9),

    # 第7关（11个箭头，自动生成，保证有解）
    generate_solvable_level(11),
]

INITIAL_LEVELS = [[row[:] for row in level] for level in LEVELS]

# 游戏状态变量
game_state = "START"   # START, PLAYING, WIN, LOSE
current_level_idx = 0
mistakes = 0
MAX_MISTAKES = 3

# 计时变量
start_time = 0
elapsed_time = 0
final_time = 0

# 尺寸与坐标
CELL_SIZE = 80
GRID_OFFSET_X = (WIDTH - CELL_SIZE * 4) // 2
GRID_OFFSET_Y = 200

# 按钮区域
RESTART_BTN_RECT = pygame.Rect(WIDTH - 180, 60, 140, 50)
START_BTN_RECT = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)

# 碰撞动画变量
collision_anim_timer = 0
collision_anim_pos = (0, 0)


# ================= 核心逻辑函数 =================
def check_collision(board, row, col, direction):
    """检查箭头前方是否有阻挡"""
    if direction == 1:  # 上
        for r in range(row - 1, -1, -1):
            if board[r][col] != 0: return True
    elif direction == 2:  # 下
        for r in range(row + 1, 4):
            if board[r][col] != 0: return True
    elif direction == 3:  # 左
        for c in range(col - 1, -1, -1):
            if board[row][c] != 0: return True
    elif direction == 4:  # 右
        for c in range(col + 1, 4):
            if board[row][c] != 0: return True
    return False


def get_rating(seconds):
    """根据用时评定等级"""
    if seconds <= 120:
        return "S"
    elif seconds <= 240:
        return "A"
    elif seconds <= 360:
        return "B"
    else:
        return "C"


def reset_level():
    """重置当前关卡"""
    global mistakes, game_state, collision_anim_timer
    mistakes = 0
    game_state = "PLAYING"
    collision_anim_timer = 0
    LEVELS[current_level_idx] = [row[:] for row in INITIAL_LEVELS[current_level_idx]]
    print("✅ 当前关卡已重置！")


def reset_game():
    """重置整个游戏并重新计时"""
    global current_level_idx, mistakes, game_state, start_time, elapsed_time
    current_level_idx = 0
    mistakes = 0
    game_state = "PLAYING"
    start_time = time.time()  # 记录开始时间
    elapsed_time = 0
    for i in range(len(LEVELS)):
        LEVELS[i] = [row[:] for row in INITIAL_LEVELS[i]]
    print("🎮 游戏开始！")


# ================= 主循环 =================
running = True
while running:
    # 实时更新计时器（仅在游玩状态时）
    if game_state == "PLAYING":
        elapsed_time = int(time.time() - start_time)

    # 1. 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # 开始界面：点击开始按钮
            if game_state == "START":
                if START_BTN_RECT.collidepoint(mouse_x, mouse_y):
                    reset_game()
                continue

            # 游戏中：优先检测“重新开始”按钮
            if RESTART_BTN_RECT.collidepoint(mouse_x, mouse_y):
                reset_level()
                continue

            # 通关状态：点击进入下一关或重新开始
            if game_state == "WIN":
                if current_level_idx < len(LEVELS) - 1:
                    current_level_idx += 1
                    reset_level()
                else:
                    reset_game()
                continue

            # 游戏中：点击棋盘
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
                                if current_level_idx == len(LEVELS) - 1:
                                    final_time = elapsed_time  # 最后一关通关，冻结时间
                                game_state = "WIN"

    # 2. 动画逻辑
    if collision_anim_timer > 0:
        collision_anim_timer -= 1

    # 3. 绘制背景
    screen.fill((30, 30, 40))

    # 4. 分状态绘制
    if game_state == "START":
        # ---- 开始界面 ----
        title_text = font_large.render("一箭又一箭", True, (0, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(title_text, title_rect)

        pygame.draw.rect(screen, (50, 200, 50), START_BTN_RECT, border_radius=10)
        start_text = font_large.render("开始游戏", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=START_BTN_RECT.center)
        screen.blit(start_text, start_rect)

    else:
        # ---- 游戏界面 ----
        remaining = sum(1 for row_data in LEVELS[current_level_idx] for x in row_data if x != 0)

        # 显示关卡进度、剩余箭头、失误次数
        text_level = font_medium.render(f"关卡: {current_level_idx + 1} / {len(LEVELS)}", True, (255, 255, 255))
        screen.blit(text_level, (50, 50))
        text_remain = font_medium.render(f"剩余: {remaining}", True, (0, 255, 255))
        screen.blit(text_remain, (50, 100))
        text_mistake = font_medium.render(f"失误: {mistakes} / {MAX_MISTAKES}", True, (255, 100, 100))
        screen.blit(text_mistake, (50, 150))

        # 显示计时器
        display_time = elapsed_time if game_state == "PLAYING" else final_time
        mins = display_time // 60
        secs = display_time % 60
        time_str = f"{mins:02d}:{secs:02d}"
        text_time = font_medium.render(f"用时: {time_str}", True, (255, 255, 0))
        screen.blit(text_time, (WIDTH - 180, 120))

        # 绘制“重新开始”按钮
        pygame.draw.rect(screen, (200, 50, 50), RESTART_BTN_RECT, border_radius=10)
        text_restart = font_medium.render("重新开始", True, (255, 255, 255))
        text_rect = text_restart.get_rect(center=RESTART_BTN_RECT.center)
        screen.blit(text_restart, text_rect)

        # 绘制棋盘与箭头
        current_board = LEVELS[current_level_idx]
        for row in range(4):
            for col in range(4):
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE

                # 处理碰撞抖动
                draw_x, draw_y = x, y
                if collision_anim_timer > 0 and collision_anim_pos == (row, col):
                    offset = 8 if collision_anim_timer % 2 == 0 else -8
                    draw_x += offset

                # 画格子边框
                pygame.draw.rect(screen, (100, 100, 100), (draw_x, draw_y, CELL_SIZE, CELL_SIZE), 2)

                # 画箭头
                arrow_type = current_board[row][col]
                if arrow_type != 0:
                    center_x = draw_x + CELL_SIZE // 2
                    center_y = draw_y + CELL_SIZE // 2

                    # 默认颜色
                    color = (255, 255, 0)
                    # 碰撞时变红
                    if collision_anim_timer > 0 and collision_anim_pos == (row, col):
                        color = (255, 50, 50)
                    else:
                        if arrow_type == 1: color = (0, 255, 255)
                        elif arrow_type == 2: color = (255, 100, 100)
                        elif arrow_type == 3: color = (100, 255, 100)
                        elif arrow_type == 4: color = (255, 255, 0)

                    # 根据方向绘制三角形
                    if arrow_type == 1:  # 上
                        points = [(center_x, center_y - 20), (center_x - 15, center_y + 15), (center_x + 15, center_y + 15)]
                    elif arrow_type == 2:  # 下
                        points = [(center_x, center_y + 20), (center_x - 15, center_y - 15), (center_x + 15, center_y - 15)]
                    elif arrow_type == 3:  # 左
                        points = [(center_x - 20, center_y), (center_x + 15, center_y - 15), (center_x + 15, center_y + 15)]
                    elif arrow_type == 4:  # 右
                        points = [(center_x + 20, center_y), (center_x - 15, center_y - 15), (center_x - 15, center_y + 15)]

                    pygame.draw.polygon(screen, color, points)

        # ---- 胜利 / 失败遮罩 ----
        if game_state == "WIN":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            if current_level_idx < len(LEVELS) - 1:
                text_win = font_large.render("通关！点击进入下一关", True, (0, 255, 0))
                text_rect = text_win.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
                screen.blit(text_win, text_rect)
            else:
                # 全部通关
                text_win = font_large.render("全部通关！", True, (0, 255, 0))
                text_win_rect = text_win.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
                screen.blit(text_win, text_win_rect)

                # 显示总用时
                final_mins = final_time // 60
                final_secs = final_time % 60
                final_time_str = f"{final_mins:02d}:{final_secs:02d}"
                text_final_time = font_medium.render(f"总用时: {final_time_str}", True, (255, 255, 0))
                text_time_rect = text_final_time.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
                screen.blit(text_final_time, text_time_rect)

                # 显示评级
                rating = get_rating(final_time)
                rating_colors = {"S": (255, 215, 0), "A": (0, 255, 0), "B": (0, 255, 255), "C": (200, 200, 200)}
                rating_color = rating_colors.get(rating, (200, 200, 200))
                text_rating = font_medium.render(f"评级: {rating} 级", True, rating_color)
                text_rating_rect = text_rating.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
                screen.blit(text_rating, text_rating_rect)

                # 重新开始提示
                text_replay = font_medium.render("点击屏幕重新开始", True, (200, 200, 200))
                text_replay_rect = text_replay.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
                screen.blit(text_replay, text_replay_rect)

        elif game_state == "LOSE":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            text_lose = font_large.render("失败！点击右上方重开", True, (255, 0, 0))
            text_rect = text_lose.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text_lose, text_rect)

    # 5. 刷新屏幕
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()