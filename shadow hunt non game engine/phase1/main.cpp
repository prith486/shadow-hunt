#include <graphics.h>
#include <iostream>
#include <cstdio>
#include <windows.h>
#include "game_map.h"

const int SCREEN_WIDTH = 900;
const int SCREEN_HEIGHT = 600;

int main() {

    initwindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Hunter Assassin - Maze Map (Phase 1 C++)");

    std::cout << "============================================================" << std::endl;
    std::cout << "      HUNTER ASSASSIN - PHASE 1 (C++ CORE ALGORITHMS)       " << std::endl;
    std::cout << "============================================================" << std::endl;
    std::cout << " Algorithms Applied:" << std::endl;
    std::cout << "   - DDA Line Algorithm (assign1.cpp port)" << std::endl;
    std::cout << "   - Bresenham Line Algorithm (assign1b.cpp port, all octants)" << std::endl;
    std::cout << " World Dimensions:  " << MAP_WIDTH << " x " << MAP_HEIGHT << " px" << std::endl;
    std::cout << " Viewport Window:   " << SCREEN_WIDTH << " x " << SCREEN_HEIGHT << " px" << std::endl;
    std::cout << " Controls:" << std::endl;
    std::cout << "   - WASD / Arrow Keys : Pan camera across maze" << std::endl;
    std::cout << "   - [G]               : Toggle debug grid" << std::endl;
    std::cout << "   - [R]               : Reset camera to top-left (0, 0)" << std::endl;
    std::cout << "   - [ESC] / [Q]       : Exit game" << std::endl;
    std::cout << "============================================================" << std::endl;

    GameMap gameMap(SCREEN_WIDTH, SCREEN_HEIGHT);

    int camera_x = 0;
    int camera_y = 0;
    const int CAM_SPEED = 12;

    bool showGrid = false;
    bool running = true;
    int activePage = 0;

    while (running) {

        if ((GetAsyncKeyState(VK_ESCAPE) & 0x8000)) {
            running = false;
        }

        if ((GetAsyncKeyState('W') & 0x8000) || (GetAsyncKeyState(VK_UP) & 0x8000)) {
            camera_y -= CAM_SPEED;
        }
        if ((GetAsyncKeyState('S') & 0x8000) || (GetAsyncKeyState(VK_DOWN) & 0x8000)) {
            camera_y += CAM_SPEED;
        }
        if ((GetAsyncKeyState('A') & 0x8000) || (GetAsyncKeyState(VK_LEFT) & 0x8000)) {
            camera_x -= CAM_SPEED;
        }
        if ((GetAsyncKeyState('D') & 0x8000) || (GetAsyncKeyState(VK_RIGHT) & 0x8000)) {
            camera_x += CAM_SPEED;
        }
        if (GetAsyncKeyState('R') & 0x8000) {
            camera_x = 0;
            camera_y = 0;
        }

        if (kbhit()) {
            char ch = getch();
            if (ch == 'g' || ch == 'G') {
                showGrid = !showGrid;
            } else if (ch == 'q' || ch == 'Q' || ch == 27) {
                running = false;
            } else if (ch == 'r' || ch == 'R') {
                camera_x = 0;
                camera_y = 0;
            }
        }

        if (camera_x < 0) camera_x = 0;
        if (camera_y < 0) camera_y = 0;
        if (camera_x > MAP_WIDTH - SCREEN_WIDTH) camera_x = MAP_WIDTH - SCREEN_WIDTH;
        if (camera_y > MAP_HEIGHT - SCREEN_HEIGHT) camera_y = MAP_HEIGHT - SCREEN_HEIGHT;

        setactivepage(activePage);

        setfillstyle(SOLID_FILL, COLOR(30, 30, 30));
        bar(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

        gameMap.draw(camera_x, camera_y, showGrid);

        setcolor(COLOR_WIREFRAME);
        setbkcolor(COLOR(30, 30, 30));
        outtextxy(12, 10, (char*)"SHADOW HUNT / HUNTER ASSASSIN - PHASE 1 (C++)");

        char hudStr[128];
        sprintf(hudStr, "Cam: (%d, %d) | WASD: Pan | [G] Grid: %s | [R] Reset | [ESC] Quit",
                camera_x, camera_y, showGrid ? "ON" : "OFF");
        outtextxy(12, 28, hudStr);

        setvisualpage(activePage);
        activePage = 1 - activePage;

        Sleep(16);
    }

    closegraph();
    std::cout << "Exited cleanly." << std::endl;
    return 0;
}

