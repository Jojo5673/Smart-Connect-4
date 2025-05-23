if __name__ == '__main__':
    import pygame, sys, time
    import settings
    from concurrent.futures import ThreadPoolExecutor

    from ai import AI
    from board import Board
    import utility


    pygame.init()
    pygame.display.set_caption("Connect 4")
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((settings.SCREEN_DIMS))
    game_active = False
    fps_ticks = 0
    curr_fps = 0
    active_pos = {
        1: (settings.SCREEN_DIMS[0]//4, screen.get_rect().top + settings.HEIGHT_DIV // 2),
        2: (3 * settings.SCREEN_DIMS[0]//4, screen.get_rect().top + settings.HEIGHT_DIV // 2)
    }
    columns = []
    hole_colors = []
    PLAYER = settings.PLAYER
    BOT = settings.BOT

    players_rect = pygame.Rect(screen.get_rect().left, screen.get_rect().top, screen.get_rect().width, 1 * settings.HEIGHT_DIV)
    bot = utility.circle_crop_image(pygame.image.load(utility.resource_path("assets/robot.png")).convert_alpha())
    person = utility.circle_crop_image(pygame.image.load(utility.resource_path("assets/you.png")).convert_alpha())
    gb = Board()
    ai = AI(gb)
    working_depth = None
    executor = ThreadPoolExecutor(max_workers=2)
    future = None

    def draw_button(msg, left=None, right=None, x_center=None):
        font = pygame.font.SysFont(None, 48)
        msg_image = font.render(msg, True, settings.TEXT_COLOR, settings.BTN_COLOR)
        msg_rect = msg_image.get_rect()

        width, height = msg_rect.width + settings.BTN_PADDING[0], msg_rect.height + settings.BTN_PADDING[1]
        color = settings.BTN_COLOR
        rect = pygame.Rect(0,0,width, height)
        rect.centery = screen.get_rect().bottom - settings.HEIGHT_DIV // 2
        if left is not None:
            rect.left = left
        elif right is not None:
            rect.right = right
        elif x_center is not None:
            rect.centerx = x_center
        else:
            rect.centerx = screen.get_rect().centerx

        msg_rect.center = rect.center
        screen.fill(color, rect)
        screen.blit(msg_image, msg_rect)
        return rect

    play_button = draw_button("")
    rematch_button = draw_button("")
    new_bot_button = draw_button("")
    bot_choices = []

    def check_buttons(mouse_x, mouse_y):
        global working_depth
        global game_active, gb, hole_colors
        if not game_active and play_button.collidepoint(mouse_x, mouse_y):
            game_active = True
            gb = Board()
            ai.depth = working_depth
            hole_colors = []
            draw_screen()
        elif gb.game_over and rematch_button.collidepoint(mouse_x, mouse_y):
            gb = Board()
            hole_colors = []
            draw_screen()
        elif gb.game_over and new_bot_button.collidepoint(mouse_x, mouse_y):
            working_depth = None
            game_active = False
        elif not game_active:
            for rect, depth in bot_choices:
                if rect.collidepoint(mouse_x, mouse_y):
                    working_depth = depth


    def draw_message(msg,
                     bg_col=settings.PLAYER_RECT_COLOR,
                     txt_col=settings.TEXT_COLOR,
                     center=(screen.get_rect().centerx, screen.get_rect().top + settings.HEIGHT_DIV // 2)):
        font = pygame.font.SysFont(None, 48)
        msg_image = font.render(msg, True, txt_col, bg_col)
        msg_rect = msg_image.get_rect()
        msg_rect.center = center
        screen.blit(msg_image, msg_rect)

    def draw_fps():
        global fps_ticks, curr_fps
        fps_ticks += 1
        if fps_ticks > settings.FPS_TICK_LIMIT:
            curr_fps = int(clock.get_fps())
            fps_ticks = 0

        font = pygame.font.SysFont(None, 30)
        fps_surface = font.render(f"FPS: {curr_fps}", True, (0, 0, 0))
        fps_bg = pygame.Rect(10, 10, 100, 30)
        screen.fill((settings.PLAYER_RECT_COLOR), fps_bg)
        screen.blit(fps_surface, (10, 10))

    def place_at(col):
        hole = gb.advance_turn(col)
        try:
         hole_colors[hole[0]][hole[1]] = settings.PLAYER_COLORS[gb.turn + 1]
        except TypeError:
         hole_colors[hole[0]][hole[1]] = settings.PLAYER_COLORS[gb.turn + 1]

    def create_bot_choices():
        global bot_choices
        container_left = screen.get_rect().centerx - settings.SCREEN_DIMS[0] // 5 #choice rects are contained in
        width = settings.SCREEN_DIMS[0] // 10
        for i in range(4):
            rect = pygame.Rect(container_left + i * width, 0, width, settings.HEIGHT_DIV)
            rect.centery = settings.HEIGHT_DIV // 2
            bot_choices.append((rect, i*2))

    def draw_bot_select():
        hdiv = settings.HEIGHT_DIV
        screen_quarter = settings.SCREEN_DIMS[0]//4
        padding = settings.PADDING
        mouse_pos = pygame.mouse.get_pos()
        i = 0
        for rect, depth in bot_choices:
            if rect.collidepoint(mouse_pos):
                color = settings.PLAYER_RECT_COLOR_SELECTED
            else:
                color = settings.PLAYER_RECT_COLOR
            pygame.draw.rect(screen, color, rect, border_radius=settings.PADDING)
            bot_img = pygame.transform.scale(bot, (hdiv - 2 * padding, hdiv - 2 * padding))
            pygame.draw.circle(screen, settings.BOT_LEVEL_COLORS[i], rect.center, hdiv // 2 - padding)
            screen.blit(bot_img, bot_img.get_rect(center=rect.center))
            i += 1

    def check_events():
        for event in pygame.event.get():
            mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                executor.shutdown()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                check_buttons(*mouse_pos)
                if game_active and gb.turn == PLAYER:
                    for i, rect in enumerate(columns):
                        if rect.collidepoint(mouse_pos):
                            place_at(i)

    def draw_screen():
        global columns, players_rect
        columns = []
        hdiv = settings.HEIGHT_DIV
        b_width = settings.BOARD_WIDTH
        b_height = settings.BOARD_HEIGHT
        bg_col = settings.BG_COLOR
        padding = settings.PADDING

        screen.fill((settings.PLAYER_RECT_COLOR), players_rect)
        bg = pygame.Rect(screen.get_rect().left, players_rect.bottom, screen.get_rect().width, screen.get_height() - players_rect.height)
        screen.fill(bg_col, bg)

        board_left = int(screen.get_rect().centerx - hdiv * b_width / 2)
        board_top = bg.top + hdiv
        board_rect = pygame.Rect(board_left, board_top, b_width*hdiv, b_height*hdiv)
        board = pygame.Rect(board_left - padding, board_top - padding, board_rect.width + 2 * padding , board_rect.height + 2 * padding)
        pygame.draw.rect(screen, (67, 146, 186), board, border_radius=padding)
        for row in range(b_height):
            hole_colors.append([])

        left = board_rect.left
        for i in range(b_width):
            top = board_rect.top
            for j in range(b_height):
                hole = pygame.draw.circle(screen, bg_col, (left+hdiv//2, top+hdiv//2), hdiv//2-padding/2)
                top += hdiv
                hole_colors[j].append(bg_col)
            column = pygame.Rect(left, board_rect.top, hdiv, board_rect.height)
            columns.append(column)
            left += hdiv

    def update_screen():
        global bot, person
        hdiv = settings.HEIGHT_DIV
        b_height = settings.BOARD_HEIGHT
        screen_quarter = settings.SCREEN_DIMS[0]//4
        padding = settings.PADDING
        mouse_pos = pygame.mouse.get_pos()

        screen.fill((settings.PLAYER_RECT_COLOR), players_rect)
        pygame.draw.circle(screen, (255,255,255), active_pos[gb.turn+1],hdiv // 2 - padding/2)

        bot = pygame.transform.scale(bot, (hdiv - 2*padding, hdiv - 2*padding))
        person = pygame.transform.scale(person, (hdiv - 2*padding, hdiv - 2*padding))
        player_circle = pygame.draw.circle(screen, settings.PLAYER_COLORS[2], (screen_quarter, screen.get_rect().top + hdiv // 2),
                                           hdiv // 2 - padding)
        ai_circle = pygame.draw.circle(screen, settings.PLAYER_COLORS[1], (screen_quarter * 3, screen.get_rect().top + hdiv // 2),
                                       hdiv // 2 - padding)
        screen.blit(bot, bot.get_rect(center=(screen_quarter * 3, screen.get_rect().top + hdiv//2)))
        screen.blit(person, person.get_rect(center=(screen_quarter, screen.get_rect().top + hdiv//2)))

        for i, rect in enumerate(columns):
            if rect.collidepoint(mouse_pos):
                color = settings.PLAYER_RECT_COLOR_SELECTED
            else:
                color = settings.PLAYER_RECT_COLOR
            pygame.draw.rect(screen, color, rect, border_radius=padding)
            top = rect.top
            for j in range(b_height):
                hole_color = hole_colors[b_height - 1 - j][i]
                pygame.draw.circle(screen, hole_color, (rect.left + hdiv // 2, top + hdiv // 2), hdiv // 2 - padding / 2)
                top += hdiv

        draw_fps()

    draw_screen()
    pygame.display.flip()
    create_bot_choices()
    start, end = 0, 0

    while True:
        check_events()
        if game_active:
            if gb.game_over:
                update_screen()
                rematch_button = draw_button("Rematch", right=screen.get_rect().centerx - settings.BTN_PADDING[0])
                new_bot_button = draw_button("New Bot", left=screen.get_rect().centerx + settings.BTN_PADDING[0])
            else:
                update_screen()
                if gb.turn == BOT:
                    if future is None:
                        ai.gb = gb
                        start = time.time()
                        future = executor.submit(ai.get_move, settings.BOT)
                    elif future.done():
                        move = future.result()
                        end = time.time()
                        print(f"ai chose {move} in {round(end - start, 6)} seconds")
                        place_at(move)
                        future = None
            draw_message(gb.msg)
        else:
            draw_screen()
            draw_bot_select()
            draw_message("Choose bot difficulty",
                         bg_col=settings.BG_COLOR,
                         center=(screen.get_rect().centerx, screen.get_rect().top + 3 * settings.HEIGHT_DIV // 2))
            if working_depth is not None:
                play_button = draw_button("Play")
        pygame.display.flip()
        clock.tick(settings.FPS)
