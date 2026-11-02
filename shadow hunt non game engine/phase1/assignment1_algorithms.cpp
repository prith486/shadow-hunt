#include <graphics.h>
#include <iostream>
#include <cmath>

using namespace std;

void bresenhamLine(int x1, int y1, int x2, int y2)
{
    int dx = abs(x2 - x1);
    int dy = abs(y2 - y1);

    int P = 2 * dy - dx;

    int X, Y, Xend;

    if (x1 > x2)
    {
        X = x2;
        Y = y2;
        Xend = x1;
    }
    else
    {
        X = x1;
        Y = y1;
        Xend = x2;
    }

    putpixel(X, Y, WHITE);

    while (X < Xend)
    {
        if (P < 0)
        {
            X++;
            P = P + 2 * dy;
        }
        else
        {
            X++;
            Y++;
            P = P + 2 * dy - 2 * dx;
        }

        putpixel(X, Y, WHITE);
    }
}

int main()
{
    int x1, y1, x2, y2;

    cout << "Enter first coordinates: ";
    cin >> x1 >> y1;

    cout << "Enter second coordinates: ";
    cin >> x2 >> y2;

    int gd = DETECT, gm;
    initgraph(&gd, &gm, NULL);

    bresenhamLine(x1, y1, x2, y2);

    getch();
    closegraph();

    return 0;
}

