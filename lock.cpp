#include <windows.h>

HHOOK keyboardHook;

LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam)
{
    if (nCode >= 0 && (wParam == WM_KEYDOWN || wParam == WM_SYSKEYDOWN))
    {
        KBDLLHOOKSTRUCT *kbd = (KBDLLHOOKSTRUCT *)lParam;

        bool alt   = GetAsyncKeyState(VK_MENU) & 0x8000;
        bool ctrl  = GetAsyncKeyState(VK_CONTROL) & 0x8000;
        bool shift = GetAsyncKeyState(VK_SHIFT) & 0x8000;

        if (
            (kbd->vkCode == VK_TAB && alt) ||        // Alt+Tab
            (kbd->vkCode == VK_ESCAPE && alt) ||     // Alt+Esc
            (kbd->vkCode == VK_ESCAPE && ctrl) ||    // Ctrl+Esc
            (kbd->vkCode == VK_ESCAPE && ctrl && shift) || // Ctrl+Shift+Esc
            (kbd->vkCode == VK_F4 && alt) ||         // Alt+F4
            (kbd->vkCode == VK_LWIN) ||              // Win trái
            (kbd->vkCode == VK_RWIN)                 // Win phải
        )
        {
            return 1;
        }
    }
    return CallNextHookEx(keyboardHook, nCode, wParam, lParam);
}

int main()
{
    keyboardHook = SetWindowsHookEx(WH_KEYBOARD_LL, KeyboardProc, GetModuleHandle(NULL), 0);

    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    UnhookWindowsHookEx(keyboardHook);
    return 0;
}