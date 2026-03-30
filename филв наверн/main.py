import flet as ft
import random
import time
import sys
import os
import re
import threading


def main(page: ft.Page):
    # ======== НАСТРОЙКИ ОКНА ========
    page.title = "Математический филворд"
    page.window_width = 1100
    page.window_height = 950
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.BLUE_50

    # ======== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ========
    game_vars = {
        'selected_cells': [],
        'found_answers': [],
        'score': 0,
        'hint_mode': False,
        'difficulty': 'easy',
        'answers_to_find': [],
        'grid': None,
        'answers_list': None,
        'current_example': None,
        'score_text': None,
        'timer_text': None,
        'message': None,
        'hint_text': None,
        'hint_btn': None,
        'new_game_btn': None,
        'menu_btn': None,
        'cells_data': [],
        'variables': {},
        'grid_size': 10,
        'timer_running': True,
        'start_time': 0,
        'time_elapsed': 0,
    }

    # ======== ДАННЫЕ ДЛЯ РАЗНЫХ УРОВНЕЙ СЛОЖНОСТИ ========

    # Простой уровень
    easy_answers = [5, 7, 12, 15, 20, 24, 36, 42, 64, 81, 100, 121, 144]
    easy_examples = [
        "2+3", "4+1", "7-2", "10-5", "5*1", "25/5", "1*5", "9-4",
        "3+4", "5+2", "9-2", "14-7", "7*1", "49/7", "8-1", "21/3",
        "5+7", "8+4", "15-3", "20-8", "3*4", "6*2", "24/2", "36/3", "9+3",
        "7+8", "9+6", "18-3", "20-5", "3*5", "5*3", "30/2", "45/3", "12+3",
        "10+10", "15+5", "25-5", "30-10", "4*5", "5*4", "40/2", "100/5", "18+2",
        "12+12", "18+6", "30-6", "40-16", "4*6", "6*4", "8*3", "48/2", "20+4",
        "18+18", "30+6", "40-4", "50-14", "6*6", "9*4", "12*3", "72/2", "20+16",
        "20+22", "30+12", "50-8", "60-18", "6*7", "7*6", "84/2", "126/3", "21+21",
        "32+32", "40+24", "70-6", "80-16", "8*8", "16*4", "128/2", "256/4", "50+14",
        "40+41", "50+31", "90-9", "100-19", "9*9", "27*3", "162/2", "243/3", "72+9",
        "50+50", "60+40", "110-10", "150-50", "10*10", "25*4", "200/2", "1000/10", "75+25",
        "60+61", "70+51", "130-9", "140-19", "11*11", "121*1", "242/2", "363/3", "100+21",
        "72+72", "80+64", "150-6", "160-16", "12*12", "24*6", "288/2", "576/4", "120+24",
    ]

    # Средний уровень (с переменными X, Y, Z, W)
    medium_answers = [6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 24, 25, 27, 28, 30, 32, 35, 36, 40, 42, 45, 48, 49, 50,
                      54, 56, 60, 63, 64, 70, 72, 80, 81, 90, 100]

    # Сложный уровень
    hard_answers = [
        "5²+10", "6²-6", "7²+7", "8²-8", "9²+9", "10²-10",
        "2³+2", "3³-3", "4³+4", "5³-5", "6³+6", "7³-7",
        "2⁴+4", "3⁴-5", "4⁴+6", "5⁴-7",
        "2⁵+6", "3⁵-8", "4⁵+10",
        "√100+10", "√81+9", "√121+11", "√169-13",
        "10+√100", "30+√81", "50+√121", "60-√169",
        "2³+3³", "3³-2³", "4³+5²", "5³-6²",
        "100/10+5", "144/12-4", "81/9+3", "64/8-2",
    ]

    hard_examples = [
        "5*5+10", "6*6-6", "7*7+7", "8*8-8", "9*9+9", "10*10-10",
        "2*2*2+2", "3*3*3-3", "4*4*4+4", "5*5*5-5", "6*6*6+6", "7*7*7-7",
        "2*2*2*2+4", "3*3*3*3-5", "4*4*4*4+6", "5*5*5*5-7",
        "2*2*2*2*2+6", "3*3*3*3*3-8", "4*4*4*4*4+10",
        "100/10+10", "81/9+9", "121/11+11", "169/13-13",
        "10+100/10", "30+81/9", "50+121/11", "60-169/13",
        "2*2*2+3*3*3", "3*3*3-2*2*2", "4*4*4+5*5", "5*5*5-6*6",
        "100/10+5", "144/12-4", "81/9+3", "64/8-2",
    ]

    # ======== ФУНКЦИИ МЕНЮ ========
    def close_dialog(dialog):
        dialog.open = False
        page.update()

    def show_rules(e):
        """Показывает правила игры"""
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("📖 Правила игры", size=24, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("1) В поле нужно найти математические примеры", size=16),
                    ft.Text("2) Примеры могут изгибаться в любом направлении (и по диагонали)", size=16),
                    ft.Text("3) Слева показаны ответы, которые нужно найти", size=16),
                    ft.Text("4) Выделяй примеры мышкой (зелёным)", size=16),
                    ft.Text("5) Найденные примеры становятся жёлтыми", size=16),
                    ft.Text("6) Можно использовать кнопку подсказки 🔍", size=16),
                    ft.Text("7) Очки = результат примера", size=16),
                    ft.Text("8) Используемые в другом примере цифры могут быть использованы повторно", size=16),
                ], spacing=10),
                width=450,
                padding=20,
            ),
            actions=[ft.TextButton("Понятно!", on_click=lambda e: close_dialog(dlg))],
        )
        page.open(dlg)
        page.update()

    def show_about(e):
        """Показывает информацию об игре"""
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("ℹ️ Об игре", size=24, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("🧮 Математический филворд", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Версия 1.0", size=16),
                    ft.Text("", size=10),
                    ft.Text("Три уровня сложности:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("🟢 ПРОСТОЙ - простые примеры", size=14),
                    ft.Text("🟡 СРЕДНИЙ - буквы на поле (X,Y,Z,W)", size=14),
                    ft.Text("🔴 СЛОЖНЫЙ - составные выражения со знаками", size=14),
                    ft.Text("", size=10),
                    ft.Text("🎮 Пасхалки:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("• Деление на ноль → Фокси", size=14),
                    ft.Text("• Результат 67 → все ответы 67", size=14),
                    ft.Text("• Результат 666 → дьявольская тема", size=14),
                    ft.Text("", size=10),
                    ft.Text("⏱️ Таймер отслеживает время игры", size=14),
                    ft.Text("", size=10),
                    ft.Text("© 2026", size=14),
                ], spacing=5),
                width=450,
                height=450,
                padding=20,
            ),
            actions=[ft.TextButton("Закрыть", on_click=lambda e: close_dialog(dlg))],
        )
        page.open(dlg)
        page.update()

    def exit_game(e):
        """Выход из игры"""
        page.window.destroy()

    # ======== ФУНКЦИЯ ОБНОВЛЕНИЯ ТАЙМЕРА ========
    def update_timer():
        if game_vars['timer_running'] and game_vars['timer_text']:
            game_vars['time_elapsed'] = time.time() - game_vars['start_time']
            minutes = int(game_vars['time_elapsed'] // 60)
            seconds = int(game_vars['time_elapsed'] % 60)
            game_vars['timer_text'].value = f"⏱️ {minutes:02d}:{seconds:02d}"
            page.update()

    def start_timer():
        game_vars['start_time'] = time.time()
        game_vars['timer_running'] = True

        def timer_loop():
            while game_vars['timer_running']:
                update_timer()
                time.sleep(0.5)

        thread = threading.Thread(target=timer_loop, daemon=True)
        thread.start()

    def stop_timer():
        game_vars['timer_running'] = False

    def back_to_menu(e):
        stop_timer()
        if hasattr(page, 'foxy_jumpscare'):
            page.foxy_jumpscare.restore_normal_theme()
        page.controls.clear()
        page.bgcolor = ft.Colors.BLUE_50
        create_main_menu()
        page.update()

    # ======== КЛАСС ДЛЯ АНИМАЦИИ ФОКСИ ========
    class FoxyJumpscare:
        def __init__(self, page):
            self.page = page
            self.foxy = None
            self.dark_bg = None
            self.warning_text = None
            self.is_jumping = False
            self.gif_path = self.find_gif()
            self.original_colors = None

        def find_gif(self):
            possible_paths = [
                "foxy.gif",
                "./foxy.gif",
                os.path.join(os.path.dirname(__file__), "foxy.gif"),
                os.path.join(os.path.dirname(__file__), "assets", "foxy.gif"),
                os.path.join(os.getcwd(), "foxy.gif"),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
            return None

        def create_foxy(self):
            self.dark_bg = ft.Container(
                width=self.page.window_width * 2,
                height=self.page.window_height * 2,
                bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.BLACK),
                left=-self.page.window_width // 2,
                top=-self.page.window_height // 2,
                opacity=0,
            )
            img_size = 1500
            offset = 400
            if self.gif_path:
                self.foxy = ft.Image(
                    src=self.gif_path,
                    width=img_size,
                    height=img_size,
                    fit=ft.ImageFit.CONTAIN,
                    opacity=0,
                    left=self.page.window_width // 2 - img_size // 2 + offset,
                    top=self.page.window_height // 2 - img_size // 2,
                )
            else:
                foxy_art = [
                    "           /\\____________/\\           ",
                    "          /  \\   🦊   /  \\          ",
                    "         /    \\_____/    \\         ",
                    "        /______/     \\______\\        ",
                    "       |      | FOXY |      |       ",
                    "       |      | JUMP |      |       ",
                    "       \\______\\_____/______/       ",
                    "          |         |          ",
                    "          |  BOO!   |          ",
                    "          |_________|          "
                ]
                text_content = ft.Column(
                    [ft.Text(line, size=72, weight=ft.FontWeight.BOLD,
                             color=ft.Colors.RED_900, font_family="Courier New",
                             text_align=ft.TextAlign.CENTER)
                     for line in foxy_art],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15
                )
                self.foxy = ft.Container(
                    content=text_content,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=40,
                    padding=70,
                    opacity=0,
                    left=self.page.window_width // 2 - 750 + offset,
                    top=self.page.window_height // 2 - 600,
                    width=1500,
                    height=1200,
                )
            text_offset = int(self.page.window_width * 0.04)
            self.warning_text = ft.Text(
                "⚠️ ДЕЛЕНИЕ НА НОЛЬ! ⚠️",
                size=48,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.RED_900,
                opacity=0,
                left=self.page.window_width // 2 - 200 + offset - text_offset,
                top=30,
            )

        def jump(self):
            if self.is_jumping:
                return
            self.is_jumping = True
            if not self.foxy:
                self.create_foxy()
            img_size = 1500
            offset = 400
            text_offset = int(self.page.window_width * 0.04)
            self.foxy.left = self.page.window_width // 2 - img_size // 2 + offset
            self.foxy.top = self.page.window_height // 2 - img_size // 2
            self.warning_text.left = self.page.window_width // 2 - 200 + offset - text_offset
            self.dark_bg.width = self.page.window_width * 2
            self.dark_bg.height = self.page.window_height * 2
            self.dark_bg.left = -self.page.window_width // 2
            self.dark_bg.top = -self.page.window_height // 2
            self.page.overlay.append(self.dark_bg)
            self.page.overlay.append(self.foxy)
            self.page.overlay.append(self.warning_text)
            self.foxy.opacity = 0
            self.dark_bg.opacity = 0
            self.warning_text.opacity = 0
            self.page.update()

            def animate():
                try:
                    for i in range(15):
                        self.dark_bg.opacity = i * 0.06
                        self.page.update()
                        time.sleep(0.02)
                    for i in range(10):
                        self.foxy.opacity = i * 0.1
                        self.page.update()
                        time.sleep(0.02)
                    for i in range(5):
                        self.warning_text.opacity = i * 0.2
                        self.page.update()
                        time.sleep(0.03)
                    time.sleep(1.5)
                    for i in range(15):
                        self.foxy.opacity = 1 - i * 0.07
                        self.dark_bg.opacity = 0.9 - i * 0.06
                        self.warning_text.opacity = 1 - i * 0.07
                        self.page.update()
                        time.sleep(0.05)
                    if self.dark_bg in self.page.overlay:
                        self.page.overlay.remove(self.dark_bg)
                    if self.foxy in self.page.overlay:
                        self.page.overlay.remove(self.foxy)
                    if self.warning_text in self.page.overlay:
                        self.page.overlay.remove(self.warning_text)
                    self.page.update()
                except Exception:
                    try:
                        if self.dark_bg in self.page.overlay:
                            self.page.overlay.remove(self.dark_bg)
                        if self.foxy in self.page.overlay:
                            self.page.overlay.remove(self.foxy)
                        if self.warning_text in self.page.overlay:
                            self.page.overlay.remove(self.warning_text)
                        self.page.update()
                    except:
                        pass
                finally:
                    self.is_jumping = False

            thread = threading.Thread(target=animate)
            thread.daemon = True
            thread.start()

        def sixty_seven_magic(self, duration=3):
            original_answers = game_vars['answers_to_find'].copy()
            temp_answers = ["67"] * len(original_answers)
            game_vars['answers_to_find'] = temp_answers
            update_answers_list()
            game_vars['message'].value = "67 67 67 67 67 67 67 67 67 67 67"
            game_vars['message'].color = ft.Colors.ORANGE_600
            game_vars['message'].visible = True
            game_vars['message'].size = 32
            self.page.update()

            def restore():
                time.sleep(duration)
                game_vars['answers_to_find'] = original_answers
                update_answers_list()
                game_vars['message'].visible = False
                game_vars['message'].size = 24
                self.page.update()

            thread = threading.Thread(target=restore)
            thread.daemon = True
            thread.start()

        def six_six_six(self):
            if not self.original_colors:
                self.original_colors = {
                    'bg': self.page.bgcolor,
                    'score_color': game_vars['score_text'].color,
                    'hint_color': game_vars['hint_text'].color,
                    'current_example_color': game_vars['current_example'].color,
                }
            self.page.bgcolor = ft.Colors.BLACK
            game_vars['score_text'].color = ft.Colors.RED_900
            game_vars['hint_text'].color = ft.Colors.RED_900
            game_vars['current_example'].color = ft.Colors.RED_900
            if game_vars['hint_mode']:
                game_vars['hint_text'].value = "🔥 Подсказка включена 🔥"
            else:
                game_vars['hint_text'].value = "🔥 Подсказка выключена 🔥"
            top_row = page.controls[0]
            top_row.controls.clear()
            new_score_text = ft.Text(f"Очки: {game_vars['score']}", size=20, weight=ft.FontWeight.BOLD,
                                     color=ft.Colors.RED_900)
            game_vars['score_text'] = new_score_text
            new_timer_text = ft.Text("⏱️ 00:00", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_900)
            game_vars['timer_text'] = new_timer_text
            new_hint_btn = ft.ElevatedButton(
                "🔥 Никто тебе не поможет 🔥",
                on_click=toggle_hint,
                style=ft.ButtonStyle(
                    color=ft.Colors.ORANGE_200,
                    bgcolor=ft.Colors.RED_900,
                    padding=15,
                )
            )
            game_vars['hint_btn'] = new_hint_btn
            new_game_btn = ft.ElevatedButton(
                "😈 Искупить грехи 😈",
                on_click=new_game,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.RED_900,
                    padding=20,
                )
            )
            game_vars['new_game_btn'] = new_game_btn
            menu_btn = ft.ElevatedButton(
                "👼 СПАСЕНИЕ 👼",
                on_click=back_to_menu,
                style=ft.ButtonStyle(
                    color=ft.Colors.RED_900,
                    bgcolor=ft.Colors.WHITE,
                    padding=20,
                )
            )
            game_vars['menu_btn'] = menu_btn
            top_row.controls.append(new_score_text)
            top_row.controls.append(new_timer_text)
            top_row.controls.append(new_hint_btn)
            top_row.controls.append(new_game_btn)
            top_row.controls.append(menu_btn)
            for container in game_vars['grid'].controls:
                if container.bgcolor == ft.Colors.BLUE_100:
                    container.bgcolor = ft.Colors.RED_900
                elif container.bgcolor == ft.Colors.GREEN_200:
                    container.bgcolor = ft.Colors.ORANGE_600
                elif container.bgcolor == ft.Colors.YELLOW_200:
                    container.bgcolor = ft.Colors.ORANGE_900
            game_vars['message'].value = "👿 666 👿"
            game_vars['message'].color = ft.Colors.RED_900
            game_vars['message'].visible = True
            game_vars['message'].size = 48
            self.page.update()
            update_answers_list()

        def restore_normal_theme(self):
            """Восстанавливает нормальную тему (при новой игре или выходе в меню)"""
            print("🔄 Восстанавливаю нормальную тему...")

            # Восстанавливаем фон
            if self.original_colors:
                self.page.bgcolor = self.original_colors['bg']
                game_vars['score_text'].color = self.original_colors['score_color']
                game_vars['hint_text'].color = self.original_colors['hint_color']
                game_vars['current_example'].color = self.original_colors['current_example_color']
                self.original_colors = None
            else:
                self.page.bgcolor = ft.Colors.WHITE
                game_vars['score_text'].color = ft.Colors.BLUE_900
                game_vars['hint_text'].color = ft.Colors.GREY_700
                game_vars['current_example'].color = ft.Colors.BLACK

            # Восстанавливаем текст подсказки
            if game_vars['hint_mode']:
                game_vars['hint_text'].value = "🔍 Подсказка включена"
            else:
                game_vars['hint_text'].value = "⚫ Подсказка выключена"
            game_vars['hint_text'].color = ft.Colors.GREY_700

            # Восстанавливаем цвета клеток
            for container in game_vars['grid'].controls:
                if container.bgcolor == ft.Colors.RED_900:
                    container.bgcolor = ft.Colors.BLUE_100
                elif container.bgcolor == ft.Colors.ORANGE_600:
                    container.bgcolor = ft.Colors.GREEN_200
                elif container.bgcolor == ft.Colors.ORANGE_900:
                    container.bgcolor = ft.Colors.YELLOW_200

            # ПЕРЕСОЗДАЁМ КНОПКИ
            top_row = self.page.controls[0]
            top_row.controls.clear()

            new_score_text = ft.Text(f"Очки: {game_vars['score']}", size=20, weight=ft.FontWeight.BOLD,
                                     color=ft.Colors.BLUE_900)
            game_vars['score_text'] = new_score_text

            new_timer_text = ft.Text("⏱️ 00:00", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
            game_vars['timer_text'] = new_timer_text

            new_hint_btn = ft.ElevatedButton(
                "⚫ Подсказка: ВЫКЛ" if not game_vars['hint_mode'] else "🔍 Подсказка: ВКЛ",
                on_click=toggle_hint,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.GREY_400 if not game_vars['hint_mode'] else ft.Colors.GREEN_600,
                    padding=15,
                )
            )
            game_vars['hint_btn'] = new_hint_btn

            new_game_btn = ft.ElevatedButton(
                "🔄 Новая игра",
                on_click=new_game,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_600,
                    padding=20,
                )
            )
            game_vars['new_game_btn'] = new_game_btn

            menu_btn = ft.ElevatedButton(
                "🏠 В меню",
                on_click=back_to_menu,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.ORANGE_600,
                    padding=20,
                )
            )
            game_vars['menu_btn'] = menu_btn

            top_row.controls.append(new_score_text)
            top_row.controls.append(new_timer_text)
            top_row.controls.append(new_hint_btn)
            top_row.controls.append(new_game_btn)
            top_row.controls.append(menu_btn)

            game_vars['message'].visible = False
            game_vars['message'].size = 24

            update_answers_list()
            self.page.update()
            print("✅ Нормальная тема восстановлена, кнопки пересозданы")

    # ======== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ========
    def generate_variables():
        available = list(range(2, 10))
        random.shuffle(available)
        return {'X': available[0], 'Y': available[1], 'Z': available[2], 'W': available[3]}

    def get_difficulty_data(difficulty):
        if difficulty == 'easy':
            return {'answers': easy_answers.copy(), 'examples': easy_examples.copy(), 'grid_size': 10,
                    'name': 'ПРОСТОЙ', 'color': ft.Colors.GREEN_600, 'has_variables': False}
        elif difficulty == 'medium':
            vars_dict = generate_variables()
            game_vars['variables'] = vars_dict
            return {'answers': medium_answers.copy(), 'examples': easy_examples.copy(), 'grid_size': 12,
                    'name': 'СРЕДНИЙ', 'color': ft.Colors.ORANGE_600, 'has_variables': True, 'variables': vars_dict}
        else:
            return {'answers': hard_answers.copy(), 'examples': hard_examples.copy(), 'grid_size': 14,
                    'name': 'СЛОЖНЫЙ', 'color': ft.Colors.RED_600, 'has_variables': False}

    def find_snake_path(board, example, start_r, start_c, visited=None):
        if visited is None:
            visited = [(start_r, start_c)]
        if len(visited) == len(example):
            return visited
        current_char = example[len(visited)]
        last_r, last_c = visited[-1]
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = last_r + dr, last_c + dc
                if nr < 0 or nr >= game_vars['grid_size'] or nc < 0 or nc >= game_vars['grid_size']:
                    continue
                if (nr, nc) in visited:
                    continue
                if board[nr][nc] is not None and board[nr][nc] != current_char:
                    continue
                new_visited = visited + [(nr, nc)]
                result = find_snake_path(board, example, nr, nc, new_visited)
                if result:
                    return result
        return None

    def place_example_snake(board, example):
        for _ in range(300):
            start_r = random.randint(0, game_vars['grid_size'] - 1)
            start_c = random.randint(0, game_vars['grid_size'] - 1)
            if board[start_r][start_c] is not None and board[start_r][start_c] != example[0]:
                continue
            path = find_snake_path(board, example, start_r, start_c, [(start_r, start_c)])
            if path:
                for i, (r, c) in enumerate(path):
                    board[r][c] = example[i]
                return path
        return None

    def transform_example_with_vars(example):
        if game_vars['difficulty'] != 'medium' or not game_vars['variables']:
            return example
        result = example
        for var, val in game_vars['variables'].items():
            result = result.replace(str(val), var)
        return result

    def evaluate_expr(expr):
        expr_copy = expr
        if game_vars['difficulty'] == 'medium' and game_vars['variables']:
            for var, val in game_vars['variables'].items():
                expr_copy = expr_copy.replace(var, str(val))
        try:
            expr_copy = expr_copy.replace('×', '*').replace(' ', '')
            return eval(expr_copy)
        except:
            return None

    def matches_answer(example_expr, answer_str):
        example_value = evaluate_expr(example_expr)
        if example_value is None:
            return False

        # Если ответ — число (простой и средний уровень)
        if isinstance(answer_str, (int, float)):
            return abs(example_value - answer_str) < 0.1

        # Если ответ — строка с выражением (сложный уровень)
        if isinstance(answer_str, str):
            answer_value = evaluate_complex_answer(answer_str)
            if answer_value is None:
                return False
            return abs(example_value - answer_value) < 0.1

        return False

    def evaluate_complex_answer(answer_str):
        temp = answer_str
        temp = re.sub(r'(\d+)²', r'\1*\1', temp)
        temp = re.sub(r'(\d+)³', r'\1*\1*\1', temp)
        temp = re.sub(r'(\d+)⁴', r'\1*\1*\1*\1', temp)
        temp = re.sub(r'(\d+)⁵', r'\1*\1*\1*\1*\1', temp)
        temp = re.sub(r'√(\d+)', r'math.sqrt(\1)', temp)
        try:
            import math
            return eval(temp)
        except:
            return None

    def generate_board():
        board = [[None for _ in range(game_vars['grid_size'])] for _ in range(game_vars['grid_size'])]
        difficulty_data = get_difficulty_data(game_vars['difficulty'])
        all_examples = difficulty_data['examples'].copy()
        random.shuffle(all_examples)
        examples_to_place = all_examples[:25]
        for example in examples_to_place:
            display_example = transform_example_with_vars(example)
            path = place_example_snake(board, display_example)
            if path:
                print(f"✅ Размещён пример: {display_example}")
        if game_vars['difficulty'] == 'medium':
            available_digits = [str(d) for d in range(0, 10) if d not in game_vars['variables'].values()]
            symbols = "".join(available_digits) + "+-*/XYZW"
        else:
            symbols = "0123456789+-*/"
        for r in range(game_vars['grid_size']):
            for c in range(game_vars['grid_size']):
                if board[r][c] is None:
                    board[r][c] = random.choice(symbols)
        return board

    def is_neighbor(cell1, cell2):
        row_diff = abs(cell1["row"] - cell2["row"])
        col_diff = abs(cell1["col"] - cell2["col"])
        return row_diff <= 1 and col_diff <= 1 and not (row_diff == 0 and col_diff == 0)

    def update_hint():
        if not game_vars['hint_mode']:
            game_vars['hint_text'].value = "⚫ Подсказка выключена"
            game_vars['hint_text'].color = ft.Colors.GREY_400
            game_vars['hint_text'].size = 16
            return
        if len(game_vars['selected_cells']) == 0:
            game_vars['hint_text'].value = "🔍 Выдели пример мышкой"
            game_vars['hint_text'].color = ft.Colors.GREY_700
            game_vars['hint_text'].size = 18
        else:
            current = "".join([cell["letter"] for cell in game_vars['selected_cells']])
            if not any(sign in current for sign in ['+', '-', '*', '/']):
                game_vars['hint_text'].value = "⚠️ Это просто число, нужен пример со знаком (+, -, *, /)"
                game_vars['hint_text'].color = ft.Colors.ORANGE_600
                game_vars['hint_text'].size = 18
            else:
                result = evaluate_expr(current)
                if result is not None:
                    found_match = False
                    for answer in game_vars['answers_to_find']:
                        if matches_answer(current, answer):
                            found_match = True
                            if answer in game_vars['found_answers']:
                                game_vars[
                                    'hint_text'].value = f"✅ {current} = {result:.0f} (соответствует {answer} - УЖЕ НАЙДЕНО!)"
                                game_vars['hint_text'].color = ft.Colors.GREEN_900
                            else:
                                game_vars[
                                    'hint_text'].value = f"🔍 {current} = {result:.0f} (соответствует {answer} - ещё не найдено)"
                                game_vars['hint_text'].color = ft.Colors.BLUE_900
                            break
                    if not found_match:
                        game_vars['hint_text'].value = f"❌ {current} = {result:.0f} (нет в списке ответов)"
                        game_vars['hint_text'].color = ft.Colors.RED_600
                else:
                    game_vars['hint_text'].value = "❌ Не могу вычислить :("
                    game_vars['hint_text'].color = ft.Colors.RED_600
                game_vars['hint_text'].size = 18
        page.update()

    def toggle_hint(e):
        game_vars['hint_mode'] = not game_vars['hint_mode']
        is_hell_mode = False
        if hasattr(page, 'foxy_jumpscare') and page.foxy_jumpscare.original_colors:
            if page.bgcolor == ft.Colors.BLACK:
                is_hell_mode = True
        if game_vars['hint_mode']:
            game_vars['hint_btn'].text = "🔍 Подсказка: ВКЛ" if not is_hell_mode else "🔥 Подсказка: ВКЛ 🔥"
            game_vars['hint_btn'].style.bgcolor = ft.Colors.GREEN_600 if not is_hell_mode else ft.Colors.RED_900
            game_vars['hint_text'].value = "🔍 Подсказка включена" if not is_hell_mode else "🔥 Подсказка включена 🔥"
        else:
            game_vars['hint_btn'].text = "⚫ Подсказка: ВЫКЛ" if not is_hell_mode else "🔥 Подсказка выключена 🔥"
            game_vars['hint_btn'].style.bgcolor = ft.Colors.GREY_400 if not is_hell_mode else ft.Colors.RED_900
            game_vars['hint_text'].value = "⚫ Подсказка выключена" if not is_hell_mode else "🔥 Подсказка выключена 🔥"
        if is_hell_mode:
            game_vars['hint_text'].color = ft.Colors.RED_900
            game_vars['hint_btn'].style.color = ft.Colors.ORANGE_200
        else:
            game_vars['hint_text'].color = ft.Colors.GREY_700
            game_vars['hint_btn'].style.color = ft.Colors.WHITE
        update_hint()
        page.update()

    def check_example():
        current = "".join([cell["letter"] for cell in game_vars['selected_cells']])
        if not any(sign in current for sign in ['+', '-', '*', '/']):
            update_hint()
            return
        if '/0' in current or '/ 0' in current:
            if not hasattr(page, 'foxy_jumpscare'):
                page.foxy_jumpscare = FoxyJumpscare(page)
            page.foxy_jumpscare.jump()
            show_message("⚠️ НЕЛЬЗЯ ДЕЛИТЬ НА НОЛЬ! ⚠️", ft.Colors.RED_900)
            clear_selection()
            update_hint()
            return
        result = evaluate_expr(current)
        if result == 67:
            if not hasattr(page, 'foxy_jumpscare'):
                page.foxy_jumpscare = FoxyJumpscare(page)
            page.foxy_jumpscare.sixty_seven_magic(3)
            clear_selection()
            update_hint()
            return
        if result == 666:
            if not hasattr(page, 'foxy_jumpscare'):
                page.foxy_jumpscare = FoxyJumpscare(page)
            page.foxy_jumpscare.six_six_six()
            clear_selection()
            update_hint()
            return
        if result is not None:
            for answer in game_vars['answers_to_find']:
                if matches_answer(current, answer) and answer not in game_vars['found_answers']:
                    game_vars['found_answers'].append(answer)
                    game_vars['score'] += int(result)
                    show_message(f"Отлично! {current} = {result:.0f} (соответствует {answer}) +{int(result)} очков!",
                                 ft.Colors.GREEN)
                    game_vars['score_text'].value = f"Очки: {game_vars['score']}"
                    update_answers_list()
                    for cell_data in game_vars['selected_cells']:
                        for container in game_vars['grid'].controls:
                            if container.data == cell_data:
                                container.bgcolor = ft.Colors.YELLOW_200
                    clear_selection()
                    if len(game_vars['found_answers']) == len(game_vars['answers_to_find']):
                        stop_timer()
                        show_message("ПОБЕДА! Ты нашёл все ответы! 🎉", ft.Colors.ORANGE)
                    break
        update_hint()
        page.update()

    def update_answers_list():
        if game_vars['answers_list'] is None:
            return
        game_vars['answers_list'].controls.clear()
        difficulty_name = "ПРОСТОЙ"
        difficulty_color = ft.Colors.GREEN_600
        is_hell_mode = False
        if hasattr(page, 'foxy_jumpscare') and page.foxy_jumpscare.original_colors:
            if page.bgcolor == ft.Colors.BLACK:
                is_hell_mode = True
        if game_vars['difficulty'] == 'medium':
            difficulty_name = "СРЕДНИЙ"
            difficulty_color = ft.Colors.ORANGE_600 if not is_hell_mode else ft.Colors.RED_900
        elif game_vars['difficulty'] == 'hard':
            difficulty_name = "СЛОЖНЫЙ"
            difficulty_color = ft.Colors.RED_600 if not is_hell_mode else ft.Colors.RED_900
        else:
            difficulty_color = ft.Colors.GREEN_600 if not is_hell_mode else ft.Colors.RED_900
        game_vars['answers_list'].controls.append(
            ft.Text(f"Уровень: {difficulty_name}", size=16, weight=ft.FontWeight.BOLD, color=difficulty_color))
        header_color = ft.Colors.BLACK if not is_hell_mode else ft.Colors.RED_900
        game_vars['answers_list'].controls.append(
            ft.Text(f"Найди примеры:", size=16, weight=ft.FontWeight.BOLD, color=header_color))
        for answer in game_vars['answers_to_find']:
            if answer in game_vars['found_answers']:
                color = ft.Colors.GREEN_900
                prefix = "✓"
                weight = ft.FontWeight.BOLD
            else:
                if is_hell_mode:
                    color = ft.Colors.RED_900
                else:
                    color = ft.Colors.BLACK
                prefix = "○"
                weight = ft.FontWeight.NORMAL
            game_vars['answers_list'].controls.append(
                ft.Container(content=ft.Text(f"{prefix} {answer}", size=18, color=color, weight=weight), padding=3))
        counter_color = ft.Colors.BLUE_900 if not is_hell_mode else ft.Colors.RED_900
        game_vars['answers_list'].controls.append(ft.Container(
            content=ft.Text(f"Найдено: {len(game_vars['found_answers'])}/{len(game_vars['answers_to_find'])}", size=14,
                            color=counter_color, weight=ft.FontWeight.BOLD), padding=10))
        page.update()

    def clear_selection():
        if game_vars['grid'] is None:
            return
        for cell_container in game_vars['grid'].controls:
            if cell_container.bgcolor == ft.Colors.GREEN_200:
                cell_container.bgcolor = ft.Colors.BLUE_100
        game_vars['selected_cells'].clear()
        game_vars['current_example'].value = "Текущий пример: "
        update_hint()

    def show_message(text, color):
        if game_vars['message'] is None:
            return
        game_vars['message'].value = text
        game_vars['message'].color = color
        game_vars['message'].visible = True
        page.update()
        time.sleep(2)
        game_vars['message'].visible = False
        page.update()

    # ======== ФУНКЦИИ УПРАВЛЕНИЯ ИГРОЙ ========
    def set_difficulty(level):
        game_vars['difficulty'] = level
        difficulty_data = get_difficulty_data(level)
        game_vars['grid_size'] = difficulty_data['grid_size']
        start_game(None)

    def start_game(e):
        page.controls.clear()
        page.bgcolor = ft.Colors.WHITE
        create_game_interface()
        start_timer()
        page.update()

    def on_cell_click(e):
        cell_container = e.control
        cell_data = cell_container.data
        if cell_container.bgcolor == ft.Colors.YELLOW_200:
            pass
        if len(game_vars['selected_cells']) == 0:
            if cell_container.bgcolor != ft.Colors.GREEN_200:
                cell_container.bgcolor = ft.Colors.GREEN_200
            game_vars['selected_cells'].append(cell_data)
        else:
            last_cell = game_vars['selected_cells'][-1]
            if is_neighbor(last_cell, cell_data):
                already_selected = False
                for cell in game_vars['selected_cells']:
                    if cell["row"] == cell_data["row"] and cell["col"] == cell_data["col"]:
                        already_selected = True
                        break
                if not already_selected:
                    if cell_container.bgcolor == ft.Colors.BLUE_100:
                        cell_container.bgcolor = ft.Colors.GREEN_200
                    game_vars['selected_cells'].append(cell_data)
            else:
                clear_selection()
                if cell_container.bgcolor != ft.Colors.GREEN_200:
                    cell_container.bgcolor = ft.Colors.GREEN_200
                game_vars['selected_cells'].append(cell_data)
        current_text = "".join([cell["letter"] for cell in game_vars['selected_cells']])
        game_vars['current_example'].value = f"Текущий пример: {current_text}"
        update_hint()
        page.update()
        check_example()

    def new_game(e):
        """Новая игра"""
        stop_timer()

        # Восстанавливаем нормальную тему
        if hasattr(page, 'foxy_jumpscare'):
            page.foxy_jumpscare.restore_normal_theme()

        game_vars['found_answers'] = []
        game_vars['score'] = 0
        game_vars['selected_cells'] = []

        difficulty_data = get_difficulty_data(game_vars['difficulty'])
        game_vars['answers_to_find'] = difficulty_data['answers']
        game_vars['grid_size'] = difficulty_data['grid_size']

        if game_vars['difficulty'] == 'medium':
            game_vars['variables'] = generate_variables()

        board = generate_board()

        game_vars['cells_data'] = []
        for row in range(game_vars['grid_size']):
            for col in range(game_vars['grid_size']):
                game_vars['cells_data'].append({"letter": board[row][col], "row": row, "col": col})

        if game_vars['grid'] is not None:
            game_vars['grid'].controls.clear()
            for cell_data in game_vars['cells_data']:
                cell = ft.Container(
                    content=ft.Text(cell_data["letter"], size=20, weight=ft.FontWeight.BOLD),
                    alignment=ft.alignment.center,
                    bgcolor=ft.Colors.BLUE_100,
                    border_radius=ft.border_radius.all(10),
                    ink=True,
                    on_click=on_cell_click,
                    data=cell_data,
                )
                game_vars['grid'].controls.append(cell)
            game_vars['grid'].runs_count = game_vars['grid_size']

        game_vars['score_text'].value = f"Очки: 0"
        game_vars['current_example'].value = "Текущий пример: "

        update_answers_list()
        update_hint()

        start_timer()
        page.update()

    # ======== СОЗДАНИЕ ИНТЕРФЕЙСОВ ========
    def create_main_menu():
        title = ft.Text("🧮 МАТЕМАТИЧЕСКИЙ\n   ФИЛВОРД", size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900,
                        text_align=ft.TextAlign.CENTER)
        subtitle = ft.Text("Найди примеры → получи ответы", size=24, color=ft.Colors.BLUE_700, italic=True)

        easy_btn = ft.ElevatedButton("🟢 ПРОСТОЙ", on_click=lambda e: set_difficulty('easy'),
                                     style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600,
                                                          padding=15,
                                                          text_style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)),
                                     width=200, height=60)
        medium_btn = ft.ElevatedButton("🟡 СРЕДНИЙ", on_click=lambda e: set_difficulty('medium'),
                                       style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.ORANGE_600,
                                                            padding=15, text_style=ft.TextStyle(size=20,
                                                                                                weight=ft.FontWeight.BOLD)),
                                       width=200, height=60)
        hard_btn = ft.ElevatedButton("🔴 СЛОЖНЫЙ", on_click=lambda e: set_difficulty('hard'),
                                     style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_600, padding=15,
                                                          text_style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)),
                                     width=200, height=60)

        rules_btn = ft.ElevatedButton("📖 ПРАВИЛА", on_click=show_rules,
                                      style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_600,
                                                           padding=15,
                                                           text_style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)),
                                      width=300, height=60)
        about_btn = ft.ElevatedButton("ℹ️ ОБ ИГРЕ", on_click=show_about,
                                      style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.PURPLE_600,
                                                           padding=15,
                                                           text_style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)),
                                      width=300, height=60)
        exit_btn = ft.ElevatedButton("🚪 ВЫХОД", on_click=exit_game,
                                     style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_600, padding=15,
                                                          text_style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)),
                                     width=300, height=60)

        difficulty_row = ft.Row([easy_btn, medium_btn, hard_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        examples_row = ft.Row([
            ft.Container(content=ft.Text("2+3=5", size=20), bgcolor=ft.Colors.YELLOW_200, padding=10, border_radius=10),
            ft.Container(content=ft.Text("X+Y=12", size=20), bgcolor=ft.Colors.ORANGE_200, padding=10,
                         border_radius=10),
            ft.Container(content=ft.Text("8²-8=56", size=20), bgcolor=ft.Colors.RED_200, padding=10, border_radius=10),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

        menu = ft.Column([
            ft.Container(height=50), title, ft.Container(height=20), subtitle, ft.Container(height=30), examples_row,
            ft.Container(height=40), ft.Text("Выбери уровень сложности:", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=20), difficulty_row, ft.Container(height=40), rules_btn, ft.Container(height=10),
            about_btn, ft.Container(height=10), exit_btn,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        page.add(menu)

    def create_game_interface():
        difficulty_data = get_difficulty_data(game_vars['difficulty'])
        game_vars['answers_to_find'] = difficulty_data['answers']
        game_vars['grid_size'] = difficulty_data['grid_size']
        game_vars['selected_cells'] = []
        game_vars['found_answers'] = []
        game_vars['score'] = 0
        game_vars['hint_mode'] = False
        if game_vars['difficulty'] == 'medium':
            game_vars['variables'] = generate_variables()
        board = generate_board()
        game_vars['cells_data'] = []
        for row in range(game_vars['grid_size']):
            for col in range(game_vars['grid_size']):
                game_vars['cells_data'].append({"letter": board[row][col], "row": row, "col": col})
        game_vars['grid'] = ft.GridView(runs_count=game_vars['grid_size'], spacing=5, run_spacing=5, width=650,
                                        height=650)
        for cell_data in game_vars['cells_data']:
            cell = ft.Container(content=ft.Text(cell_data["letter"], size=20, weight=ft.FontWeight.BOLD),
                                alignment=ft.alignment.center, bgcolor=ft.Colors.BLUE_100,
                                border_radius=ft.border_radius.all(10), ink=True, on_click=on_cell_click,
                                data=cell_data)
            game_vars['grid'].controls.append(cell)
        game_vars['answers_list'] = ft.Column(spacing=5, width=200, scroll=ft.ScrollMode.AUTO)
        game_vars['current_example'] = ft.Text("Текущий пример: ", size=20, weight=ft.FontWeight.BOLD)
        game_vars['score_text'] = ft.Text("Очки: 0", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
        game_vars['timer_text'] = ft.Text("⏱️ 00:00", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
        game_vars['message'] = ft.Text("", size=24, weight=ft.FontWeight.BOLD, visible=False)
        game_vars['hint_text'] = ft.Text("⚫ Подсказка выключена", size=16, weight=ft.FontWeight.BOLD,
                                         color=ft.Colors.GREY_400)
        game_vars['hint_btn'] = ft.ElevatedButton("⚫ Подсказка: ВЫКЛ", on_click=toggle_hint,
                                                  style=ft.ButtonStyle(color=ft.Colors.WHITE,
                                                                       bgcolor=ft.Colors.GREY_400, padding=15))
        game_vars['new_game_btn'] = ft.ElevatedButton("🔄 Новая игра", on_click=new_game,
                                                      style=ft.ButtonStyle(color=ft.Colors.WHITE,
                                                                           bgcolor=ft.Colors.BLUE_600, padding=20))
        game_vars['menu_btn'] = ft.ElevatedButton("🏠 В меню", on_click=back_to_menu,
                                                  style=ft.ButtonStyle(color=ft.Colors.WHITE,
                                                                       bgcolor=ft.Colors.ORANGE_600, padding=20))
        vars_info = ft.Text("", size=14)
        if game_vars['difficulty'] == 'medium':
            vars_info = ft.Text(f"Буквы X, Y, Z, W на поле - это цифры", size=16, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.ORANGE_900, italic=True)
        elif game_vars['difficulty'] == 'hard':
            vars_info = ft.Text(f"Ищи примеры, соответствующие выражениям со знаками", size=16,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.RED_900, italic=True)
        top_row = ft.Row(
            [game_vars['score_text'], game_vars['timer_text'], game_vars['hint_btn'], game_vars['new_game_btn'],
             game_vars['menu_btn']], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        main_content = ft.Row([
            ft.Column([ft.Container(content=game_vars['answers_list'], width=220, height=650,
                                    border=ft.border.all(2, ft.Colors.BLUE_200), border_radius=10, padding=10),
                       vars_info], spacing=10),
            ft.Column([game_vars['grid'], game_vars['current_example'], game_vars['hint_text']], spacing=20)
        ], spacing=30, vertical_alignment=ft.CrossAxisAlignment.START)
        update_answers_list()
        page.add(top_row, main_content, game_vars['message'])

    # ======== ЗАПУСК ========
    create_main_menu()


ft.app(target=main)