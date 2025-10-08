using Godot;
using System;

public partial class InterfaceManager : CanvasLayer
{
    [Export] public Menu Menu;
    
    public static InterfaceManager instance;

    public override void _Ready()
    {
        instance = this;
    }
}
