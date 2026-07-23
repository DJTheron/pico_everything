#include <cstdio>
#include <cstring>

#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"

#include "lib/app.h"
#include "lib/canvas.h"
#include "lib/colors.h"
#include "lib/input.h"
#include "lib/st7789.h"

// App entry points (defined in apps/*.cpp).
void stopwatch_run();
void picotello_run();

// ---- Menu tree ---------------------------------------------------------------
// Root
//  ├── Clock/
//  │    └── Stopwatch
//  └── Picotello
static const MenuItem CLOCK_ITEMS[] = {
    {"Stopwatch", stopwatch_run, nullptr},
};
static const Menu CLOCK_MENU = {CLOCK_ITEMS, 1};

static const MenuItem ROOT_ITEMS[] = {
    {"Clock",     nullptr,       &CLOCK_MENU},
    {"Picotello", picotello_run, nullptr},
};
static const Menu ROOT_MENU = {ROOT_ITEMS, 2};

// A single global framebuffer shared by the launcher and every app.
Canvas g_canvas;

namespace {

// Draw one "card": app name centred, breadcrumb path at top-left.
void draw_card(const MenuItem& item, const char* path) {
    g_canvas.fill(color::BLACK);
    // 8px per char at size 1 for the path; size 2 (16px) for the title.
    int title_len = (int)strlen(item.name);
    int tx = (Canvas::W - title_len * 16) / 2;
    if (tx < 0) tx = 0;
    g_canvas.text(path, 2, 2, color::GREEN, 1);
    g_canvas.text(item.name, tx, 112, color::GREEN, 2);
    g_canvas.show();
}

// Run a menu level. `basepath` is the breadcrumb prefix (e.g. ">apps/Clock/").
void run_menu(const Menu& menu, const char* basepath) {
    int selected = 0;
    char path[96];

    auto redraw = [&]() {
        snprintf(path, sizeof(path), "%s%s", basepath, menu.items[selected].name);
        draw_card(menu.items[selected], path);
    };
    redraw();

    while (true) {
        input::update();

        // left = next, right = prev (matches main.py's inverted feel).
        if (input::pressed(input::LEFT)) {
            selected = (selected + 1) % menu.count;
            redraw();
        }
        if (input::pressed(input::RIGHT)) {
            selected = (selected - 1 + menu.count) % menu.count;
            redraw();
        }

        // A = open app / enter folder.
        if (input::pressed(input::A)) {
            const MenuItem& item = menu.items[selected];
            if (item.run) {
                item.run();
            } else if (item.sub) {
                char sub_base[96];
                snprintf(sub_base, sizeof(sub_base), "%s%s/", basepath, item.name);
                run_menu(*item.sub, sub_base);
            }
            redraw();  // restore the card after returning
        }

        // Y = back up one level. Root's breadcrumb is ">", which has nowhere
        // to go; any deeper path returns to the parent menu.
        if (input::pressed(input::Y) && strcmp(basepath, ">") != 0) {
            return;
        }

        sleep_ms(10);
    }
}

}  // namespace

int main() {
    stdio_init_all();
    st7789::init();
    input::init();

    // Bring up the wireless chip once at boot. Apps that need WiFi (Picotello)
    // assume this succeeded; if it fails, the rest of the launcher still works.
    if (cyw43_arch_init() != 0) {
        g_canvas.fill(color::BLACK);
        g_canvas.text("WiFi init failed", 20, 110, color::RED, 1);
        g_canvas.show();
        sleep_ms(1500);
    }

    // Root breadcrumb is ">"; submenus append "Name/".
    run_menu(ROOT_MENU, ">");
    return 0;
}
