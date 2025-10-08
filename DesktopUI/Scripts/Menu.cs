using Godot;
using System;

public partial class Menu : Control
{
    public bool following = false;
    public bool MouseMoving = false;
    private Vector2I DragStartPos = new Vector2I();

    public override void _Ready()
    {
        GetWindow().SetSize(new Vector2I(GetWindow().Size.X * 2, GetWindow().Size.Y * 2));
    }

    public override void _Process(double delta)
    {
        MouseMoving = false;
        if (following)
        {
            Vector2I mousePos = (Vector2I)GetGlobalMousePosition();
            GetWindow().SetPosition(GetWindow().Position + mousePos - DragStartPos);
        }
    }

    private void OnGuiInput(InputEvent @event)
    {
        if (@event is InputEventMouseButton)
        {
            InputEventMouseButton mouse = (InputEventMouseButton)@event;
            if (mouse.GetButtonIndex() == MouseButton.Left)
            {
                following = !following;
                DragStartPos = (Vector2I)GetLocalMousePosition();
            }
        }

        if (@event is InputEventMouseMotion)
        {
            MouseMoving = true;
        }
    }
}
