#include <graphics.h>
#include <iostream>
#include <cstdio>
#include <windows.h>
#include "cg_math.h"
#include "map_engine.h"
#include "entities.h"

// ============================================================================
// WINDOW SETTINGS (PHASE 2)
// Window Size: 980 x 820
// Clean wireframe stealth simulation — NO GRID LINES IN BETWEEN MAPS!
// ============================================================================
const int WINDOW_WIDTH  = 980;
const int WINDOW_HEIGHT = 820;

int main() {
    initwindow(WINDOW_WIDTH, WINDOW_HEIGHT, "SHADOW HUNT - Grayscale Static Wireframe (Phase 2 C++)");

    std::cout << "============================================================" << std::endl;
    std::cout << "      HUNTER ASSASSIN - PHASE 2 (C++ CORE ALGORITHMS)       " << std::endl;
    std::cout << "============================================================" << std::endl;
    std::cout << " Algorithms Applied:" << std::endl;
    std::cout << "   - DDA Line Algorithm (assign1.cpp)" << std::endl;
    std::cout << "   - Bresenham Line Algorithm (assign1b.cpp)" << std::endl;
    std::cout << "   - Midpoint Circle Algorithm (assign2.cpp)" << std::endl;
    std::cout << "   - 3x3 Affine Transformation Matrices (assign3.cpp)" << std::endl;
    std::cout << "   - Ray-Casting Point-in-Polygon for FOV Vision Cones" << std::endl;
    std::cout << " Note: Grids removed completely from the map environment!" << std::endl;
    std::cout << " Controls:" << std::endl;
    std::cout << "   - [H]         : Toggle Midpoint Circle Hitboxes" << std::endl;
    std::cout << "   - [R]         : Restart / Reset Simulation" << std::endl;
    std::cout << "   - [ESC] / [Q] : Exit Game" << std::endl;
    std::cout << "============================================================" << std::endl;

    float origin_x = (WINDOW_WIDTH  - 770.0f) / 2.0f;
    float origin_y = (WINDOW_HEIGHT - 550.0f) / 2.0f + 25.0f;

    // Simulation Subsystems
    MapEngine mapEngine(origin_x, origin_y);
    Player player(origin_x + 55.0f, origin_y + 55.0f, 4.5f);
    CollectibleManager collectibles;
    collectibles.populate_map(mapEngine);

    std::vector<Enemy> enemies;
    std::vector<Point> p1;
    p1.push_back(Point(origin_x + 160.0f, origin_y + 495.0f));
    p1.push_back(Point(origin_x + 610.0f, origin_y + 495.0f));
    enemies.push_back(Enemy(p1, false, 2.0f));

    std::vector<Point> p2;
    p2.push_back(Point(origin_x + 220.0f, origin_y + 275.0f));
    p2.push_back(Point(origin_x + 550.0f, origin_y + 275.0f));
    enemies.push_back(Enemy(p2, true, 1.8f));

    SecurityCamera camera(origin_x + mapEngine.room_w - 18.0f, origin_y + 18.0f, 2.45f, 0.65f, 0.022f);

    int score = 0;
    bool showHitbox = false;
    bool running = true;
    int activePage = 0;

    while (running) {
        // ----------------------------------------------------
        // INPUT PROCESSING
        // ----------------------------------------------------
        if (GetAsyncKeyState(VK_ESCAPE) & 0x8000) {
            running = false;
        }

        if (kbhit()) {
            char key = getch();
            if (key == 'h' || key == 'H') {
                showHitbox = !showHitbox;
            } else if (key == 'r' || key == 'R') {
                score = 0;
                mapEngine = MapEngine(origin_x, origin_y);
                player = Player(origin_x + 55.0f, origin_y + 55.0f, 4.5f);
                collectibles = CollectibleManager();
                collectibles.populate_map(mapEngine);
                enemies.clear();
                enemies.push_back(Enemy(p1, false, 2.0f));
                enemies.push_back(Enemy(p2, true, 1.8f));
                camera = SecurityCamera(origin_x + mapEngine.room_w - 18.0f, origin_y + 18.0f, 2.45f, 0.65f, 0.022f);
            } else if (key == 'q' || key == 'Q' || key == 27) {
                running = false;
            }
        }

        // Check camera detection & update logic
        camera.update(player);
        for (size_t i = 0; i < enemies.size(); i++) {
            enemies[i].update(player);
        }

        // ----------------------------------------------------
        // DOUBLE BUFFERING: RENDER TO OFF-SCREEN BUFFER
        // ----------------------------------------------------
        setactivepage(activePage);

        // Clear background
        setfillstyle(SOLID_FILL, BLACK);
        bar(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT);

        // ----------------------------------------------------
        // HEADER HUD BANNER
        // ----------------------------------------------------
        setfillstyle(SOLID_FILL, COLOR(17, 17, 17));
        bar(0, 0, WINDOW_WIDTH, 52);

        // Header border
        drawBresenhamLine(0, 52, WINDOW_WIDTH, 52, COLOR_WIREFRAME_DIM);

        setcolor(COLOR_WIREFRAME_WHITE);
        setbkcolor(COLOR(17, 17, 17));
        outtextxy(16, 18, (char*)"SHADOW HUNT");

        char hpStr[32];
        sprintf(hpStr, "HP: %d%%", (int)player.health);
        setcolor(COLOR_WIREFRAME_LIGHT);
        outtextxy(180, 18, hpStr);

        char scoreStr[32];
        sprintf(scoreStr, "SCORE: %d", score);
        setcolor(COLOR_WIREFRAME_WHITE);
        outtextxy(280, 18, scoreStr);

        char targetsStr[32];
        sprintf(targetsStr, "Targets: %d/2", (int)enemies.size());
        setcolor(COLOR_WIREFRAME_MED);
        outtextxy(400, 18, targetsStr);

        char itemsStr[64];
        sprintf(itemsStr, "Coins: %d | MedKits: %d", (int)collectibles.coins.size(), (int)collectibles.health_kits.size());
        setcolor(COLOR_WIREFRAME_DARK);
        outtextxy(530, 18, itemsStr);

        setcolor(COLOR_WIREFRAME_LIGHT);
        outtextxy(780, 18, (char*)"Status: STATIC (P2)");

        // ----------------------------------------------------
        // DRAW CLEAN MAP ENVIRONMENT (NO INTERMEDIATE GRIDS)
        // ----------------------------------------------------
        mapEngine.render(camera.is_alarm_triggered);

        // ----------------------------------------------------
        // DRAW COLLECTIBLES
        // ----------------------------------------------------
        collectibles.render();

        // ----------------------------------------------------
        // DRAW SECURITY CAMERA WITH VISION CONE
        // ----------------------------------------------------
        camera.render(camera.is_alarm_triggered);

        // ----------------------------------------------------
        // DRAW PATROL GUARDS & SHIELDED ENFORCERS
        // ----------------------------------------------------
        for (size_t i = 0; i < enemies.size(); i++) {
            enemies[i].render(showHitbox);
        }

        // ----------------------------------------------------
        // DRAW PLAYER OPERATIVE
        // ----------------------------------------------------
        player.render(showHitbox);

        // ----------------------------------------------------
        // FOOTER CONTROLS BANNER
        // ----------------------------------------------------
        setcolor(COLOR_WIREFRAME_DIM);
        setbkcolor(BLACK);
        outtextxy(16, WINDOW_HEIGHT - 24,
            (char*)"Controls: [H] Toggle Midpoint Hitbox | [R] Restart | [ESC/Q] Quit | Clean Map (Grids Removed)");

        // Flip pages (zero flicker!)
        setvisualpage(activePage);
        activePage = 1 - activePage;

        Sleep(16);
    }

    closegraph();
    std::cout << "Phase 2 exited cleanly." << std::endl;
    return 0;
}
