using Godot;
using System;
using System.Runtime.InteropServices;

public partial class World : Node3D
{
    [DllImport("user32.dll")]
    private static extern int SetWindowLong(IntPtr hWnd, int nIndex, uint dwNewLong);
    
    [DllImport("user32.dll")]
    private static extern IntPtr GetActiveWindow();
    
    [DllImport("user32.dll")]
    private static extern int SetLayeredWindowAttributes(IntPtr hwnd, uint crKey, byte bAlpha, uint dwFlags); 
    
    private const int GWL_EXSTYLE = -20;
    private const uint  WS_EX_LAYERED = 0x00080000;
    private const uint LWA_COLORKEY = 0x00000001;
    
    public override void _Ready()
    {
        IntPtr activeWindow = GetActiveWindow();
        
        SetWindowLong(activeWindow, GWL_EXSTYLE, WS_EX_LAYERED);
        SetLayeredWindowAttributes(activeWindow, 0, 0, LWA_COLORKEY);
    }
}