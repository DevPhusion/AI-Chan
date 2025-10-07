using Godot;
using System;
using System.Runtime.InteropServices;

public partial class World : Node3D
{
    const int GWL_EXSTYLE = -20;
    const int WS_EX_LAYERED = 0x00080000;
    const int WS_EX_TRANSPARENT = 0x00000020;
    const int WS_EX_TOPMOST = 0x00000008;

    const uint LWA_ALPHA = 0x02;
    const uint LWA_COLORKEY = 0x01;

    [DllImport("user32.dll", SetLastError = true)]
    static extern IntPtr GetActiveWindow();

    [DllImport("user32.dll", SetLastError = true)]
    static extern int GetWindowLong(IntPtr hWnd, int nIndex);

    [DllImport("user32.dll", SetLastError = true)]
    static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);

    [DllImport("user32.dll", SetLastError = true)]
    static extern bool SetLayeredWindowAttributes(IntPtr hwnd, uint crKey, byte bAlpha, uint dwFlags);

    [DllImport("user32.dll", SetLastError = true)]
    static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

    static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);

    [DllImport("user32.dll", SetLastError = true)]
    static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    const int SW_SHOW = 5;

    [Export] public byte opacity = 255; // 255 = fully opaque, 0 = invisible
    [Export] public bool clickThrough = false;
    [Export] public bool alwaysOnTop = true;

    void Start()
    {
        IntPtr hwnd = GetActiveWindow();
        if (hwnd == IntPtr.Zero)
        {
            GD.PrintErr("Could not find window handle.");
            return;
        }

        // Get the current extended window style
        int extendedStyle = GetWindowLong(hwnd, GWL_EXSTYLE);

        // Add layered style for transparency
        extendedStyle |= WS_EX_LAYERED;

        // Optional: make it click-through
        if (clickThrough)
            extendedStyle |= WS_EX_TRANSPARENT;

        // Optional: keep it on top
        if (alwaysOnTop)
            extendedStyle |= WS_EX_TOPMOST;

        SetWindowLong(hwnd, GWL_EXSTYLE, extendedStyle);

        // Apply the transparency (alpha blending)
        SetLayeredWindowAttributes(hwnd, 0, opacity, LWA_ALPHA);

        // Show window if hidden
        ShowWindow(hwnd, SW_SHOW);
    }
}
